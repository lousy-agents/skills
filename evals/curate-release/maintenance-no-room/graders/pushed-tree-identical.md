---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/final-refs_heads_feat_csv-export-1x.txt
pattern: '^ref=refs/heads/feat/csv-export-1x new=[0-9a-f]+ tree=9b2bec129ab7269e7784f2af27707c0602226274$'
flags: m
weight: 2
---

Outcome: the remote's record of the latest push to the PR branch shows a tree byte-identical to the original PR tree.
