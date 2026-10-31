---
description: "Natural-language request. A feature PR into maintenance branch 1.x, which was cut from main at main's latest release v1.4.2; main has released nothing since, so 1.x accepts no release at all."
expected_outcome: "Skill fires; commit typed feat; pushed with a lease; the comment warns that 1.x cannot publish any version yet (min = max = 1.4.2) instead of forecasting 1.5.0."
tags: [trigger, maintenance, full-run]
plugins: ["../../../skills/curate-release", "ghmock"]
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

PR https://github.com/acme-fixture-nonexistent/ledger/pull/36 targets `1.x` and its commits are a mess. We publish with semantic-release and keep individual commits at merge, so please curate the branch's commits so the release notes read properly. Repository merge settings, read by the routine before this session started: allow_merge_commit=true, allow_rebase_merge=true, allow_squash_merge=false. I'm away; nobody can answer questions, so use your judgment and tell me what you did.
