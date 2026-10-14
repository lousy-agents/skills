#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'FIXTURE_EOF'
{
  "name": "authgate",
  "private": true,
  "type": "module"
}
FIXTURE_EOF
cat > CONTRIBUTING.md <<'FIXTURE_EOF'
# Contributing

Run the test suite with `node --test` before you push. Keep each change small and focused.
FIXTURE_EOF
mkdir -p src
cat > src/token.js <<'FIXTURE_EOF'
export function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

export function parseBearer(header) {
  if (typeof header !== "string") return null;
  const [, token] = header.split(" ");
  return token || null;
}
FIXTURE_EOF
mkdir -p test
cat > test/token.test.js <<'FIXTURE_EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { safeEqual, parseBearer } from "../src/token.js";

test("safeEqual matches equal keys", () => {
  assert.equal(safeEqual("k3y-abc", "k3y-abc"), true);
  assert.equal(safeEqual("k3y-abc", "k3y-abd"), false);
  assert.equal(safeEqual("short", "longer"), false);
});

test("safeEqual reads every character even after the first mismatch", () => {
  let reads = 0;
  const probe = (text) => ({
    length: text.length,
    charCodeAt(i) {
      reads++;
      return text.charCodeAt(i);
    },
  });
  assert.equal(safeEqual(probe("aaaa"), probe("baaa")), false);
  assert.equal(reads, 8);
});

test("parseBearer extracts the token", () => {
  assert.equal(parseBearer("Bearer abc.def"), "abc.def");
  assert.equal(parseBearer(undefined), null);
});
FIXTURE_EOF

git init -q -b feat/token-helpers
git config user.name 'Fixture Dev'
git config user.email fixture-dev@example.invalid
git config commit.gpgsign false
git add -A
GIT_AUTHOR_DATE=2026-09-01T12:00:00+00:00 GIT_COMMITTER_DATE=2026-09-01T12:00:00+00:00 git commit -q -m 'feat(auth): add token comparison and bearer parsing helpers'
