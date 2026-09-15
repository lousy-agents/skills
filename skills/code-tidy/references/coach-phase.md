# Coach phase

Driver of the outer pass. Runs **before** SOLID. Load this after
Prepare. Baseline for SOLID is recorded only after every coach tier.

Coach has no Stage A/B. Classification is ours.

## Invoke

Portable default:

```bash
mise exec github:lousy-agents/coach -- coach codesignal --format json <args>
```

Source-build **only** when `./cmd/coach` exists in cwd:

```bash
scratch="$(mktemp)"
mise exec -- go build -o "$scratch" ./cmd/coach
"$scratch" codesignal --format json <args>
rm -f "$scratch"
```

Delete the scratch binary on every exit path. Do not call
`go build ./cmd/coach` in a repo that is not coach.

Read `<binary> codesignal --help` once per invocation. Do not invent
flags. Bind every flag you add to that help text.

## Skip, do not fail

Read `.cleanup-loop.md` if it exists, then Edit in
`coach: skipped (<reason>)`. Write only when the file is missing.
Continue to SOLID when:

- no Go/TS/TSX file is in the scope list
- codesignal cannot start after mise is present
- exit 2 for unsupported language or a TypeScript scan that cannot
  resolve a compiler / host Node

Missing `mise` is still a hard blocker for the **whole** skill.

Do **not** run `--suggest-project-config` or `--prepare-compiler`
unless the user explicitly asked. Both are interactive or
candidate-only; this skill does not author architecture policy.

`--baseline` (whole-repo) only when the user asked to tidy the whole
repo. Default remains `--base <resolved-base>`.

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
- Stage B whose only fix changes a public contract, a schema, or
  layer policy → Ruling required, do not fix.
- Out-of-scope Stage-B paths → do not edit. List them Stage A-only
  with reason `out of scope`.

## Tier 1 — simple scan loop

No `--project-config`. This tier must run even when a project config
exists, so architecture policy never hides a simple finding.

```bash
mise exec github:lousy-agents/coach -- coach codesignal --format json \
  --base <resolved-base> --scope production
```

Also run `--scope all` when the production scan's
`summary.files_analyzed` is 0, or the user asked for all. A tests-only
diff often analyzes 0 production files; `--scope all` is how coach
sees the test files. If `--scope all` is also 0, record
`coach: no analyzable files in diff` and continue to SOLID. Do
**not** fall through to `--baseline`. SOLID still tidies test files
that are in the git scope even when coach `--scope production`
excluded them (`coverage.excluded` reason `test_only`).

`--project-language` without `--project-config` is a silent no-op on
a scan (coach default language is `go`). Do not add it in Tier 1
unless `--help` shows a reason to. File-local rules still fire on
Go/TS/TSX paths from the diff.

Cycle ≤5:

`resolve-binary → scan-set → classify Stage A then B → edit in-scope Stage-B paths → commit only if those edits landed → same scan-set`

Do not commit a no-op cycle. Stop Tier 1 when Stage-B is empty after
a fresh simple scan, or 5 cycles have run, or the simple scan cannot
execute. Leftover Stage-B after the cap does not skip SOLID — list
each leftover under `questions`, then continue. After the tier,
Read `.cleanup-loop.md` and Edit the Tier 1 coach section.

Git during this phase: same as the cleanup loop (commit only, trailer,
no push).

## Tier 2 — detect a committed project config

Detect only. Do not write a config.

Detection, in order, against the **analyzed revision** (`HEAD` after
Tier 1 commits), not an uncommitted worktree file:

1. A path the user named in the invocation, if
   `git cat-file -e "HEAD:<path>"` succeeds.
2. `git cat-file -e HEAD:project.json`.
3. A repository-relative path already recorded in project
   instructions / CI / README as the coach `--project-config` file,
   if that blob exists at `HEAD`.

If none exist, Read `.cleanup-loop.md` if it exists, then Edit in
`coach: project-config absent; tier 3 skipped`. Write only when the
file is missing. Then go to the SOLID phase.

`--check-project --project-language typescript` is a **readiness**
probe, not a scan-fix loop. If the repo is TS-heavy it may run once
as an informational note in the state file. Exit 0 ≠ clean. It is
not a gate and it is not Tier 3.

The payload is a readiness object (`status`, `checks`, `gaps`,
`next_actions`), not a scan report. It has no `signals` array. Do
not classify Stage A/B from it. Do not execute `next_actions`
(`prepare_compiler`, `author_policy`) — those are how an unattended
run would author a config or launch an interactive compiler setup.
Scan success is independent of check-project gaps such as
`policy_missing` or `typescript_version_mismatch`.

```bash
mise exec github:lousy-agents/coach -- coach codesignal --format json \
  --baseline --check-project --project-language typescript
```

`--check-project` requires `--baseline` and cannot combine with
`--base`. Only run it when `--help` lists the flag.

## Tier 3 — project scan loop

Only if Tier 2 found a committed config.

```bash
mise exec github:lousy-agents/coach -- coach codesignal --format json \
  --base <resolved-base> --scope production --project-config <detected-path>
```

Add `--project-language typescript` when the config or the in-scope
set is TypeScript **and** `--help` lists that flag.

Invalid config (not at the analyzed revision, not JSON, schema
failure): coach exits 2 with `project_config_invalid` and writes no
report. Record the reason and continue to SOLID.

Cycle ≤5, same Stage A/B bar and commit rule as Tier 1 (commit only
if Stage-B edits landed). Architecture signals
(`architecture.layer_violation`, `architecture.layer_bypass`,
`schema_version` `"2"`) enter the same classification:

- Stage B if the finding could cause incorrect behavior, a test
  failure, or a misleading result, the file is in scope, and the
  remedy is a production-code change (not a config rewrite).
- Ruling required if the remedy would change a public contract, a
  schema, or layer policy itself.
- Stage A otherwise.

Prefer improving production code over editing or silencing
`project.json`. This skill does not author architecture policy.

Stop Tier 3 when Stage-B is empty after a fresh project scan, or 5
cycles have run, or the project scan cannot execute. After the
tier, Read `.cleanup-loop.md` and Edit the Tier 3 coach section.

## After all coach tiers

Record the pass-1 test/lint baseline on the post-coach tree. Then run
SOLID. Do not re-run coach after SOLID in the same invocation.

## State file per tier

Read `.cleanup-loop.md`, then Edit the matching section. Write only
when the file is missing.

- Tier 1: commands, Stage-A count, each Stage-B item, SHAs.
- Tier 2: detected path or `absent`; whether `--check-project` ran.
- Tier 3: ran / skipped / invalid, commands, Stage-A/B, SHAs.
