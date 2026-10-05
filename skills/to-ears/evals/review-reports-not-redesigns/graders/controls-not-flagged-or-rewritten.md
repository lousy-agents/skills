---
type: llm
weight: 3
---
AC-1.1 and AC-1.7 are well-formed criteria that a good review leaves essentially alone.

PASS only if both hold:
1. No finding rated Blocker or High is filed against AC-1.1 or AC-1.7 themselves. A Medium or Low note, or a finding that only mentions AC-1.7 as the other side of AC-1.12's conflict, is acceptable. A gap about missing behavior filed under AC-1.1 or AC-1.7 as High or Blocker counts as a FAIL.
2. In the corrected draft, AC-1.1 still has the auth-api sending the reset link to the verified email address, and AC-1.7 still rejects links older than 60 minutes with HTTP 410. Minor wording changes are fine, and so is an inline "[TBD: conflicts with AC-… — OQ-…]" marker or a Medium/Low open question about which component sends. Moving the sending to another component, adding new obligations, or changing 60 or 410 is a FAIL.

FAIL if either does not hold.
