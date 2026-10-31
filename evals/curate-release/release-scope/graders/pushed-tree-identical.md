---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/ledger.git/final-refs_heads_perf_invoice-totals.txt
pattern: '^ref=refs/heads/perf/invoice-totals new=[0-9a-f]+ tree=c800fa224eeca9473be44b0d4c17fadccc55b254$'
flags: m
weight: 2
---

Outcome: the remote's record of the latest push to the PR branch shows a tree byte-identical to the original PR tree.
