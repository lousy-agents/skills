---
type: llm
weight: 2
---
PASS only if both hold:
1. AC-1.1's boundary is tested: a request beyond 100 in the window (for example, the 101st) is checked for rejection. It may be labeled draft if the response notes that the wording leaves the first rejected request open.
2. AC-1.3's positive case is tested with the gateway in lockdown mode and a non-allowlisted client expecting HTTP 503, with the lockdown state set or confirmed through an interface (for example, /internal/limiter/state).

FAIL if either is missing.
