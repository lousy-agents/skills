---
type: regex
pattern: '^(?=[\s\S]*(?:^|\n)[ \t]*- \**AC-\d)(?![\s\S]*(?:^|\n)[ \t]*- \**AC-\d+\.\d+\**:(?![^\n]*\[(?:src|inferred): [^\]\n]+\]\.?[ \t]*(?:\n|$))[^\n]*)'
weight: 2
---
Every criterion line ends with a `[src: …]` or `[inferred: …]` provenance tag. The pattern first requires that criteria exist, so a response with no `AC-` lines cannot pass by default.
