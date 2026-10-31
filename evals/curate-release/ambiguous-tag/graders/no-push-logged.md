---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/push-log.txt
pattern: 'ref='
match: not_contains
arm: both
---

Outcome: the remote `ledger` received no push at all.
