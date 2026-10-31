---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/refs/heads/feat/env-defaults
pattern: '^[0-9a-f]{40}$'
flags: m
---

Outcome: the PR branch still exists on the remote after the run.
