---
description: "Natural-language request, no slash command. A feature PR into maintenance branch 1.x (latest 1.3.1) while main is at 2.0.0, so 1.x accepts minor releases."
expected_outcome: "Skill fires; commit typed feat; pushed with a lease; PR comment forecasts a minor release (1.4.0) on the 1.x channel without warning that the feat conflicts with the maintenance branch."
tags: [trigger, maintenance, full-run]
plugins: ["../../../skills/curate-release", "ghmock"]
max_turns: 120
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

PR https://github.com/acme-fixture-nonexistent/ledger/pull/17 is about to merge into `1.x`, and its commits are a mess ("wip csv", "docs", "address review"). We publish with semantic-release and keep individual commits at merge, so can you reshape the branch's commits so the release notes read properly? Repository merge settings, read by the routine before this session started: allow_merge_commit=true, allow_rebase_merge=true, allow_squash_merge=false. I'm away for the rest of the day, so nobody can answer questions; use your judgment and tell me what you did.
