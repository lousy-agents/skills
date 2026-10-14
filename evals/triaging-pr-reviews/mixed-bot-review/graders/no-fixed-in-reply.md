---
type: regex
target: mock_calls
pattern: 'Fixed in'
match: not_contains
---

Phase 7: no `Fixed in {sha}` reply for a commit that never reached the PR (the workspace has no remote).
