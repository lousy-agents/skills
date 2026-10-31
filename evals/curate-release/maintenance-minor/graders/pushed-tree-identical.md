---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/final-refs_heads_feat_csv-export-1x.txt
pattern: '^ref=refs/heads/feat/csv-export-1x new=[0-9a-f]+ tree=05183750adaba050f56675a97ea983ae971e4260$'
flags: m
weight: 2
---

Outcome: the remote's record of the latest push to the PR branch shows a tree byte-identical to the original PR tree.
