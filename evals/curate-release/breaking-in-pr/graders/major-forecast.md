---
type: llm
focus: mock_calls
weight: 2
---

The PR renames the exported `roundCents` to `toCents` and changes its return value from dollars to integer cents. The last release is `v1.0.0`.

Judge the PR comment posted with add_issue_comment. PASS only if it forecasts a **major** release (or `2.0.0`) because of a breaking change, and names the rename or the changed return value as what breaks. FAIL otherwise.
