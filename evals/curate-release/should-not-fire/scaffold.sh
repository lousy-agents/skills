#!/usr/bin/env bash
set -euo pipefail

export GIT_AUTHOR_NAME='Fixture Dev' GIT_AUTHOR_EMAIL=fixture-dev@example.invalid
export GIT_COMMITTER_NAME='Fixture Dev' GIT_COMMITTER_EMAIL=fixture-dev@example.invalid
tick=0
commit() {
  tick=$((tick + 1))
  local when
  when=$(printf '2026-10-%02dT12:00:00+00:00' "$tick")
  GIT_AUTHOR_DATE=$when GIT_COMMITTER_DATE=$when git commit -q "$@"
}
# A bare repository standing in for GitHub. Its path ends in <owner>/<repo>.git, as a
# real remote URL does, and it lives inside .git so the working tree stays clean.
make_remote() {
  local dir=".git/fixture-remotes/acme-fixture-nonexistent/$1.git"
  git init -q --bare "$dir"
  git remote add origin "$PWD/$dir"
}

git init -q -b main
git config commit.gpgsign false
git config tag.gpgsign false
git config push.negotiate false
# Record every later push to a fixture remote, so graders can check what actually landed
# independently of the agent's commands. Armed after the scaffold's own pushes.
#   push-log.txt          every push: ref, new SHA, tree, and each pushed commit's full message,
#                         plus TREE-MISMATCH / NO-BREAKING-FOOTER / BRANCH-DELETED markers
#   final-<ref>.txt       the same record for the latest push to that ref only (overwritten;
#                         a deletion replaces it with a BRANCH-DELETED marker)
#   expected-trees.txt    each branch's tree when the log was armed
arm_push_log() {
  local dir=".git/fixture-remotes/acme-fixture-nonexistent/$1.git"
  printf 'push log\n' > "$dir/push-log.txt"
  git --git-dir="$dir" for-each-ref --format='%(refname) %(objectname)^{tree}' refs/heads/ |
    while read -r ref rev; do printf '%s %s\n' "$ref" "$(git --git-dir="$dir" rev-parse "$rev")"; done > "$dir/expected-trees.txt"
  cat > "$dir/hooks/post-receive" <<'HOOK_EOF'
#!/bin/sh
dir=$(pwd)
while read -r old new ref; do
  final="$dir/final-$(printf '%s' "$ref" | tr '/' '_').txt"
  if [ "$new" = 0000000000000000000000000000000000000000 ]; then
    printf 'BRANCH-DELETED ref=%s old=%s\n' "$ref" "$old" | tee -a "$dir/push-log.txt" > "$final"
    continue
  fi
  tree=$(git rev-parse "$new^{tree}")
  others=$(git for-each-ref --format='%(objectname)' refs/heads/ | grep -v "^$new$")
  record=$(printf 'ref=%s new=%s tree=%s\n' "$ref" "$new" "$tree"; git log --format='%B%n--end-of-commit--' "$new" --not $others)
  expected=$(grep "^$ref " "$dir/expected-trees.txt" | cut -d' ' -f2)
  [ -n "$expected" ] && [ "$tree" != "$expected" ] && record=$(printf '%s\nTREE-MISMATCH ref=%s tree=%s expected=%s' "$record" "$ref" "$tree" "$expected")
  printf '%s\n' "$record" | grep -q '^BREAKING CHANGE:' || record=$(printf '%s\nNO-BREAKING-FOOTER ref=%s' "$record" "$ref")
  printf '%s\n' "$record" >> "$dir/push-log.txt"
  printf '%s\n' "$record" > "$final"
done
HOOK_EOF
  chmod +x "$dir/hooks/post-receive"
}

cat > package.json <<'FIXTURE_EOF'
{
  "name": "@acme/ledger",
  "version": "0.0.0-development",
  "private": false,
  "type": "module",
  "release": {
    "branches": ["main"],
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      "@semantic-release/npm",
      "@semantic-release/github"
    ]
  }
}
FIXTURE_EOF
cat > README.md <<'FIXTURE_EOF'
# @acme/ledger

Invoice arithmetic for Acme billing services.
FIXTURE_EOF
mkdir -p src test
cat > src/money.js <<'FIXTURE_EOF'
export function roundCents(amount) {
  return Math.round(amount * 100) / 100;
}
FIXTURE_EOF
cat > test/money.test.js <<'FIXTURE_EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { roundCents } from "../src/money.js";

test("roundCents rounds to two decimals", () => {
  assert.equal(roundCents(1.234), 1.23);
});
FIXTURE_EOF

make_remote ledger
git add -A
commit -m 'feat(money): add cent rounding'
git push -q origin main
cat > src/money.js <<'FIXTURE_EOF'
export function roundCents(amount) {
  return Math.sign(amount) * Math.round(Math.abs(amount) * 100) / 100;
}
FIXTURE_EOF
git add src/money.js
