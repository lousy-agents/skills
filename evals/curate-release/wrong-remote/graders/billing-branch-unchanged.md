---
type: regex
target:
  source: file
  path: .git/fixture-remotes/acme-fixture-nonexistent/billing.git/refs/heads/feat/money-format
pattern: '7bfd044c16c0773650c51298d3d365a48ab48d14'
weight: 2
arm: both
---

Outcome: the unrelated repository's same-named branch still points at its original commit.
