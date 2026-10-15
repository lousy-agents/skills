---
type: tool_used
tool: Edit
input_match: '(?://|/\*)(?:(?!\\n)[^"])*?(?:[Pp]er [Rr]eview|[Ff]ixed:|[Aa]ddressed|[Rr]eview|[Cc]opilot|\bPR\s*#?\d)'
min: 0
max: 0
---

No Edit adds a code comment that cites the review, the reviewer, Copilot, the PR, or says fixed:/addressed.
