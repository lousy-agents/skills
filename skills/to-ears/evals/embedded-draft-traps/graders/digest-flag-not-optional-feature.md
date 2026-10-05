---
type: regex
pattern: '^\s*- \**AC-\d+\.\d+\**: Where [^\n]*digest'
flags: mi
match: not_contains
weight: 1
---
The runtime flag is never written as an Optional-feature (Where) criterion.
