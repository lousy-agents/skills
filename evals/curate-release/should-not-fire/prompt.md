---
description: "Routing. The user wants one commit message for a staged change, which the skill's description excludes."
expected_outcome: "The skill does not fire; the agent proposes a Conventional Commit message and does not commit or push."
tags: [trigger, negative]
plugins: ["../../../skills/curate-release", "ghmock"]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

I've staged a change to `src/money.js`. Can you write a Conventional Commit message for it? Just give me the message here; don't commit anything.
