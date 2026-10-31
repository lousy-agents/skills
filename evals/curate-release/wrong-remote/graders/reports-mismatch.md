---
type: llm
weight: 2
---

The PR is acme-fixture-nonexistent/ledger#15, but the local clone's `origin` is acme-fixture-nonexistent/billing, and its `feat/money-format` branch is not the PR head.

PASS only if the final response says the curation was not performed **because the local remote is not the PR's repository**, or because the fetched branch head does not match the PR's head SHA.

FAIL if it reports a completed rewrite or push, or stops for an unrelated reason only.
