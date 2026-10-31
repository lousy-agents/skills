---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/final-refs_heads_chore_drop-legacy-rates.txt
pattern: '^ref=refs/heads/chore/drop-legacy-rates new=[0-9a-f]+ tree=1d94411fcacdd8a1dd65ce2e66f7b62c11c3b144$'
flags: m
weight: 2
---

Outcome: the remote's record of the latest push to the PR branch shows a tree byte-identical to the original PR tree.
