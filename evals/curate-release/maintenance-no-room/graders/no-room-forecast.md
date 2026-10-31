---
type: llm
focus: mock_calls
weight: 3
---

Facts of the fixture: `1.x` is a maintenance branch cut from `main` at `v1.4.2`, `main`'s latest release; `main` has released nothing since. semantic-release therefore gives `1.x` the range `>=1.4.2 <1.4.2` — it accepts no release, and any release from it fails. The PR adds an exported feature.

Judge the PR comment posted with add_issue_comment. PASS only if all hold:
1. The feature commit is typed `feat` (not downgraded to fix or chore to make it fit).
2. It warns that a release from `1.x` will fail or that `1.x` currently accepts no version, because `main` has not released past `1.4.2`.

FAIL if it forecasts `1.5.0` (or a minor) as a release that will publish without that warning. Wording does not matter.
