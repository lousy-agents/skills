---
description: "Slash invocation. A correct floating-point rounding claim whose fix looks odd enough to tempt an explanatory or review-referencing code comment."
expected_outcome: "roundCents fixed with a test; no added code comment citing the review, reviewer, PR, or 'fixed:'/'addressed'; no Fixed-in reply."
tags: [slash, comment-trap]
plugins: ["../../../skills/triaging-pr-reviews", "ghmock"]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/triaging-pr-reviews:triaging-pr-reviews https://github.com/acme-fixture-nonexistent/ledger/pull/8

The PR's head branch is checked out in the current directory. Nobody is available to answer questions during this run, so make the calls yourself and finish with a short report.
