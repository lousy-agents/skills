---
type: llm
focus: mock_calls
weight: 3
---

Facts of the fixture: the PR targets maintenance branch `1.x`, whose latest release is `v1.3.1`; `main` released `v2.0.0`. A `1.x` maintenance branch therefore accepts patch and minor releases below 2.0.0. The PR adds an exported, documented `toCsv` function — a feature.

Judge the PR comment posted with add_issue_comment. PASS only if all hold:
1. The feature commit is typed `feat` (not downgraded to `fix` or `chore`).
2. It forecasts a minor release (or `1.4.0`) on the `1.x` branch/channel.
3. It does **not** warn that the feat conflicts with the maintenance branch, will fail the release, or that only patches are allowed on `1.x`.

FAIL if any does not hold. Wording does not matter.
