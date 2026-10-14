#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'FIXTURE_EOF'
{
  "name": "stockroom",
  "private": true,
  "type": "module"
}
FIXTURE_EOF
cat > CONTRIBUTING.md <<'FIXTURE_EOF'
# Contributing

Run the test suite with `node --test` before you push. Keep each change small and focused.
FIXTURE_EOF
mkdir -p src
cat > src/csv.js <<'FIXTURE_EOF'
export function toCsv(rows) {
  if (rows.length === 0) return "";
  const header = Object.keys(rows[0]);
  const lines = rows.map((row) => header.map((key) => String(row[key])).join(","));
  return [header.join(","), ...lines].join("\n");
}
FIXTURE_EOF
mkdir -p test
cat > test/csv.test.js <<'FIXTURE_EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { toCsv } from "../src/csv.js";

test("toCsv writes a header and one line per row", () => {
  assert.equal(toCsv([{ sku: "ABC-1234", qty: 3 }]), "sku,qty\nABC-1234,3");
});
FIXTURE_EOF

git init -q -b feat/csv-export
git config user.name 'Fixture Dev'
git config user.email fixture-dev@example.invalid
git config commit.gpgsign false
git add -A
GIT_AUTHOR_DATE=2026-09-01T12:00:00+00:00 GIT_COMMITTER_DATE=2026-09-01T12:00:00+00:00 git commit -q -m 'feat(export): add CSV export for the catalog'
