---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/final-refs_heads_refactor_to-cents.txt
pattern: '^BREAKING CHANGE: '
flags: m
weight: 2
---

Outcome: after the latest push, a commit on the PR branch, read on the remote, carries a `BREAKING CHANGE:` footer.
