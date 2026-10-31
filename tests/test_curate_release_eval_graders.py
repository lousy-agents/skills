#!/usr/bin/env python3
"""Negative probes for the curate-release eval graders that read the fixture remote.

The eval suite grades a rewrite by what actually landed on the fixture remote: a
post-receive hook records each push in push-log.txt (cumulative) and final-<ref>.txt
(latest push only). These tests run the real breaking-in-pr scaffold, simulate pushes
against its remote, and apply the case's own file-target regex graders, so a grader
that would pass on stale or partial evidence fails here instead of in a paid eval run.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = REPO_ROOT / "evals" / "curate-release" / "breaking-in-pr"
BRANCH = "refactor/to-cents"
GOOD_MESSAGE = (
    "feat(money)!: rename roundCents to toCents\n\n"
    "BREAKING CHANGE: roundCents is removed; toCents returns integer cents.\n\n"
    "Release-Story: curated\n"
)
FOOTERLESS_MESSAGE = "feat(money): rename roundCents to toCents\n\nRelease-Story: curated\n"


def parse_grader(path: Path) -> dict:
    """Parse the small YAML subset the grader frontmatter uses."""
    front = path.read_text(encoding="utf-8").split("---")[1]
    grader: dict = {}
    nested: dict | None = None
    for line in front.strip().splitlines():
        if line.startswith("  ") and nested is not None:
            key, _, value = line.strip().partition(": ")
            nested[key] = value
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if value:
            grader[key] = value.strip("'")
            nested = None
        else:
            nested = grader[key] = {}
    return grader


def file_graders() -> dict[str, dict]:
    graders = {}
    for path in sorted((CASE_DIR / "graders").glob("*.md")):
        grader = parse_grader(path)
        if grader["type"] == "regex" and isinstance(grader.get("target"), dict):
            graders[path.stem] = grader
    return graders


def passes(grader: dict, workspace: Path) -> bool:
    target = workspace / grader["target"]["path"]
    text = target.read_text(encoding="utf-8") if target.is_file() else ""
    flags = re.M if "m" in grader.get("flags", "") else 0
    found = re.search(grader["pattern"], text, flags) is not None
    return not found if grader.get("match") == "not_contains" else found


class CurateReleaseRemoteGraderTest(unittest.TestCase):
    def setUp(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is not installed")
        self.workspace = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.workspace)
        subprocess.run(["bash", str(CASE_DIR / "scaffold.sh")], cwd=self.workspace, check=True, capture_output=True)
        self.env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Probe",
            "GIT_AUTHOR_EMAIL": "probe@example.invalid",
            "GIT_COMMITTER_NAME": "Probe",
            "GIT_COMMITTER_EMAIL": "probe@example.invalid",
        }
        self.git("checkout", "-q", "--no-track", "-B", BRANCH, f"refs/remotes/origin/{BRANCH}")
        self.original_head = self.git("rev-parse", "HEAD")
        self.base = self.git("merge-base", "refs/remotes/origin/main", "HEAD")
        self.graders = file_graders()

    def git(self, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=self.workspace, env=self.env, check=True, capture_output=True, text=True)
        return result.stdout.strip()

    def push(self, message: str, alter_content: bool = False) -> None:
        """Rewrite the PR branch into one commit and force-push it with a lease."""
        if alter_content:
            money = self.workspace / "src" / "money.js"
            money.write_text(money.read_text(encoding="utf-8") + "// drift\n", encoding="utf-8")
        remote_head = self.git("rev-parse", f"refs/remotes/origin/{BRANCH}")
        self.git("reset", "-q", "--soft", self.base)
        self.git("add", "--force", "--", "src", "test")
        message_file = self.workspace / ".git" / "probe-message"
        message_file.write_text(message, encoding="utf-8")
        self.git("commit", "-q", "-F", str(message_file))
        self.git("push", "-q", f"--force-with-lease=refs/heads/{BRANCH}:{remote_head}", "origin", f"HEAD:refs/heads/{BRANCH}")
        self.git("fetch", "-q", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")

    def delete_branch(self) -> None:
        remote_head = self.git("rev-parse", f"refs/remotes/origin/{BRANCH}")
        self.git("push", "-q", f"--force-with-lease=refs/heads/{BRANCH}:{remote_head}", "origin", f":refs/heads/{BRANCH}")

    def verdicts(self) -> dict[str, bool]:
        return {name: passes(grader, self.workspace) for name, grader in self.graders.items()}

    def test_the_case_has_the_remote_graders_these_probes_rely_on(self) -> None:
        for name in ("pushed-tree-identical", "no-tree-mismatch", "pushed-breaking-footer", "no-footerless-push", "pushed-trailer", "remote-branch-exists"):
            self.assertIn(name, self.graders)

    def test_no_push_fails_every_positive_remote_grader(self) -> None:
        verdicts = self.verdicts()
        self.assertTrue(verdicts["remote-branch-exists"], "the untouched PR branch still exists")
        self.assertFalse(verdicts["pushed-tree-identical"])
        self.assertFalse(verdicts["pushed-breaking-footer"])
        self.assertFalse(verdicts["pushed-trailer"])

    def test_one_good_push_passes_every_remote_grader(self) -> None:
        self.push(GOOD_MESSAGE)
        self.assertEqual(self.verdicts(), {name: True for name in self.graders})

    def test_a_good_push_followed_by_an_altered_tree_fails(self) -> None:
        self.push(GOOD_MESSAGE)
        self.push(GOOD_MESSAGE, alter_content=True)
        verdicts = self.verdicts()
        self.assertFalse(verdicts["pushed-tree-identical"], "a stale good push must not satisfy the final-tree check")
        self.assertFalse(verdicts["no-tree-mismatch"])

    def test_an_altered_tree_later_restored_still_fails(self) -> None:
        self.push(GOOD_MESSAGE, alter_content=True)
        self.git("checkout", "-q", self.original_head, "--", "src")
        self.push(GOOD_MESSAGE)
        verdicts = self.verdicts()
        self.assertTrue(verdicts["pushed-tree-identical"])
        self.assertFalse(verdicts["no-tree-mismatch"], "a bad push anywhere in the run must fail the case")

    def test_a_good_push_followed_by_a_branch_deletion_fails(self) -> None:
        self.push(GOOD_MESSAGE)
        self.delete_branch()
        verdicts = self.verdicts()
        self.assertFalse(verdicts["pushed-tree-identical"], "a deleted branch must not keep a stale final record")
        self.assertFalse(verdicts["pushed-breaking-footer"])
        self.assertFalse(verdicts["pushed-trailer"])
        self.assertFalse(verdicts["no-tree-mismatch"])
        self.assertFalse(verdicts["remote-branch-exists"])

    def test_a_good_push_followed_by_a_footerless_push_fails(self) -> None:
        self.push(GOOD_MESSAGE)
        self.push(FOOTERLESS_MESSAGE)
        verdicts = self.verdicts()
        self.assertFalse(verdicts["pushed-breaking-footer"], "a stale footer must not satisfy the final-state check")
        self.assertFalse(verdicts["no-footerless-push"])


if __name__ == "__main__":
    unittest.main()
