---
type: regex
pattern: '^\s*- \**AC-\d+\.\d+\**:(?![^\n]*\[(?:src|inferred): [^\]\n]+\]\.?\s*$)[^\n]*$'
flags: m
match: not_contains
weight: 2
---
No criterion line lacks a trailing `[src: …]` or `[inferred: …]` provenance tag.
