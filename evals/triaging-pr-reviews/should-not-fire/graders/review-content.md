---
type: llm
---

The PR adds `toCsv(rows)` in src/csv.js, which joins raw values with commas and does no quoting or escaping.

PASS if the reply is a review of this change that raises at least one concrete point about `toCsv` (for example: values containing commas, double quotes, or newlines are not quoted or escaped; rows with different keys; null or undefined values).

FAIL if the reply instead reports on triaging existing review comments, says there is nothing to review, or does not discuss `toCsv` at all.
