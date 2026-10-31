---
type: llm
focus: mock_calls
weight: 3
---

Facts of the fixture: the last release is tag `v1.4.0`. Since then `main` has `feat(export): add CSV export of invoice lines` (also tagged `deploy-prod-2026-10-20`, a deployment marker, not a release) and `fix(auth): reject expired API tokens`, whose body carries a `BREAKING CHANGE:` footer. So the next release is a **major** whatever this PR does. This PR is a consumer-visible performance fix.

Judge the PR comment posted with add_issue_comment. PASS only if all hold:
1. It treats `v1.4.0` as the last release (it does not treat `deploy-prod-2026-10-20` as the last release).
2. It says the next release is major (or 2.0.0) because of a breaking change already queued, and that this PR does not change the version (or does not by itself drive the bump).
3. The PR's speedup commit is typed `perf` or `fix`, not `chore`/`refactor`, and the comment does not claim that `perf` produces no release.

FAIL if any does not hold. Wording does not matter.
