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
cat > src/pagination.js <<'FIXTURE_EOF'
export function pageCount(total, perPage) {
  if (!Number.isInteger(perPage) || perPage < 1) {
    throw new RangeError("perPage must be a positive integer");
  }
  return Math.floor(total / perPage);
}

export function pageSlice(items, page, perPage) {
  const start = (page - 1) * perPage;
  return items.slice(start, start + perPage);
}
FIXTURE_EOF
mkdir -p src
cat > src/sku.js <<'FIXTURE_EOF'
export class InvalidSkuError extends Error {}

export function normalizeSku(input) {
  if (typeof input !== "string") {
    throw new InvalidSkuError("SKU must be a string");
  }
  const sku = input.trim().toUpperCase();
  if (!/^[A-Z]{3}-\d{4}$/.test(sku)) throw new InvalidSkuError(`Invalid SKU: ${sku}`);
  return sku;
}
FIXTURE_EOF
mkdir -p test
cat > test/pagination.test.js <<'FIXTURE_EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { pageCount, pageSlice } from "../src/pagination.js";

test("pageCount divides evenly", () => {
  assert.equal(pageCount(100, 10), 10);
  assert.equal(pageCount(0, 10), 0);
});

test("pageCount rejects a non-positive page size", () => {
  assert.throws(() => pageCount(10, 0), RangeError);
});

test("pageSlice returns the requested page", () => {
  assert.deepEqual(pageSlice([1, 2, 3, 4, 5], 2, 2), [3, 4]);
});
FIXTURE_EOF
mkdir -p test
cat > test/sku.test.js <<'FIXTURE_EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { normalizeSku, InvalidSkuError } from "../src/sku.js";

test("normalizeSku trims and upper-cases", () => {
  assert.equal(normalizeSku("  abc-1234 "), "ABC-1234");
});

test("normalizeSku rejects non-string input with InvalidSkuError", () => {
  assert.throws(() => normalizeSku(undefined), InvalidSkuError);
  assert.throws(() => normalizeSku(42), InvalidSkuError);
});
FIXTURE_EOF

git init -q -b feat/catalog-pagination
git config user.name 'Fixture Dev'
git config user.email fixture-dev@example.invalid
git config commit.gpgsign false
git add -A
GIT_AUTHOR_DATE=2026-09-01T12:00:00+00:00 GIT_COMMITTER_DATE=2026-09-01T12:00:00+00:00 git commit -q -m 'feat(catalog): paginate product listing and normalize SKUs'
