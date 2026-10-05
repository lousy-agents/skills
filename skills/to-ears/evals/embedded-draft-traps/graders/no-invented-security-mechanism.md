---
type: regex
pattern: '^\s*- \**AC-[^\n]*\b(?:TLS|SSL|AES|HTTPS|encrypt\w*|HMAC|OAuth)\b'
flags: mi
match: not_contains
weight: 1
---
"Notifications must be secure" is not turned into an invented mechanism inside a criterion.
