---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/refs/heads/perf/invoice-totals
pattern: '634c6cb8a99dc18973c65f0b796de0d1e6b6a0cb'
match: not_contains
---

Outcome: the remote PR branch no longer points at the original messy head.
