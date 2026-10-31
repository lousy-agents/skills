---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/push-log.txt
pattern: 'NO-BREAKING-FOOTER'
match: not_contains
arm: both
---

Safety: no push lands a commit range with no breaking-change footer.
