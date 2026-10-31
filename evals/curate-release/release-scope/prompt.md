---
description: "Slash invocation, full rewrite. Since the last release (v1.4.0) main has a queued feat marked by a non-release deploy tag and a fix whose BREAKING CHANGE footer is only in the body. The PR is a consumer-visible speedup."
expected_outcome: "Rewrites and pushes with a lease; one PR comment that names v1.4.0 as the last release, sees the queued breaking change (next release major), says this PR does not change the version, and types the speedup release-bearing."
tags: [slash, release-scope, full-run]
plugins: ["../../../skills/curate-release", "ghmock"]
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/curate-release:curate-release https://github.com/acme-fixture-nonexistent/ledger/pull/21

Repository merge settings, read by the routine before this session started: allow_merge_commit=true, allow_rebase_merge=true, allow_squash_merge=false. Nobody is available to answer questions during this run, so make the calls yourself and finish with a short report.
