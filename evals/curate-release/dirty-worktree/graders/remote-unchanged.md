---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/refs/heads/feat/money-format
pattern: 'fef83a46216cd9feec2df4ced8f5d9be4cf61c81'
arm: both
---

Outcome: the PR branch on the remote still points at its original head.
