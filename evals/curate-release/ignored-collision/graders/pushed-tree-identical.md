---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/final-refs_heads_feat_env-defaults.txt
pattern: '^ref=refs/heads/feat/env-defaults new=[0-9a-f]+ tree=fd3a1f02e02f9ce5c0f3b22f61cb39d5ee075d03$'
flags: m
weight: 2
---

Outcome: the remote's record of the latest push to the PR branch shows a tree byte-identical to the original PR tree.
