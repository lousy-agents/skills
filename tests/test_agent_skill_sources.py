"""Behavioral checks for the grounding checker and archive builder CLIs, and the shipped package."""

import gzip
import hashlib
import io
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zlib


SKILL = Path(__file__).resolve().parents[1] / "skills/agent-skill-engineering"


class SourceIntegrityCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "relocated-skill"
        (self.skill / "scripts").mkdir(parents=True)
        (self.skill / "provenance").mkdir()
        shutil.copy2(SKILL / "scripts/check_sources.py", self.skill / "scripts")
        self.archive = self.skill / "provenance/grounding-sources.tar.gz"
        self.manifest = self.skill / "provenance/sources.json"

    def bundle(self, members, unbundled=()):
        with tarfile.open(self.archive, "w:gz") as archive:
            for name, content in members:
                entry = tarfile.TarInfo(name)
                entry.size = len(content)
                archive.addfile(entry, io.BytesIO(content))
        files = [
            {"path": name, "bytes": len(content),
             "sha256": hashlib.sha256(content).hexdigest()}
            for name, content in members
        ] + [
            {"path": name, "bytes": len(content),
             "sha256": hashlib.sha256(content).hexdigest(), "bundled": False}
            for name, content in unbundled
        ]
        self.write_manifest({
            "schema_version": 1,
            "archive": {
                "path": "provenance/grounding-sources.tar.gz",
                "sha256": hashlib.sha256(self.archive.read_bytes()).hexdigest(),
            },
            "source_ids": {f"S{index}": entry["path"] for index, entry in enumerate(files)},
            "files": files,
        })

    def read_manifest(self):
        return json.loads(self.manifest.read_text())

    def write_manifest(self, manifest):
        self.manifest.write_text(json.dumps(manifest))

    def run_check(self, *args, skill=None):
        skill = skill or self.skill
        return subprocess.run(
            [sys.executable, str(skill / "scripts/check_sources.py"), *args],
            cwd=self.root, capture_output=True, text=True, timeout=10,
        )

    def assert_failure(self, result):
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("Source verification failed:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_relocated_package_verifies_without_extracting_sources(self):
        self.bundle([("docs/reference.md", b"original source\n")])
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout),
                         {"verified": True, "source_files": 1, "unbundled": []})
        self.assertEqual(result.stderr, "")
        self.assertFalse((self.root / "docs").exists())
        self.assertFalse((self.skill / "docs").exists())

    def test_refreshed_hash_does_not_hide_truncated_gzip_diagnostic(self):
        self.bundle([("docs/reference.md", b"source")])
        self.archive.write_bytes(b"\x1f\x8b\x08\x00")
        manifest = json.loads(self.manifest.read_text())
        manifest["archive"]["sha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.manifest.write_text(json.dumps(manifest))
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("Compressed file ended", result.stderr)

    def test_refreshed_archive_hash_alone_does_not_hide_changed_source_bytes(self):
        self.bundle([("docs/reference.md", b"original")])
        original_manifest = json.loads(self.manifest.read_text())
        self.bundle([("docs/reference.md", b"tampered")])
        original_manifest["archive"]["sha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.manifest.write_text(json.dumps(original_manifest))
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("source SHA-256 mismatch", result.stderr)

    def test_unsafe_member_is_rejected_even_if_manifest_lists_it(self):
        self.bundle([("../outside.md", b"must not be extracted")])
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("unsafe", result.stderr)
        self.assertFalse((self.root / "outside.md").exists())

    def test_dropping_a_cited_source_from_the_manifest_fails(self):
        self.bundle([("docs/a.md", b"a"), ("docs/b.md", b"b")])
        manifest = self.read_manifest()
        manifest["files"] = manifest["files"][:1]
        self.bundle([("docs/a.md", b"a")])
        refreshed = self.read_manifest()
        refreshed["source_ids"] = manifest["source_ids"]
        self.write_manifest(refreshed)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("cited sources missing from files list: docs/b.md", result.stderr)

    def test_empty_source_list_is_not_verified(self):
        self.bundle([])
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("lists no source files", result.stderr)

    def test_source_mapping_instead_of_list_is_not_verified(self):
        self.bundle([("docs/a.md", b"a")])
        manifest = self.read_manifest()
        manifest["files"] = {"docs/a.md": manifest["files"][0]}
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("lists no source files", result.stderr)

    def test_boolean_size_is_rejected_as_malformed(self):
        self.bundle([("docs/one.md", b"1")])
        manifest = self.read_manifest()
        manifest["files"][0]["bytes"] = True
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("malformed manifest entry", result.stderr)

    def test_malformed_entry_fields_are_rejected(self):
        cases = {
            "string bundled flag": ("bundled", "false"),
            "negative size": ("bytes", -1),
            "short digest": ("sha256", "ab" * 31),
            "uppercase digest": ("sha256", "AB" * 32),
            "non-string path": ("path", 7),
        }
        for label, (field, value) in cases.items():
            with self.subTest(case=label):
                self.bundle([("docs/one.md", b"1")])
                manifest = self.read_manifest()
                manifest["files"][0][field] = value
                self.write_manifest(manifest)
                result = self.run_check()
                self.assert_failure(result)
                self.assertIn("malformed manifest entry", result.stderr)

    def test_unsupported_schema_version_is_rejected(self):
        for version in (True, 1.0, "1", 2, 0):
            with self.subTest(version=version):
                self.bundle([("docs/one.md", b"1")])
                manifest = self.read_manifest()
                manifest["schema_version"] = version
                self.write_manifest(manifest)
                result = self.run_check()
                self.assert_failure(result)
                self.assertIn("schema_version", result.stderr)

    def test_deeply_nested_manifest_fails_without_traceback(self):
        self.manifest.write_text("[" * 200000)
        self.assert_failure(self.run_check())

    def test_unbundled_source_is_reported_and_may_not_appear_in_archive(self):
        paper = ("research/paper.md", b"not redistributable")
        self.bundle([("docs/a.md", b"a")], unbundled=[paper])
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["unbundled"], ["research/paper.md"])

        manifest = self.read_manifest()
        self.bundle([("docs/a.md", b"a"), paper])
        smuggled = self.read_manifest()
        manifest["archive"] = smuggled["archive"]
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("unexpected, unsafe, or duplicate archive member: research/paper.md", result.stderr)

    def test_external_copy_of_unbundled_source_is_identified_by_hash(self):
        self.bundle([("docs/a.md", b"a")], unbundled=[("research/paper.md", b"paper bytes")])
        copy = self.root / "downloaded.md"
        copy.write_bytes(b"paper bytes")
        result = self.run_check("--external", str(copy))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"verified": True, "matches": "research/paper.md"})

        copy.write_bytes(b"paper bytes, edited")
        result = self.run_check("--external", str(copy))
        self.assert_failure(result)
        self.assertIn("does not match any unbundled source hash", result.stderr)

    def test_empty_external_path_fails_instead_of_running_full_check(self):
        self.bundle([("docs/a.md", b"a")], unbundled=[("research/paper.md", b"paper")])
        self.assert_failure(self.run_check("--external", ""))

    def refresh_archive_hash(self):
        manifest = self.read_manifest()
        manifest["archive"]["sha256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.write_manifest(manifest)

    def test_symlink_member_is_rejected_even_if_manifest_lists_it(self):
        self.bundle([("docs/link.md", b"")])
        with tarfile.open(self.archive, "w:gz") as archive:
            entry = tarfile.TarInfo("docs/link.md")
            entry.type = tarfile.SYMTYPE
            entry.linkname = "/etc/hosts"
            archive.addfile(entry)
        self.refresh_archive_hash()
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("unsafe", result.stderr)

    def test_duplicate_archive_member_is_rejected(self):
        self.bundle([("docs/a.md", b"a"), ("docs/a.md", b"a")])
        manifest = self.read_manifest()
        manifest["files"] = manifest["files"][:1]
        manifest["source_ids"] = {"S0": "docs/a.md"}
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("duplicate archive member: docs/a.md", result.stderr)

    def test_duplicate_manifest_path_is_rejected(self):
        self.bundle([("docs/a.md", b"a")])
        manifest = self.read_manifest()
        manifest["files"].append(dict(manifest["files"][0]))
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("duplicate source paths", result.stderr)

    def test_size_mismatch_is_rejected(self):
        self.bundle([("docs/a.md", b"abc")])
        manifest = self.read_manifest()
        manifest["files"][0]["bytes"] = 4
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("size mismatch: docs/a.md", result.stderr)

    def test_license_must_stay_bundled(self):
        self.bundle([("docs/a.md", b"a")], unbundled=[("docs/LICENSE", b"license")])
        manifest = self.read_manifest()
        manifest["documentation"] = {"license_archive_path": "docs/LICENSE"}
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("license must be bundled: docs/LICENSE", result.stderr)

    def test_external_does_not_match_bundled_sources(self):
        self.bundle([("docs/a.md", b"bundled bytes")], unbundled=[("research/paper.md", b"paper")])
        copy = self.root / "copy.md"
        copy.write_bytes(b"bundled bytes")
        result = self.run_check("--external", str(copy))
        self.assert_failure(result)
        self.assertIn("does not match any unbundled source hash", result.stderr)

    def test_changed_archive_without_refreshed_hash_is_rejected(self):
        self.bundle([("docs/a.md", b"a")])
        manifest = self.read_manifest()
        self.bundle([("docs/a.md", b"a"), ("docs/extra.md", b"x")])
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("archive SHA-256 mismatch", result.stderr)

    def test_bundled_source_missing_from_archive_is_rejected(self):
        self.bundle([("docs/a.md", b"a"), ("docs/b.md", b"b")])
        manifest = self.read_manifest()
        self.bundle([("docs/a.md", b"a")])
        manifest["archive"] = self.read_manifest()["archive"]
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("missing source files: docs/b.md", result.stderr)

    def test_license_path_must_be_listed(self):
        self.bundle([("docs/a.md", b"a")])
        manifest = self.read_manifest()
        manifest["documentation"] = {"license_archive_path": "docs/LICENSE"}
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("cited sources missing from files list: docs/LICENSE", result.stderr)

    def test_absolute_member_is_rejected_even_if_manifest_lists_it(self):
        self.bundle([("/abs.md", b"absolute")])
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("unsafe", result.stderr)

    def test_empty_license_path_is_not_treated_as_absent(self):
        self.bundle([("docs/a.md", b"a")])
        manifest = self.read_manifest()
        manifest["documentation"] = {"license_archive_path": ""}
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("cited sources missing from files list", result.stderr)

    def test_uncompressed_tar_archive_is_rejected(self):
        self.bundle([("docs/a.md", b"a")])
        with tarfile.open(self.archive, "w") as archive:
            entry = tarfile.TarInfo("docs/a.md")
            entry.size = 1
            archive.addfile(entry, io.BytesIO(b"a"))
        self.refresh_archive_hash()
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("not a gzip file", result.stderr)

    def test_overlong_digest_on_unbundled_source_is_rejected(self):
        self.bundle([("docs/a.md", b"a")], unbundled=[("research/paper.md", b"paper")])
        manifest = self.read_manifest()
        manifest["files"][1]["sha256"] = "a" * 65
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("malformed manifest entry", result.stderr)

    def test_external_rejects_manifest_that_full_check_rejects(self):
        self.bundle([("docs/a.md", b"a")], unbundled=[("research/paper.md", b"paper")])
        copy = self.root / "copy.md"
        copy.write_bytes(b"paper")
        manifest = self.read_manifest()
        manifest["schema_version"] = 2
        self.write_manifest(manifest)
        result = self.run_check("--external", str(copy))
        self.assert_failure(result)
        self.assertIn("schema_version", result.stderr)

    def test_non_gzip_archive_fails_without_traceback(self):
        self.bundle([("docs/a.md", b"a")])
        self.archive.write_bytes(b"plain bytes, not gzip")
        self.refresh_archive_hash()
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("not a gzip file", result.stderr)

    def test_structurally_malformed_manifests_fail_without_traceback(self):
        self.bundle([("docs/a.md", b"a")])
        good = self.read_manifest()
        cases = {
            "missing files key": {k: v for k, v in good.items() if k != "files"},
            "list manifest": [],
            "string entry": dict(good, files=["docs/a.md"]),
        }
        for label, manifest in cases.items():
            with self.subTest(case=label):
                self.write_manifest(manifest)
                self.assert_failure(self.run_check())

    def test_shipped_package_verifies_in_place(self):
        result = self.run_check(skill=SKILL)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["verified"])
        self.assertEqual(report["source_files"], 12)
        self.assertEqual(report["unbundled"],
                         ["research/agent-skill-evolution-how-revisions-affect-coding-agents.md"])
        with tarfile.open(SKILL / "provenance/grounding-sources.tar.gz") as archive:
            self.assertFalse([name for name in archive.getnames() if name.startswith("research/")])

    def test_declared_license_without_archive_path_is_rejected(self):
        self.bundle([("docs/a.md", b"a")])
        manifest = self.read_manifest()
        manifest["documentation"] = {"license": "CC-BY-4.0"}
        self.write_manifest(manifest)
        result = self.run_check()
        self.assert_failure(result)
        self.assertIn("no license_archive_path", result.stderr)


class ShippedPackageConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SKILL / "provenance/sources.json").read_text())

    def test_provenance_holds_only_the_manifest_and_archive(self):
        names = sorted(path.name for path in (SKILL / "provenance").iterdir()
                       if path.name != ".DS_Store")
        self.assertEqual(names, ["grounding-sources.tar.gz", "sources.json"])

    def test_notice_names_the_pinned_documentation_commit(self):
        notice = (SKILL / "NOTICE.md").read_text()
        self.assertIn(self.manifest["documentation"]["commit"], notice)
        self.assertIn(self.manifest["documentation"]["license_archive_path"], notice)

    def test_every_cited_source_id_is_in_the_manifest(self):
        texts = [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]
        cited = {token for path in texts
                 for token in re.findall(r"\b(D-[A-Z]+|R[0-9]+)\b", path.read_text())}
        self.assertTrue(cited)
        self.assertEqual(sorted(cited - self.manifest["source_ids"].keys()), [])


class ArchiveBuildCliTests(unittest.TestCase):
    def run_build(self, skill, source, output):
        return subprocess.run(
            [sys.executable, "-I", str(skill / "scripts/build_archive.py"), str(source), str(output)],
            capture_output=True, text=True, check=False)

    def test_archive_rebuilds_from_its_members(self):
        shipped = SKILL / "provenance/grounding-sources.tar.gz"
        manifest = json.loads((SKILL / "provenance/sources.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "src"
            with tarfile.open(shipped) as archive:
                for member in archive.getmembers():
                    target = source / member.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.extractfile(member).read())
            output = Path(temp) / "rebuilt.tar.gz"
            result = self.run_build(SKILL, source, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(gzip.decompress(output.read_bytes()), gzip.decompress(shipped.read_bytes()))
            if "ng" not in zlib.ZLIB_RUNTIME_VERSION:
                self.assertEqual(json.loads(result.stdout)["archive_sha256"], manifest["archive"]["sha256"])
                self.assertEqual(output.read_bytes(), shipped.read_bytes())

    def run_build_with_manifest(self, files, prepare=lambda source: None, output_name="out.tar.gz"):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / "skill"
            (skill / "scripts").mkdir(parents=True)
            (skill / "provenance").mkdir()
            shutil.copy2(SKILL / "scripts/build_archive.py", skill / "scripts")
            listed = files(root) if callable(files) else files
            (skill / "provenance/sources.json").write_text(json.dumps({"files": listed}))
            source = root / "src"
            (source / "docs").mkdir(parents=True)
            (source / "docs/a.md").write_text("a")
            (root / "outside.txt").write_text("host secret")
            prepare(source)
            output = root / output_name
            result = self.run_build(skill, source, output)
            return result, output.exists(), (source / "docs/a.md").read_bytes()

    def assert_refused(self, result, written):
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Archive build failed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(written)

    def test_build_refuses_paths_and_symlinks_that_leave_the_source_tree(self):
        def link_source(source):
            (source / "docs/a.md").unlink()
            (source / "docs/a.md").symlink_to(source.parent / "outside.txt")

        def link_directory(source):
            (source / "linked").symlink_to(source.parent)

        cases = {
            "parent traversal": ([{"path": "../outside.txt"}], lambda source: None),
            "absolute path": (lambda root: [{"path": str(root.resolve() / "outside.txt")}], lambda source: None),
            "symlinked file": ([{"path": "docs/a.md"}], link_source),
            "symlinked directory": ([{"path": "linked/outside.txt"}], link_directory),
        }
        for label, (files, prepare) in cases.items():
            with self.subTest(case=label):
                result, written, _ = self.run_build_with_manifest(files, prepare)
                self.assert_refused(result, written)

    def test_build_refuses_manifests_the_checker_would_reject(self):
        cases = {
            "no bundled files": [{"path": "docs/a.md", "bundled": False}],
            "duplicate path": [{"path": "docs/a.md"}, {"path": "docs/a.md"}],
            "case-only collision": [{"path": "docs/a.md"}, {"path": "docs/A.md"}],
        }
        for label, files in cases.items():
            with self.subTest(case=label):
                result, written, _ = self.run_build_with_manifest(files)
                self.assert_refused(result, written)

    def test_build_refuses_output_inside_the_source_tree(self):
        result, _, source_bytes = self.run_build_with_manifest(
            [{"path": "docs/a.md"}], output_name="src/docs/a.md")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("output must be outside source_dir", result.stderr)
        self.assertEqual(source_bytes, b"a")

    def test_build_writes_listed_regular_file(self):
        result, written, _ = self.run_build_with_manifest([{"path": "docs/a.md"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(written)
        self.assertEqual(json.loads(result.stdout)["files"][0]["bytes"], 1)

    def test_build_reports_missing_source_file(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as out:
            result = self.run_build(SKILL, source, Path(out) / "out.tar.gz")
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing source file", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

if __name__ == "__main__":
    unittest.main()
