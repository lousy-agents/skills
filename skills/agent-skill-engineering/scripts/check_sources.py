#!/usr/bin/env python3
"""Verify bundled grounding bytes without extraction or external dependencies."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile


SHA256 = re.compile(r"[0-9a-f]{64}")


def load_entries(manifest):
    version = manifest.get("schema_version")
    if type(version) is not int or version != 1:
        raise ValueError("unsupported manifest schema_version; expected 1")
    entries = manifest["files"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest lists no source files")
    expected = {}
    for entry in entries:
        path, size, digest = entry["path"], entry["bytes"], entry["sha256"]
        if (not isinstance(path, str) or type(size) is not int or size < 0
                or not isinstance(digest, str) or not SHA256.fullmatch(digest)
                or not isinstance(entry.get("bundled", True), bool)):
            raise ValueError(f"malformed manifest entry: {path!r}")
        if path in expected:
            raise ValueError("duplicate source paths in manifest")
        expected[path] = entry
    referenced = list(manifest["source_ids"].values())
    documentation = manifest.get("documentation", {})
    license_path = documentation.get("license_archive_path")
    if documentation.get("license") and license_path is None:
        raise ValueError("declared documentation license has no license_archive_path")
    if license_path is not None:
        referenced.append(license_path)
        if not expected.get(license_path, {}).get("bundled", True):
            raise ValueError(f"license must be bundled: {license_path}")
    unlisted = sorted(set(referenced) - expected.keys())
    if unlisted:
        raise ValueError(f"cited sources missing from files list: {', '.join(unlisted)}")
    return expected


def verify(skill_root):
    manifest = json.loads((skill_root / "provenance/sources.json").read_text())
    expected = load_entries(manifest)
    bundled = {path for path, entry in expected.items() if entry.get("bundled", True)}
    archive = skill_root / manifest["archive"]["path"]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest["archive"]["sha256"]:
        raise ValueError("archive SHA-256 mismatch; restore or review the source snapshot")
    seen = set()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or ".." in path.parts or not member.isfile()
                    or member.name not in bundled or member.name in seen):
                raise ValueError(f"unexpected, unsafe, or duplicate archive member: {member.name}")
            entry = expected[member.name]
            if member.size != entry["bytes"]:
                raise ValueError(f"size mismatch: {member.name}")
            with bundle.extractfile(member) as stream:
                digest = hashlib.sha256(stream.read()).hexdigest()
            if digest != entry["sha256"]:
                raise ValueError(f"source SHA-256 mismatch: {member.name}")
            seen.add(member.name)
    missing = bundled - seen
    if missing:
        raise ValueError(f"missing source files: {', '.join(sorted(missing))}")
    return {"verified": True, "source_files": len(seen),
            "unbundled": sorted(expected.keys() - bundled)}


def identify(skill_root, candidate):
    manifest = json.loads((skill_root / "provenance/sources.json").read_text())
    expected = load_entries(manifest)
    digest = hashlib.sha256(Path(candidate).read_bytes()).hexdigest()
    for path, entry in expected.items():
        if not entry.get("bundled", True) and entry["sha256"] == digest:
            return {"verified": True, "matches": path}
    raise ValueError(f"{candidate} does not match any unbundled source hash")


def main():
    parser = argparse.ArgumentParser(
        description="Check archive and every bundled source hash; does not extract or use the network.",
        epilog="Exit codes: 0 verified; 1 missing, malformed, corrupt, or mismatched source data; 2 usage error.",
    )
    parser.add_argument("--external", metavar="PATH",
                        help="instead, check a separately obtained copy of an unbundled source")
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    try:
        result = identify(skill_root, args.external) if args.external is not None else verify(skill_root)
    except (OSError, EOFError, ValueError, KeyError, TypeError, AttributeError,
            RecursionError, tarfile.TarError) as error:
        print(f"Source verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
