#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'FIXTURE_EOF'
{
  "name": "notifier",
  "private": true,
  "type": "module"
}
FIXTURE_EOF
cat > CONTRIBUTING.md <<'FIXTURE_EOF'
# Contributing

Run the test suite with `node --test` before you push. Keep each change small and focused.
FIXTURE_EOF
mkdir -p src
cat > src/retry.js <<'FIXTURE_EOF'
export function backoffDelay(attempt, { baseMs = 100, maxDelayMs = 30000 } = {}) {
  return baseMs * 2 ** attempt;
}

export function hookUrl(baseUrl, id) {
  return `${baseUrl}/hooks/${encodeURIComponent(id)}`;
}
FIXTURE_EOF
mkdir -p test
cat > test/retry.test.js <<'FIXTURE_EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { backoffDelay, hookUrl } from "../src/retry.js";

test("backoffDelay doubles per attempt", () => {
  assert.equal(backoffDelay(0), 100);
  assert.equal(backoffDelay(3), 800);
});

test("hookUrl encodes the hook id", () => {
  assert.equal(hookUrl("https://hooks.example.test", "a b"), "https://hooks.example.test/hooks/a%20b");
});
FIXTURE_EOF

git init -q -b feat/webhook-retry
git config user.name 'Fixture Dev'
git config user.email fixture-dev@example.invalid
git config commit.gpgsign false
git add -A
GIT_AUTHOR_DATE=2026-09-01T12:00:00+00:00 GIT_COMMITTER_DATE=2026-09-01T12:00:00+00:00 git commit -q -m 'feat(webhooks): add retry backoff and hook URL builder'
