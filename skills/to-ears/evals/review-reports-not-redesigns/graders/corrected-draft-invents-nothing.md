---
type: llm
weight: 3
---
Look at the corrected draft criteria in the response (lines starting "- AC-"). Splitting a criterion into new IDs (for example AC-1.13, AC-1.14) and adding "[TBD: …]" placeholders are allowed and are not invented values.

PASS only if both hold:
1. No corrected criterion states a new number, threshold, time limit, status code, or mechanism that is absent from the original twelve criteria and Notes (60, 410, and 2024 are from the source). New values must appear only as "[TBD: …]" placeholders or as open questions.
2. No corrected criterion settles what happens when a non-admin requests a forced reset (for example, "shall reject it with 403"). That must remain an open question or a TBD.

FAIL if either does not hold.
