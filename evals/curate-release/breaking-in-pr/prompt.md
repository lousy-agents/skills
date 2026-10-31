---
description: "Slash invocation, full rewrite. The PR renames an exported function and changes its return unit, but its commits say only 'wip' and 'fix tests'."
expected_outcome: "Pushes with a lease; the remote's push record shows an unchanged tree and a BREAKING CHANGE footer in the pushed commits; the comment forecasts a major release."
tags: [slash, breaking-change, full-run]
plugins: ["../../../skills/curate-release", "ghmock"]
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/curate-release:curate-release https://github.com/acme-fixture-nonexistent/ledger/pull/31

Repository merge settings, read by the routine before this session started: allow_merge_commit=true, allow_rebase_merge=true, allow_squash_merge=false. Nobody is available to answer questions during this run, so make the calls yourself and finish with a short report.
