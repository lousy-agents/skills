---
description: "Routing. The user asks for a new review of a PR, which the skill's 'Do NOT use' list excludes."
expected_outcome: "The skill does not fire; the agent reviews the diff itself; nothing is posted to the PR."
tags: [trigger, negative]
plugins: ["../../../skills/triaging-pr-reviews", "ghmock"]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

Can you write a review of https://github.com/acme-fixture-nonexistent/stockroom/pull/42? Read what it changes and give me your review here in chat: what you'd flag and why. Don't post anything to GitHub. Nobody is around to answer questions, so just give me your best review.
