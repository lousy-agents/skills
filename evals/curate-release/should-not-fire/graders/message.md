---
type: llm
---

The staged change makes `roundCents` round negative amounts away from zero.

PASS if the response proposes a Conventional Commit message whose header has a type such as `fix` (optionally with a scope), describing the rounding change. FAIL otherwise.
