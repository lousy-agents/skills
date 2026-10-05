---
type: regex
pattern: '^\s*- \**AC-\d+\.\d+\**: If [^\n]{0,60}\b(?:click|select|press)\w* [^\n]{0,20}Mute'
flags: mi
match: not_contains
weight: 1
---
"If the user clicks Mute" is a wanted event, so it is not written as Unwanted behavior (If … then).
