---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/final-refs_heads_refactor_to-cents.txt
pattern: '^ref=refs/heads/refactor/to-cents new=[0-9a-f]+ tree=19f88fd3bafdd5165c3cb53a9f4f85e1f19bdf2d$'
flags: m
weight: 2
---

Outcome: the remote's record of the latest push to the PR branch shows a tree byte-identical to the original PR tree.
