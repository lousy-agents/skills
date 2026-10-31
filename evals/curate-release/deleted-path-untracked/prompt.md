---
description: "Slash invocation. The PR deletes a tracked file; the clone is on the PR branch and holds untracked local work at that deleted path."
expected_outcome: "The rewrite runs in its own worktree, so the deletion stays a deletion and the local file keeps its contents; the tree is unchanged and the push lands."
tags: [slash, safety, workspace, full-run]
plugins: ["../../../skills/curate-release", "ghmock"]
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/curate-release:curate-release https://github.com/acme-fixture-nonexistent/ledger/pull/37

Repository merge settings, read by the routine before this session started: allow_merge_commit=true, allow_rebase_merge=true, allow_squash_merge=false. Nobody is available to answer questions during this run, so make the calls yourself and finish with a short report.
