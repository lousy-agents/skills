---
type: regex
pattern: '^\s*- \**AC-[^\n]*\b(?:3|three) (?:times|retries|attempts)\b'
flags: mi
match: not_contains
weight: 2
---
No criterion adopts the current code's 3 retries; code behavior is not intent.
