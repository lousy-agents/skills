#!/usr/bin/env python3
"""Fail-closed tests for curate-release's worktree setup and re-entry blocks.

Phase 1 of skills/curate-release/SKILL.md creates a dedicated worktree and every
later phase re-enters it with a prefix block before resetting or committing. If
either block keeps going after a failed `git worktree add` or `cd`, the shell stays
in the clone's own checkout, and the resets that follow can erase local work there.
These tests extract both blocks verbatim from SKILL.md and run them against a
disposable clone whose checkout already sits at the PR head, which is the case
where a HEAD check alone cannot tell the two trees apart.
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
SKILL = REPO_ROOT / "skills" / "curate-release" / "SKILL.md"
BRANCH = "topic"
OTHER_BRANCH = "other"


def phase1_blocks() -> tuple[str, str]:
    """Return the setup block and the re-entry prefix from 'Establish the git state'."""
    text = SKILL.read_text(encoding="utf-8")
    section = text[text.index("### Establish the git state") :]
    blocks = re.findall(r"```bash\n(.*?)```", section, flags=re.S)
    return blocks[0], blocks[1]


class CurateReleaseWorktreeBlockTest(unittest.TestCase):
    def setUp(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is not installed")
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Probe",
            "GIT_AUTHOR_EMAIL": "probe@example.invalid",
            "GIT_COMMITTER_NAME": "Probe",
            "GIT_COMMITTER_EMAIL": "probe@example.invalid",
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "commit.gpgsign",
            "GIT_CONFIG_VALUE_0": "false",
            "GIT_CONFIG_KEY_1": "push.negotiate",
            "GIT_CONFIG_VALUE_1": "false",
        }
        self.clone = self.root / "clone"
        self.run_git(self.root, "init", "-q", "--bare", "remote.git")
        self.run_git(self.root, "init", "-q", "-b", "main", "clone")
        self.git("remote", "add", "origin", str(self.root / "remote.git"))
        (self.clone / "a.txt").write_text("a\n", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        self.git("push", "-q", "origin", "main")
        self.git("checkout", "-q", "-b", BRANCH)
        (self.clone / "a.txt").write_text("a\nb\n", encoding="utf-8")
        self.git("commit", "-q", "-am", "wip")
        self.git("push", "-q", "origin", BRANCH)
        self.git("checkout", "-q", "-b", OTHER_BRANCH, "main")
        (self.clone / "b.txt").write_text("b\n", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "other wip")
        self.git("push", "-q", "origin", OTHER_BRANCH)
        self.git("checkout", "-q", BRANCH)
        self.git(
            "fetch", "-q", "origin",
            "+refs/heads/main:refs/remotes/origin/main",
            f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}",
            f"+refs/heads/{OTHER_BRANCH}:refs/remotes/origin/{OTHER_BRANCH}",
        )
        # Untracked local work in the clone, which sits at the PR head itself.
        (self.clone / "local-notes.txt").write_text("LOCAL WORK\n", encoding="utf-8")
        self.head_sha = self.git("rev-parse", "HEAD")
        self.other_sha = self.git("rev-parse", f"refs/remotes/origin/{OTHER_BRANCH}")
        self.setup_block, self.prefix_block = self.blocks_for(BRANCH, self.head_sha, 7)

    def blocks_for(self, branch: str, head_sha: str, pr_number: int) -> tuple[str, str]:
        def fill(block: str) -> str:
            return (
                block.replace("<head_ref>", branch)
                .replace("<base_ref>", "main")
                .replace("<head_sha>", head_sha)
                .replace("<owner>", "acme")
                .replace("<repo>", "ledger")
                .replace("<pr_number>", str(pr_number))
            )

        setup, prefix = phase1_blocks()
        return fill(setup), fill(prefix)

    def setup(self, block: str) -> Path:
        result = self.bash(block)
        self.assertEqual(result.returncode, 0, result.stderr)
        return Path(re.search(r"^RUN=(.+)$", result.stdout, flags=re.M).group(1))

    @staticmethod
    def enter(prefix: str, run: Path) -> str:
        return prefix.replace("<run_dir>", str(run))

    def run_git(self, cwd: Path, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=cwd, env=self.env, check=True, capture_output=True, text=True).stdout.strip()

    def git(self, *args: str) -> str:
        return self.run_git(self.clone, *args)

    def bash(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", "-c", script], cwd=self.clone, env=self.env, capture_output=True, text=True)

    def assert_clone_untouched(self) -> None:
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head_sha)
        self.assertEqual(self.git("branch", "--show-current"), BRANCH)
        self.assertEqual((self.clone / "local-notes.txt").read_text(encoding="utf-8"), "LOCAL WORK\n")

    def test_setup_then_prefix_lands_in_a_linked_worktree(self) -> None:
        run = self.setup(self.setup_block)
        entered = self.bash(self.enter(self.prefix_block, run) + '\ngit rev-parse --show-toplevel\necho "$BASE $ORIG"')
        self.assertEqual(entered.returncode, 0, entered.stderr)
        toplevel, pins = entered.stdout.strip().splitlines()[-2:]
        self.assertNotEqual(Path(toplevel).resolve(), self.clone.resolve())
        self.assertTrue(toplevel.endswith("/worktree"), toplevel)
        self.assertEqual(pins.split()[1], self.head_sha)
        self.assert_clone_untouched()

    def test_failed_worktree_add_stops_before_pinning_while_clone_is_at_head(self) -> None:
        self.git("update-ref", "-d", f"refs/remotes/origin/{BRANCH}")
        setup = self.bash(self.setup_block + "\necho REACHED-THE-END")
        self.assertNotEqual(setup.returncode, 0)
        self.assertNotIn("REACHED-THE-END", setup.stdout)
        common = Path(self.git("rev-parse", "--path-format=absolute", "--git-common-dir"))
        self.assertEqual(list((common / "curate-release").glob("run.*/base")), [])
        self.assertNotIn("RUN=", setup.stdout)
        self.assert_clone_untouched()

    def test_a_locked_leftover_worktree_does_not_collide(self) -> None:
        leftover = Path(self.git("rev-parse", "--path-format=absolute", "--git-common-dir")) / "curate-release" / "worktree"
        leftover.parent.mkdir(parents=True)
        self.git("worktree", "add", "-q", "--detach", str(leftover), "HEAD")
        self.git("worktree", "lock", str(leftover))
        shutil.rmtree(leftover)
        self.setup(self.setup_block)
        self.assert_clone_untouched()

    def test_prefix_refuses_a_stale_run_and_never_resets_the_clone(self) -> None:
        run = self.setup(self.setup_block)
        self.run_git(self.clone, "worktree", "remove", "--force", str(run / "worktree"))
        destructive = self.bash(self.enter(self.prefix_block, run) + '\ngit reset -q --hard HEAD~1\necho REACHED-THE-RESET')
        self.assertNotEqual(destructive.returncode, 0)
        self.assertNotIn("REACHED-THE-RESET", destructive.stdout)
        self.assert_clone_untouched()

    def test_prefix_refuses_a_plain_directory_where_the_worktree_should_be(self) -> None:
        run = self.setup(self.setup_block)
        self.run_git(self.clone, "worktree", "remove", "--force", str(run / "worktree"))
        (run / "worktree").mkdir()
        destructive = self.bash(self.enter(self.prefix_block, run) + '\ngit reset -q --hard HEAD~1\necho REACHED-THE-RESET')
        self.assertNotEqual(destructive.returncode, 0)
        self.assertNotIn("REACHED-THE-RESET", destructive.stdout)
        self.assert_clone_untouched()


    def test_interleaved_runs_stay_bound_to_their_own_worktree(self) -> None:
        other_setup, other_prefix = self.blocks_for(OTHER_BRANCH, self.other_sha, 8)
        run_a = self.setup(self.setup_block)
        run_b = self.setup(other_setup)
        self.assertNotEqual(run_a, run_b)
        b_head_before = self.run_git(run_b / "worktree", "rev-parse", "HEAD")
        # Run A resumes after run B's setup, from inside A's own worktree, and resets.
        resumed = subprocess.run(
            ["bash", "-c", self.enter(self.prefix_block, run_a) + '\necho "$ORIG"\ngit reset -q --soft "$BASE"\ngit rev-parse --show-toplevel'],
            cwd=run_a / "worktree", env=self.env, capture_output=True, text=True,
        )
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        orig, toplevel = resumed.stdout.strip().splitlines()[-2:]
        self.assertEqual(orig, self.head_sha, "run A must reload its own ORIG, not run B's")
        self.assertEqual(Path(toplevel).resolve(), (run_a / "worktree").resolve())
        self.assertEqual(self.run_git(run_b / "worktree", "rev-parse", "HEAD"), b_head_before, "run B's worktree must be untouched")
        # Run B's prefix still reaches B.
        b_orig = self.bash(self.enter(other_prefix, run_b) + '\necho "$ORIG"').stdout.strip().splitlines()[-1]
        self.assertEqual(b_orig, self.other_sha)
        self.assert_clone_untouched()

    def test_prefix_refuses_a_run_directory_for_another_target(self) -> None:
        other_setup, _ = self.blocks_for(OTHER_BRANCH, self.other_sha, 8)
        run_b = self.setup(other_setup)
        crossed = self.bash(self.enter(self.prefix_block, run_b) + '\ngit reset -q --hard HEAD~1\necho REACHED-THE-RESET')
        self.assertNotEqual(crossed.returncode, 0)
        self.assertNotIn("REACHED-THE-RESET", crossed.stdout)
        self.assertEqual(self.run_git(run_b / "worktree", "rev-parse", "HEAD"), self.other_sha)

    def test_prefix_refuses_swapped_pins(self) -> None:
        run = self.setup(self.setup_block)
        (run / "orig").write_text(self.other_sha + "\n", encoding="utf-8")
        swapped = self.bash(self.enter(self.prefix_block, run) + '\ngit reset -q --hard "$ORIG"\necho REACHED-THE-RESET')
        self.assertNotEqual(swapped.returncode, 0)
        self.assertNotIn("REACHED-THE-RESET", swapped.stdout)
        self.assertEqual(self.run_git(run / "worktree", "rev-parse", "HEAD"), self.head_sha)


if __name__ == "__main__":
    unittest.main()
