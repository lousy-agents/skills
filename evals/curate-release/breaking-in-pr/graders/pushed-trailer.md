---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/final-refs_heads_refactor_to-cents.txt
pattern: '^Release-Story: curated$'
flags: m
---

Outcome: the commits on the PR branch after the latest push, read on the remote, carry the Release-Story trailer.
