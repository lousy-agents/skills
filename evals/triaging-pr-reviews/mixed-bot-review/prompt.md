---
description: "Slash invocation. One correct Copilot claim, one hallucinated Copilot claim (impossible line, wrong control flow), one already-resolved human thread."
expected_outcome: "Math.floor -> Math.ceil fixed with a test; normalizeSku claim rejected after reading the code; resolved rename thread excluded and counted; no Fixed-in reply because nothing was pushed."
tags: [slash, verdicts, resolved-exclusion, hallucination]
plugins: ["../../../skills/triaging-pr-reviews", "ghmock"]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/triaging-pr-reviews:triaging-pr-reviews https://github.com/acme-fixture-nonexistent/stockroom/pull/17

The PR's head branch is checked out in the current directory. Nobody is available to answer questions during this run, so make the calls yourself and finish with a short report.
