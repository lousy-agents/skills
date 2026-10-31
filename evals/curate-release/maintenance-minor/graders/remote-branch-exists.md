---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/refs/heads/feat/csv-export-1x
pattern: '^[0-9a-f]{40}$'
flags: m
---

Outcome: the PR branch still exists on the remote after the run.
