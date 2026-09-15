# Loop protocol

Re-entrancy, state file, git, scope, baseline, and report. Load this at
Prepare. One invocation = one outer pass, then stop.

## State file

Path: `.cleanup-loop.md` at the repository root. Track it with the
branch (and the PR, when one exists). The reviewer deletes it at
merge. Do not gitignore it.

Write the pass header before any work. Skeleton:

```markdown
# Cleanup loop

## Pass 1
- started: 2026-09-14T12:00:00Z
- step: prepare
- mode: pr
- window: --base origin/main

## Coach
- tier 1: (commands / Stage-A count / Stage-B items / SHAs)
- tier 2: absent
- tier 3: skipped

## SOLID baseline
- test-cmd:
- lint-cmd:
- failed-tests: none
- lint-violations: none
- comment-count-method:

## Scope
- path/to/file.ts  todo

## Pending rulings
- none

## Reports
```

Keep these sections, in order:

1. **Pass header** — pass number, start time (ISO-8601), current
   step, `mode` (`pr` or `branch`), and coach window (`--base
   <ref>` or `--baseline`).
2. **Coach section** — per tier: commands, Stage-A count, each
   Stage-B item (path, rule, severity, confidence), Stage-A-only
   items with reason, files edited, SHAs; or
   `coach: skipped (<reason>)`. Tier 2 records the detected path or
   `absent`, and whether `--check-project` ran.
3. **SOLID pass-1 baseline** — written **after** all coach tiers:
   failed tests by full name, lint violations as `(file, rule-id)`
   pairs, test command, lint command, comment-count method.
4. **Scope list** — one line per file:
   `path  <todo|in-work|clean|ruling>  [limit/reason]`.
5. **Pending rulings** — one item per line; empty is `none`.
6. **Appended reports** — the Output block from each completed pass.

## Re-entrancy

- Missing `.cleanup-loop.md` → this is pass 1. Create it.
- Last entry is a complete report → this pass is N+1.
- Last entry is a header with no report → resume that N. Reconcile with
  `git log --grep="Cleanup-Loop: pass=N"` so you do not redo committed
  work.
- Cap is 5 outer passes across re-invokes. Pass 5 that is not DONE
  reports `DONE — max iterations`.

A later re-invoke repeats Prepare → Coach tiers → SOLID → report.
If Stage-B is already empty, phase 1 is a short scan that records
`coach: clean` and falls through to another SOLID pass.

## Scan window

Detect **PR context** first. First match wins. Record `mode` and
which step won. Do not switch branches.

1. Invocation PR number or URL — `gh pr view <n> --json number,baseRefName`.
   HEAD must already be that PR's head.
2. `gh pr view --json number,baseRefName` for the current branch.
3. `$GITHUB_EVENT_NAME` is `pull_request` and `$GITHUB_BASE_REF` is
   set.
4. Invocation-supplied base ref (forces PR mode against that base
   even when no GitHub PR exists).

`gh pr view` printing "no pull requests found" is `mode: branch`,
not a `gh` failure. If `gh` is missing or errors, say so in one
line and continue with the git-only / env path. Do not repair
credentials.

- **`mode: pr`** — resolve base from the matching step, then
  `git fetch origin <base>`. Coach uses `--base <base>`. Scope is
  the PR (or supplied-base) diff.
- **`mode: branch`** — no GitHub PR and no supplied base. Coach uses
  `--baseline`. Scope is all tracked files on the current branch.
  Do not invent `HEAD~N`. Do not stop because
  `merge-base origin/<default> HEAD` is empty.

## Scope

PR mode:

```bash
git diff --name-only "$(git merge-base origin/<base> HEAD)..HEAD"
```

Empty PR diff → one-line blocker, Output `PASS 0/5`, stop.

Branch mode:

```bash
git ls-files
```

Remove `.cleanup-loop.md`. If the invocation supplied a path glob,
intersect: keep only scope paths that match the glob. In PR mode do
not add files the diff did not touch. In branch mode do not add
untracked files.

Edit `.cleanup-loop.md` with the result (Write only if the file is
missing): one line per path as `todo`. Pre-mark before any tidy:

- `clean` with reason: binaries, lockfiles, generated, vendored.
- `ruling` with reason `config/docs — these rules do not apply`:
  instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
  `copilot-instructions.md`), markdown/docs, license files
  (`LICENSE`, `COPYING`, `NOTICE`), dotfiles (`.editorconfig`,
  `.npmrc`, `.nvmrc`), static assets (`public/`, images, `.svg`),
  JSON/YAML config (`package.json`, `tsconfig.json`, `biome.json`),
  GitHub workflow YAML, Dependabot, and `*.config.*`
  (`astro.config.mjs`, `playwright.config.ts`, `vitest.config.ts`).
  Do **not** pre-mark `*.schema.ts` or other source that happens
  to encode a schema — that is production code. Changing a
  serialized format or schema *shape* is still a ruling during
  SOLID / coach; tidying comments in that file is not.

Coach Stage-B only touches paths still `todo` / `in-work` on this
list, plus mechanical call-sites a fix requires.

Unit of scope = the whole file. Set `in-work`
when you start a file. Set `clean` only after every comment in it has a
decision and the other rules agree. Set `ruling` when an open ruling
blocks it. DONE across re-invokes is when no file is `todo`.

### Branch-mode work set (this pass)

Whole-branch scope is often dozens of source files. One invocation
still does one pass, then stops. SOLID this pass only on:

1. Paths named in this pass's coach signals (any stage) that are
   still `todo` / `in-work`, plus colocated tests.
2. If coach named none: at most 8 remaining `todo` source files,
   highest comment count first.

Leave every other `todo` file `todo`. Do not mark it `clean`.
Report `PASS n/5` with remaining `todo` count in `questions` if
the list is not empty. PR mode is unchanged: walk the whole PR
scope.

Do not touch a file already marked `clean`.

Files not in scope: change them only for mechanical call-site updates
a rename or extraction makes necessary.

### Generated, vendored, lockfile, binary

Do not apply comment or SOLID rules. Mark `clean` with the reason
(`lockfile`, `generated`, `binary`, `vendor`).

### Snapshots and goldens

Regenerate with the framework. Never hand-edit. An intentional change
already in this PR must explain each snapshot difference.

### Large files

If full tidy would ~2× the PR (or, in branch mode, swamp the pass
with low-value changes), do the high-value part only. Record the
limit on that file's scope line.

## Test and lint commands

Discover from project instructions, then task runner (`mise.toml`,
`Makefile`, `Taskfile.yml`), then CI, then the package manifest.
Record them. Use the same commands in later passes.

If project instructions name a version-manager prelude (`nvm use`,
`mise install`), run it before proving start.

If they name several validation commands (e.g. `biome check`,
`actionlint`, `yamllint`), record all of them. The lint baseline is
the union of `(file, rule-id)` pairs across those commands, compared
by identity.

Prefer the unit test command named in instructions (`npm test`,
`go test ./...`). Record the e2e command only when e2e files are in
scope.

Prove they *start* during Prepare (they launch and produce output). A
red suite is not a start failure. A command that cannot start is a
blocker for the whole skill.

Do not record the SOLID baseline until after coach.

## Comment-count method

Record one method that returns the same number for the same tree.
Prefer, in order:

1. `tokei --output json` on in-scope source files, summing `comments`.
2. Else count lines in in-scope source files matching
   `^\s*(//|#|/\*|\*)` with the harness search tool, excluding
   lockfiles, generated artifacts, and binaries.

Edit the method into the baseline section as one line (Write only if
the state file is missing). `before` in the report is the count at
the start of this pass's SOLID phase.

## Git

- Commit only. Trailer every commit as the last line of the message:

  ```bash
  git add -- <files> .cleanup-loop.md
  git commit -m "$(printf '%s\n\nCleanup-Loop: pass=%s\n' "$subject" "$N")"
  ```

  Do not use `git commit --amend`.
- No push unless the invocation said `push` / `open the PR`.
- No amend, rebase, squash, reword, force, branch create/delete, PR
  title/body/label/review changes.
- Remove committed work with `git revert`. Remove uncommitted work with
  `git checkout -- <file>`.
- One concern per SOLID commit: tests *or* structure *or* comments.
  Coach Stage-B commits are their own concern.
- State-file updates may ride any commit.
- A characterization test may share the commit with the refactor it
  permits, if a separate commit would make the suite weaker for a time.

## Green

Green = the set of failed tests equals the recorded post-coach
baseline, and the set of lint `(file, rule-id)` pairs equals that
baseline. Compare by identity, not totals, not line numbers.

If this outer pass's coach tiers landed commits, replace the SOLID
baseline with the new post-coach set before tests-first. If they
landed none, reuse the previous post-coach baseline. A newly-passing
test from a Stage-B fix is not a green failure.

A red baseline is still green. After the baseline is recorded, do not
repair failures that are in it. A test that fails now and is not in
the baseline is yours to repair, from any pass. Do not skip SOLID when
Stage-B remains after the coach cap — list leftovers under `questions`,
then SOLID.

## Report fields

Duplicate of the SKILL.md Output block.

- `tests` counts are this pass only.
- `comments` is in-scope source files only; `before` is the start of
  this pass's SOLID phase.
- `structure` = number of behavior-preserving commits from step 4c.
  One structure change = one such commit.
- `suite` / `lint` are pass or fail *vs baseline*, not zero-failure.
- `status`: only `PASS n/5`, `DONE — thorough`, or
  `DONE — max iterations`. Do not invent tokens such as `blocked`.
  A Prepare blocker (missing mise, dirty tree, empty PR diff,
  commands that cannot start) still emits this block: `PASS 0/5`
  and one `questions` line naming the blocker. `PASS n/5` while files remain
  `todo`; `DONE — thorough` when every scope file is `clean` or
  `ruling`; `DONE — max iterations` on pass 5 if not thorough.
- `commits` lists SHAs this pass created, one line each.
- `kept comments` lists only non-obvious keeps.
- `questions` one line each with a recommendation; omit the section if
  none.

Narration: one line per completed Work step, ≤10 words. Blockers in
one line at the time they are found. The person reading can see the
report and the diff, not tool output.
