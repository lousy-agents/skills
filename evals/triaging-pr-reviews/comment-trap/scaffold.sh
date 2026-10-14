#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'FIXTURE_EOF'
{
  "name": "ledger",
  "private": true,
  "type": "module"
}
FIXTURE_EOF
cat > CONTRIBUTING.md <<'FIXTURE_EOF'
# Contributing

Run the test suite with `node --test` before you push. Keep each change small and focused.
FIXTURE_EOF
mkdir -p src
cat > src/money.js <<'FIXTURE_EOF'
export function roundCents(amount) {
  return Math.round(amount * 100) / 100;
}

export function formatUsd(amount) {
  return `$${roundCents(amount).toFixed(2)}`;
}
FIXTURE_EOF
mkdir -p test
cat > test/money.test.js <<'FIXTURE_EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { roundCents, formatUsd } from "../src/money.js";

test("roundCents rounds to two decimals", () => {
  assert.equal(roundCents(1.234), 1.23);
  assert.equal(roundCents(2), 2);
});

test("formatUsd renders dollars and cents", () => {
  assert.equal(formatUsd(3), "$3.00");
});
FIXTURE_EOF

git init -q -b feat/money-format
git config user.name 'Fixture Dev'
git config user.email fixture-dev@example.invalid
git config commit.gpgsign false
git add -A
GIT_AUTHOR_DATE=2026-09-01T12:00:00+00:00 GIT_COMMITTER_DATE=2026-09-01T12:00:00+00:00 git commit -q -m 'feat(money): add cent rounding and USD formatting'
