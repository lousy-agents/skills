# Coach phase

Driver of the outer pass. Runs **before** SOLID. Load this after
Prepare. Baseline for SOLID is recorded only after every coach tier.

Coach has no Stage A/B. Classification is ours.

## Invoke

Resolve the binary once per invocation: the first path below that
runs `coach codesignal --help`. Record which one in the state file.

1. Portable default — the GitHub release through mise:

   ```bash
   mise exec github:lousy-agents/coach@v0.6.0 -- coach codesignal --format json <args>
   ```

2. GitHub API refused. Claude Code Remote answers mise's release
   lookup with HTTP 403 (`GitHub access to this repository is not
   enabled for this session`) for a repository that is not attached
   to the session. Use mise's Go backend, which resolves through the
   Go module proxy and never calls the GitHub API:

   ```bash
   MISE_FETCH_REMOTE_VERSIONS_TIMEOUT=60s \
      mise exec "go:github.com/lousy-agents/coach/cmd/coach@v0.6.0" -- coach codesignal --format json <args>
   ```

   The timeout is load-bearing: mise's default 3 s version-resolve
   window times out behind the remote proxy; 60 s installs in about
   30 s.

3. Source build from a scratch clone — anonymous git reads are served
   even where the API is not:

   ```bash
   src="$(mktemp -d)"; bin="$(mktemp)"
    git clone --depth 1 --branch v0.6.0 https://github.com/lousy-agents/coach "$src"
   (cd "$src" && go build -o "$bin" ./cmd/coach)
   "$bin" codesignal --format json <args>
   rm -rf "$src" "$bin"
   ```

   Use the Go on PATH, else `mise exec go@latest -- go build …`.

Dogfood **only** when `./cmd/coach` exists in cwd (the repository *is*
coach): `mise exec -- go build -o "$(mktemp)" ./cmd/coach` and use
that binary. Do not call `go build ./cmd/coach` in any other repo.

Delete every scratch clone and binary on every exit path. If none of
the paths runs, coach is skipped (`coach: skipped (<reason>)`) and
SOLID still runs.

Read `<binary> codesignal --help` once per invocation. Do not invent
flags. Bind every flag you add to that help text.

## Skip, do not fail

Read `.cleanup-loop.md` (Prepare already created it), then Edit in
`coach: skipped (<reason>)`. Never Write over it. Continue to SOLID
when:

- no Go/TS/TSX file is in the scope list
- codesignal cannot start after mise is present
- exit 2 for unsupported language or a TypeScript scan that cannot
  resolve a compiler / host Node

Missing `mise` is still a hard blocker for the **whole** skill.

Do **not** run `--prepare-compiler` (TTY, mutates the toolchain).
Do **not** run `--suggest-project-config --project-language
typescript` (interactive TTY). Go `--suggest-project-config
--output` is non-interactive and is the onboarding path below.

Coach window follows Prepare `mode` (do not invent flags):

- **`mode: pr`** — `--base <resolved-base>`. Do not switch to
  `--baseline` because the PR diff analyzed 0 files.
- **`mode: branch`** — `--baseline`. This is the whole-branch hunt,
  chosen only on the default branch or when the user asked for
  `whole-repo`. A feature branch without `gh` is still `mode: pr`
  against the default branch. Do not invent `HEAD~N`.

## JSON consume path

Successful scan: one JSON object on stdout.

Always present: `schema_version`, `scope`, `summary`, `signals`,
`diagnostics`, `coverage`.

`schema_version` is `"1"` without a valid `--project-config`, `"2"`
with one. Version 2 also has `project_changes`, `project_facts`,
`project_summary`, `project_coverage`.

Each signal: `path`, `rule_id`, `severity`, `confidence`,
`why_it_matters`, `recommendation`, `location.start_row` (0-based).

Exit codes (coach contract):

- `0` — command completed. **Not** "no findings". Signals do not
  change this.
- `1` — operational (not a git repo, unresolvable `--base`, I/O).
  Blocker for the coach phase only; skip coach, continue to SOLID.
- `2` — usage, `project_config_invalid`, unsupported language, or TS
  compiler/host unresolved. Empty stdout. Skip-with-reason, continue
  to SOLID. Do not "fix" a config by inventing layers.

Coach analyzes **committed Git objects**, not the dirty worktree.
Commit a Stage-B fix before the next scan or coach will not see it.

## Stage classification

- **Stage A:** every finding with path, rule, severity, confidence.
- **Stage B include bar:** could cause incorrect behavior, a test
  failure, or a misleading result, **and** the file is in tidy scope
  (or a mechanical call-site of an in-scope fix), **and** the remedy
  is a production-code change. Coach-first **may change behavior**
  when the finding is a real defect. Prefer improving production code
  over silencing the scanner.
- Style, naming, unsupported-language diagnostics, informational
  coverage, and metric/density rules (`complexity.*`, density-gated
  `structure.*`) → stay Stage A. Generic "harder to follow / easy
  to miss an edge case" text in `why_it_matters` is still Stage A.
  Promote to Stage B only when `why_it_matters` names a specific
  incorrect result, a failing test, or a misleading output on a
  named path. Do not empty Stage A for its own sake. SOLID may
  still extract those functions later.
- `state.hidden_input_mutation`: Stage B only when an **exported**
  function mutates a caller-owned argument. A private helper that
  `.push`es onto a same-class accumulator stays Stage A; SOLID 4c
  may still return a copy.
- Stage B whose only fix changes a public contract, a schema, or
  layer policy → Ruling required, do not fix.
- Out-of-scope Stage-B paths → do not edit. List them Stage A-only
  with reason `out of scope`. The same applies to a Stage-B path whose
  scope status is `clean` or `ruling`, or that falls outside the
  invocation glob: list it under `questions` and leave it alone.

## Regression guard

Prepare's start-proof run recorded the **pre-coach check**: failed
tests by full name and lint `(file, rule-id)` pairs. Every Stage-B
fix in every tier must clear this guard before it is committed:

1. Orient on the test framework first (`tidy-rules.md`, Framework
   Orient). Add or extend a behavioral test in the repo's real
   container nodes that holds the corrected behavior. It fails on the
   defect and passes on the fix. Do not invent nodes. Put it where
   the repo already keeps tests for that package or directory — the
   nearest existing test file, or a new file beside it on the same
   runner. If the recorded test command cannot exercise that area at
   all, the item is Ruling required (behavior with no test), not a
   silent fix.
2. Run the smallest covering tests, then the full recorded test and
   lint commands.
3. Compare by identity with the pre-coach check:
   - a failed test or lint pair that is **not** in the check set →
     repair it now, or `git checkout -- <files>` the fix and its test.
     Never commit it, never wait for 4a to "baseline" it.
   - a test that was failing in the check set and now passes because
     of the fix → accepted; remove it from the check set.
4. Commit the fix and its holding test together. The check set after
   that commit is the guard for the next fix.

Counterexample this guard exists for: coach edit clears a signal but
breaks `TestUnrelatedBehavior`; without the guard 4a would record that
failure as baseline and SOLID would be forbidden to repair it. With the
guard the fix is repaired or reverted before any commit.

Record each holding test and check result under the tier's line in
the state file.

## Tier 1 — simple scan loop

No `--project-config`. This tier must run even when a project config
exists, so architecture policy never hides a simple finding.

PR mode:

```bash
mise exec github:lousy-agents/coach@v0.6.0 -- coach codesignal --format json \
  --base <resolved-base> --scope production
```

Branch mode:

```bash
mise exec github:lousy-agents/coach@v0.6.0 -- coach codesignal --format json \
  --baseline --scope production
```

Also run `--scope all` when the production scan's
`summary.files_analyzed` is 0, or the user asked for all. A tests-only
PR often analyzes 0 production files; `--scope all` is how coach
sees the test files. If `--scope all` is also 0, record
`coach: no analyzable files` and continue to SOLID. In PR mode do
**not** fall through to `--baseline`. SOLID still tidies test files
that are in the git scope even when coach `--scope production`
excluded them (`coverage.excluded` reason `test_only`).

`--project-language` without `--project-config` is a silent no-op on
a scan (coach default language is `go`). Do not add it in Tier 1
unless `--help` shows a reason to. File-local rules still fire on
Go/TS/TSX paths from the diff.

Cycle ≤5:

`resolve-binary → scan-set → classify Stage A then B → edit in-scope Stage-B paths → regression guard per fix → commit only if guarded edits landed → same scan-set`

Do not commit a no-op cycle, and do not commit a fix that failed the
regression guard. Stop Tier 1 when Stage-B is empty after
a fresh simple scan, or 5 cycles have run, or the simple scan cannot
execute. Leftover Stage-B after the cap does not skip SOLID — list
each leftover under `questions`, then continue. After the tier,
Read `.cleanup-loop.md` and Edit the Tier 1 coach section.

Git during this phase: same as the cleanup loop (commit only, trailer,
no push).

## Tier 2 — detect or onboard a committed project config

Detection, in order, against the **analyzed revision** (`HEAD` after
Tier 1 commits), not an uncommitted worktree file:

1. A path the user named in the invocation, if
   `git cat-file -e "HEAD:<path>"` succeeds.
2. `git cat-file -e HEAD:project.json`.
3. A repository-relative path already recorded in project
   instructions / CI / README as the coach `--project-config` file,
   if that blob exists at `HEAD`.

If a committed config exists, record the path, run the TS readiness
probe when TS is in scope, and go to Tier 3.

If none exist, onboard once (v1 turn-key), then re-detect. Do not
overwrite an existing worktree `project.json`. Create-only.

### Readiness probe (TypeScript in scope)

```bash
mise exec github:lousy-agents/coach@v0.6.0 -- coach codesignal --format json \
  --baseline --check-project --project-language typescript
```

`--check-project` requires `--baseline` and cannot combine with
`--base`. Exit 0 ≠ clean. Payload is `status` / `checks` / `gaps` /
`next_actions` — not a scan, no `signals`. Do not classify Stage
A/B from it. Do not execute `next_actions.prepare_compiler`.
`author_policy` is replaced by the onboard below. Record the
payload in the state file. Compiler mismatch does not block
onboarding; it may still skip Tier 3 (scan exit 2).

### Onboard when policy is missing

1. **Roots.** If tracked `go.mod` files exist, Bash
   `--baseline --suggest-project-config --output project.json`
   (Go, non-interactive, create-only). If that cannot run or the
   repo is TS-only, Write `project.json` with
   `"schema_version": "1"` and `"roots": ["."]` when a root
   `package.json` / `tsconfig.json` / `go.mod` exists, else every
   directory that contains one of those files (from `git ls-files`).
2. **Layers.** Only prefixes that already have tracked `.go` /
   `.ts` / `.tsx`. Add a layer when `git ls-files '<prefix>/*'` is
   non-empty:

   | name | prefixes |
   | --- | --- |
   | entities | `src/entities`, `src/domain/entities` |
   | use-cases | `src/use-cases`, `src/usecases`, `src/domain/usecases` |
   | domain | `src/domain` (only if entities/use-cases prefixes were empty) |
   | gateways | `src/gateways`, `src/infrastructure`, `src/adapters` |
   | components | `src/components` |
   | commands | `src/commands` |
   | handlers | `pkg/handlers`, `src/handlers` |
   | db | `pkg/db`, `src/db` |

   Do not invent a prefix with no source. Skip a name if no prefix
   matched.
3. **Forbidden imports.** Add a pair only when **both** layer
   names exist: `entities→use-cases`, `entities→gateways`,
   `entities→components`, `entities→commands`, `entities→handlers`,
   `use-cases→gateways`, `use-cases→components`, `use-cases→handlers`,
   `use-cases→db`, `domain→gateways`, `domain→components`,
   `domain→handlers`, `domain→db`, `handlers→db`. Do not add
   `required_layer`.
4. Edit `project.json` to include those layers and pairs (2-space
   indent, trailing newline). Commit **only** `project.json` with
   subject `chore(coach): add project.json for codesignal project
   scan` and the pass trailer. Coach reads Git objects; an
   uncommitted config is invisible.
5. Re-run detection. Record `coach: project-config onboarded
   <path>`. If onboard failed, Edit `coach: project-config absent;
   tier 3 skipped (<reason>)` and go to SOLID.

## Tier 3 — project scan loop

Only if Tier 2 found a committed config.

PR mode:

```bash
mise exec github:lousy-agents/coach@v0.6.0 -- coach codesignal --format json \
  --base <resolved-base> --scope production --project-config <detected-path>
```

Branch mode: same flags with `--baseline` instead of `--base`. Do
not combine `--base` and `--baseline`.

Add `--project-language typescript` when the config or the in-scope
set is TypeScript **and** `--help` lists that flag.

Invalid config (not at the analyzed revision, not JSON, schema
failure): coach exits 2 with `project_config_invalid` and writes no
report. Record the reason and continue to SOLID.

Cycle ≤5, same Stage A/B bar, same regression guard, and same commit
rule as Tier 1 (commit only if guarded Stage-B edits landed). Architecture signals
(`architecture.layer_violation`, `architecture.layer_bypass`,
`schema_version` `"2"`) enter the same classification:

- Stage B if the finding could cause incorrect behavior, a test
  failure, or a misleading result, the file is in scope, and the
  remedy is a production-code change (not a config rewrite).
- Ruling required if the remedy would change a public contract, a
  schema, or layer policy itself.
- Stage A otherwise.

Prefer improving production code over editing or silencing
`project.json`. After onboard, do not rewrite layers to silence
a finding.

Stop Tier 3 when Stage-B is empty after a fresh project scan, or 5
cycles have run, or the project scan cannot execute. After the
tier, Read `.cleanup-loop.md` and Edit the Tier 3 coach section.

## After all coach tiers

Record or reuse the SOLID baseline exactly as `loop-protocol.md`
(Green) says; the three record conditions live there, not here. Then
run SOLID. Do not re-run coach after SOLID in the same invocation.

## State file per tier

Read `.cleanup-loop.md`, then Edit the matching section. Prepare
created the file; never Write over it here.

- Pre-coach check: failed tests, lint pairs (from Prepare).
- Tier 1: commands, Stage-A count, each Stage-B item, holding tests,
  guard results, SHAs.
- Tier 2: detected path, `onboarded <path>`, or `absent`;
  `--check-project` payload / skip reason.
- Tier 3: ran / skipped / invalid, commands, Stage-A/B, holding
  tests, guard results, SHAs.
