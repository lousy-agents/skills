# Loop protocol

Re-entrancy, state file, git, scope, baseline, and report. Load this at
Prepare. One invocation = one outer pass, then commit the report and
stop.

## State file

Path: `.cleanup-loop.md` at the repository root. Track it with the
branch (and the PR, when one exists). The reviewer deletes it at
merge. Do not gitignore it.

Write the pass header after every Prepare blocker has passed and
before any coach or SOLID work. Skeleton:

```markdown
# Cleanup loop

## Pass 1
- started: 2026-09-14T12:00:00Z
- step: prepare
- mode: pr
- base: origin/main (a1b2c3d, from: gh pr view)
- window: --base origin/main

## Coach
- pre-coach check: failed-tests: none; lint-violations: none
- tier 1: (commands / Stage-A count / Stage-B items / holding tests / SHAs)
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
   step (`prepare`, `coach`, `solid`, `verify`, `done`), `mode` (`pr`
   or `branch`), resolved `base` with its OID and the step that
   produced it (`inferred` when the git-only path chose the default
   branch), and coach window (`--base <ref>` or `--baseline`). One
   header only: each pass rewrites it. Edit `step` as each phase
   starts, so a resumed pass knows where the previous one stopped.
2. **Coach section** — the pre-coach check (failed tests by full
   name, lint `(file, rule-id)` pairs from Prepare's start-proof
   run); then per tier: commands, Stage-A count, each Stage-B item
   (path, rule, severity, confidence), the holding test each fix
   added, Stage-A-only items with reason, files edited, SHAs; or
   `coach: skipped (<reason>)`. Tier 2 records the detected path or
   `absent`, and whether `--check-project` ran.
3. **SOLID pass-1 baseline** — written **after** all coach tiers:
   failed tests by full name, lint violations as `(file, rule-id)`
   pairs, test command, lint command, comment-count method.
4. **Scope list** — one line per file:
   `path  <todo|in-work|clean|ruling>  [limit/reason]`.
5. **Pending rulings** — one item per line; empty is `none`.
6. **Appended reports** — one `### Pass N` block per completed pass,
   holding that pass's Output block verbatim.

## Re-entrancy

- Missing `.cleanup-loop.md` → this is pass 1. Create it once Prepare
  has passed every blocker.
- Header says pass N and Reports has a `### Pass N` block → this pass
  is N+1.
- Header says pass N and Reports has no `### Pass N` block → an
  earlier pass stopped before finalize. Resume that N. Reconcile with
  `git log --grep="Cleanup-Loop: pass=N$"` (anchor the number so
  `pass=1` does not match `pass=10`) so you do not redo committed
  work. The header's `step` says where it stopped: copy it to
  `resumed-from: <step>` before Prepare rewrites `step`.
- Last report's status is `DONE — max iterations` → re-emit that
  report and stop. `DONE — thorough` → the same, unless the
  re-admission scan (Scope) finds a commit without the trailer that
  touched a scope path since that finalize; then start pass N+1 on
  the re-admitted paths. Starting over on purpose is a human act:
  delete `.cleanup-loop.md` in a commit.
- Cap is 5 outer passes across re-invokes. Pass 5 that is not DONE
  reports `DONE — max iterations`.

Every pass ends with a finalize commit that carries the appended
report (see Git). That is why a re-invoke starts from a clean tree
and why a fresh checkout of the branch contains every report.

A later re-invoke repeats Prepare → Coach tiers → SOLID → report.
If Stage-B is already empty, phase 1 is a short scan that records
`coach: clean` and falls through to another SOLID pass.

## Scan window

Detect **PR context** first. First match wins. Record `mode` and
which step won. Do not switch branches. A detached HEAD
(`git symbolic-ref -q HEAD` fails) is a Prepare blocker before any
of this: loop commits must land on a branch.

0. Invocation said `whole-repo` → `mode: branch`; stop here. It wins
   over a PR number or a base ref given in the same invocation; say
   so in one line.
1. Invocation PR number or URL —
   `gh pr view <n> --json number,baseRefName,headRefName`, or the
   GitHub MCP tool `pull_request_read` (method `get`: `head.ref`,
   `base.ref`) when the harness offers that instead of `gh`. HEAD
   must already be that PR's head; otherwise a blocker.
2. Invocation-supplied base ref. Forces `mode: pr` against that base
   even when a GitHub PR targeting another branch exists.
3. The current branch's open PR: `gh pr view --json
   number,baseRefName`, or the GitHub MCP tool `list_pull_requests`
   with `state: open` and `head: <owner>:<branch>`, owner and repo
   parsed from `git remote get-url origin` — only when that URL is on
   github.com. Exactly one open PR → its `base.ref`.
4. `$GITHUB_EVENT_NAME` is `pull_request` and `$GITHUB_BASE_REF` is
   set.
5. `$CLAUDE_CODE_BASE_REF` is set, names a branch other than HEAD's,
   and resolves in this repository after `git fetch origin <ref>`.
   Claude Code Remote sets it to the branch the session was forked
   from, which is the natural base of the session's work branch. It
   is session-scoped, not repo-scoped: in any other checkout (a
   scratch repo, a second clone) it names a branch that does not
   exist there — ignore it in one line, never block on it. Equal to
   HEAD's branch → ignore it too (a session started on a PR branch
   has that PR found by step 3).
6. Git-only path — no PR found by `gh` or MCP (`gh` missing, erroring,
   or printing "no pull requests found"), and no env var applies.
   Resolve the default
   branch, first that succeeds: `git symbolic-ref -q
   refs/remotes/origin/HEAD`; `git remote set-head origin --auto`
   then the same `symbolic-ref` (needs the remote; failure is
   tolerated); `origin/main`; `origin/master`; local `main`; local
   `master` (each via `git rev-parse --verify -q "<ref>^{commit}"`).
   None → one-line blocker: pass a base ref or `whole-repo`. Then:
   - `git rev-parse --abbrev-ref HEAD` *is* that default branch →
     `mode: branch`;
   - otherwise → `mode: pr` against the default branch, recorded as
     `base: <resolved> (<oid>, from: inferred)`.

Missing or failing `gh` is one line of narration and never a blocker.
Do not repair credentials. Claude Code Remote has no `gh` and no
`GITHUB_*` event vars but exposes the GitHub MCP tools; use them in
steps 1 and 3 exactly as you would `gh`. Never map "gh is missing" to
"no PR exists": a feature branch without `gh` still diffs against the
default branch, so coach Stage-B stays capped to that diff.

- **`mode: pr`** — normalize the base (below). Coach uses
  `--base <resolved-base>`. Scope is the merge-base diff.
- **`mode: branch`** — only on the default branch or when asked for
  `whole-repo`. Coach uses `--baseline`. Scope is all tracked files
  on the current branch. Do not invent `HEAD~N`.

### Base normalization

The invocation and `gh` hand you a *ref*, not necessarily a remote
branch name. Fetch by branch, resolve to one verified ref, and use
that ref everywhere.

```bash
ref="<as supplied or detected>"
branch="${ref#refs/remotes/origin/}"
branch="${branch#refs/heads/}"
branch="${branch#origin/}"
git fetch origin "$branch" 2>/dev/null || true   # no remote copy is not fatal yet
if git rev-parse --verify -q "origin/$branch^{commit}" >/dev/null; then
  base="origin/$branch"
elif git rev-parse --verify -q "$ref^{commit}" >/dev/null; then
  base="$ref"                                     # local branch, tag, or SHA
else
  base=""                                         # blocker: base ref does not resolve
fi
```

`main` and `origin/main` therefore select the same base. An empty
`base` is a Prepare blocker: one line, Output `PASS 0/5`, no edits,
stop. Record `base: <base> (<oid from git rev-parse --short>, from:
<step>)` in the pass header and reuse `$base` verbatim for
`git merge-base` and for coach `--base`. Do not treat a failed
resolution as an empty diff.

## Scope

PR mode:

```bash
mb="$(git merge-base "$base" HEAD)" || mb=""
[ -n "$mb" ] || exit 1   # blocker: no merge-base (shallow clone or unrelated history)
git diff --name-only --diff-filter=d "$mb..HEAD"
```

Check `merge-base` on its own. Substituting a failed `merge-base`
into the diff yields `..HEAD`, which exits 0 with no output and would
be misread as an empty diff — the default `actions/checkout`
(`fetch-depth: 1`) produces exactly that. The blocker line names the
cause and the remedy (`git fetch --unshallow origin <branch>`, or
`fetch-depth: 0`).

`--diff-filter=d` drops paths the branch deleted: there is nothing
at HEAD to tidy. A rename lists only its new path. Empty diff →
one-line blocker naming the base, Output `PASS 0/5`, stop. Tell the
user that `whole-repo` hunts the branch instead.

Branch mode:

```bash
git ls-files
```

Remove `.cleanup-loop.md`. If the invocation supplied a path glob,
intersect: keep only scope paths that match the glob. A glob that
leaves no path is a one-line blocker naming the glob (`PASS 0/5`),
never a vacuous `DONE — thorough`. In PR mode do not add files the
diff did not touch. In branch mode do not add untracked files.

Compute this list before the state file is created or edited, so a
blocker never leaves a dirty tree.

### Reconcile, never reset

On pass 1, Write the skeleton and list every scope path as `todo`,
with the pre-marks below. On every later pass, Read the state file
and Edit the Scope section by reconciling membership while preserving
progress:

- A path already on the list keeps its status (`todo`, `in-work`,
  `clean`, `ruling`), its limit, and its reason. Never rewrite an
  existing line back to `todo`.
- A path new to the scope is added as `todo` (or pre-marked).
- A path that left the scope is dropped from the list. If it was
  `in-work` or `ruling`, say so under `questions`. Its pending ruling
  stays in Pending rulings.
- The one permitted invalidation: a `clean` path returns to `todo`
  when a commit **without** the `Cleanup-Loop` trailer touched it
  since the previous pass's finalize commit (someone pushed new work
  between passes). Detect it with:

  ```bash
  prev="$(git log --grep="Cleanup-Loop: pass=$((N-1))$" -1 --format=%H)"
  git log --invert-grep --grep='Cleanup-Loop: pass=' --name-only --format= "$prev..HEAD"
  ```

  Write `re-admitted: <sha>` on that line, and re-admit the colocated
  test file of a re-admitted production file (`re-admitted: colocated
  test of <path>`): tests-first must be able to hold the behavior the
  foreign commit added. Nothing else changes a `clean` line.

Pre-mark before any tidy:

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
  SOLID / coach; tidying comments in that file is not. These
  pre-marked lines are not work: record **one** pending-ruling entry
  for the group (`config/docs pre-marked ruling — confirm skip`), not
  one per file, and count them as done for `DONE — thorough`.

Coach Stage-B only touches paths still `todo` / `in-work` on this
list, plus mechanical call-sites a fix requires. A Stage-B signal on
a `clean` or `ruling` path, or outside the invocation glob, is listed
under `questions` and left alone.

Unit of scope = the whole file. Set `in-work`
when you start a file. Set `clean` only after every comment in it has a
decision and the other rules agree. Set `ruling` when an open ruling
blocks it. DONE across re-invokes is when no file is `todo`.

### Branch-mode work set (this pass)

Whole-branch scope is often dozens of source files. One invocation
still does one pass, then stops. Select the SOLID work set in this
order:

1. **Eligible coach set**: paths named in this pass's coach signals
   (any stage) that are still `todo` / `in-work` **and** inside the
   invocation glob, plus their colocated tests. Filter by status and
   glob first; `clean`, `ruling`, and out-of-glob paths never count.
2. **Fallback**: if that eligible set is empty — whether coach named
   nothing, or named only paths the filter removed — at most 8
   remaining `todo` source files, highest comment count first.

A persistent Stage-A signal on a `clean` file must not starve the
fallback: `a.ts clean` with a signal and `b.ts todo` selects `b.ts`.

Leave every other `todo` file `todo`. Do not mark it `clean`.
Report `PASS n/5` with the remaining `todo` count in `questions` if
the list is not empty. PR mode is unchanged: walk the whole PR
scope.

Do not touch a file already marked `clean` unless Prepare re-admitted
it.

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

Record the **check** form of each command. A manifest `lint` script
is often a fixer (`eslint . --fix`, `biome check --write`); bind to
the tool's `--help` for its report-only form (`--check`, `--no-fix`)
and record that. A fixer would rewrite tracked source during the
start-proof run, trip the dirty-tree guard on the next invocation,
and hide the very violations the baseline must list.

Prove they *start* during Prepare (they launch and produce output). A
red suite is not a start failure. A command that cannot start is a
blocker for the whole skill. If the run changed the tree anyway
(`git status --porcelain` is no longer empty), `git checkout --` the
tracked changes and delete the files it created before continuing;
the same restore runs before every commit and before finalize. Keep
that run's failed-test names and lint pairs as the **pre-coach
check**: the coach regression guard in `coach-phase.md` compares each
Stage-B fix against it.

Do not record the SOLID baseline until after coach.

## Comment-count method

Record one method that returns the same number for the same tree.
Prefer, in order:

1. `tokei --output json` on in-scope source files, summing `comments`.
2. Else count lines in in-scope source files matching
   `^\s*(//|#|/\*|\*)` with the harness search tool, excluding
   lockfiles, generated artifacts, and binaries.

Edit the method into the baseline section as one line. `before` in
the report is the count at the start of this pass's SOLID phase.

## Git

- Commit only. Trailer every commit as the last line of the message:

  ```bash
  git add -- <files> .cleanup-loop.md
  git commit -m "$(printf '%s\n\nCleanup-Loop: pass=%s\n' "$subject" "$N")"
  ```

  Do not use `git commit --amend`.
- **Finalize commit, every pass.** After the report is appended to
  `.cleanup-loop.md` and the header says `step: done`:

  ```bash
  git add -- .cleanup-loop.md
  git commit -m "$(printf 'chore(cleanup-loop): record pass %s report\n\nCleanup-Loop: pass=%s\n' "$N" "$N")"
  git status --porcelain   # must print nothing
  ```

  Do this even when the pass changed no source file, so the next
  invocation starts from a clean tree and a fresh checkout carries the
  report. The report cannot embed this commit's own SHA, so `commits`
  lists source commits only; the finalize commit is always the last
  match of `git log --grep="Cleanup-Loop: pass=N$"`.
- No push unless the invocation said `push` / `open the PR`. When it
  did, push after the finalize commit: `git push` to the tracking
  remote, or `git push origin HEAD` when no upstream is set. Never
  `--force`.
- No amend, rebase, squash, reword, force, branch create/delete, PR
  title/body/label/review changes.
- Remove committed work with `git revert`. Remove uncommitted work with
  `git checkout -- <file>`.
- One concern per SOLID commit: tests *or* structure *or* comments.
  Coach Stage-B commits are their own concern; each carries the fix
  and the holding test that proves it.
- State-file updates may ride any commit.
- A characterization test may share the commit with the refactor it
  permits, if a separate commit would make the suite weaker for a time.

## Green

Green = the set of failed tests equals the recorded post-coach
baseline, and the set of lint `(file, rule-id)` pairs equals that
baseline. Compare by identity, not totals, not line numbers.

Record the SOLID baseline from the post-coach tree when either holds:

- no SOLID baseline exists in the state file yet (pass 1, including
  a pass 1 whose coach phase was skipped or landed nothing);
- this outer pass's coach tiers landed commits;
- Prepare's re-admission scan found non-loop commits since the
  previous finalize (someone pushed new work; the recorded baseline
  describes a tree that no longer exists).

Otherwise reuse the recorded post-coach baseline. A newly-passing test
from a Stage-B fix is not a green failure. The coach regression guard
already rejected any fix that introduced a failure, so a refreshed
baseline never legitimizes a coach regression.

A red baseline is still green. After the baseline is recorded, do not
repair failures that are in it. A test that fails now and is not in
the baseline is yours to repair, from any pass. Do not skip SOLID when
Stage-B remains after the coach cap — list leftovers under `questions`,
then SOLID.

## Report fields

Duplicate of the SKILL.md Output block.

- `tests` counts are this pass only, and include a holding test the
  coach phase added.
- `comments` is in-scope source files only; `before` is the start of
  this pass's SOLID phase.
- `structure` = number of behavior-preserving commits from step 4c.
  One structure change = one such commit.
- `suite` / `lint` are pass or fail *vs baseline*, not zero-failure.
- `status`: only `PASS n/5`, `DONE — thorough`, or
  `DONE — max iterations`. Do not invent tokens such as `blocked`.
  A Prepare blocker (missing mise, dirty tree, detached HEAD,
  unresolvable base, no merge-base, empty diff, empty glob, commands
  that cannot start) still emits this block in chat: `PASS 0/5` and
  one `questions` line naming the blocker. It is not appended to
  `.cleanup-loop.md`; a blocker never touches the state file.
  - PR mode: `DONE — thorough` iff every scope file is `clean` or
    `ruling`; else `PASS n/5`.
  - Branch mode: `DONE — thorough` iff no `todo` remains across
    re-invokes. A pass that finished only its work set and left other
    `todo` files is `PASS n/5` with the remaining count under
    `questions`. Never mark unvisited files `clean` to reach DONE.
  - `DONE — max iterations` on pass 5 if not thorough.
- `commits` lists source SHAs this pass created, one line each. The
  finalize commit is excluded (see Git).
- `kept comments` lists only non-obvious keeps.
- `questions` one line each with a recommendation; omit the section if
  none.

Narration: one line per completed Work step, ≤10 words. Blockers in
one line at the time they are found. The person reading can see the
report and the diff, not tool output.
