# Blind adversarial review — 2026-10-25

## Protocol and stopping condition

The user requested independent adversarial review and corrective action for up to five rounds, stopping when issues were resolved. Two rounds were completed, with two fresh reviewers per round. Each reviewer received only an isolated package snapshot, the existing `skill-reviewer` instructions/checklist, and permission for local deterministic probes. Reviewers had no authoring conversation, previous findings, proposed fixes, other reviewers' outputs, or historical validation reports. Historical reports were deliberately excluded from review snapshots and were not classified as broken resources.

Each reviewer read the new skill and applied its evidence-grounded procedure. Review agents inherited the runtime model with no override; the exact variant and effort were undisclosed. Review was blind to history and findings, not anonymized authorship or double-blind experimental grading. Reviewers could inspect the raw implementation, evaluation contracts and, in round 2, regression tests.

The implementer independently verified actionable findings, corrected them, and gave fresh reviewers a revised snapshot without telling them what changed. The loop stopped at round 2 because both reviewers found no further substantiated defect and the corrective checks passed. This does not establish that the package has no undiscovered weaknesses.

## Round 1

| Finding | Evidence and consequence | Corrective action |
| --- | --- | --- |
| Minor: truncated gzip escapes the diagnostic handler | A truncated archive whose outer manifest hash was refreshed raises uncaught `EOFError`. It still exits 1, so this is a diagnostic defect, not an integrity bypass. A four-byte gzip-header fixture independently reproduced the traceback. | Added `EOFError` to the helper's handled failures. Added public-CLI regression coverage, including a relocated package, changed member bytes with a refreshed outer hash, and an unsafe member path. |
| Minor: routing case does not prove activation | The old question asked which skill should handle review; its two assertions could be satisfied by answering only `skill-reviewer`, without loading any skill or auditing a file. | Replaced it with a real structural-review fixture, requiring trace evidence of the reviewer entrypoint, no engineering-entrypoint load, an actual missing-description finding, and unchanged input. Added a natural authoring control under the same catalog conditions. |

The helper regression suite was run against the preserved pre-fix helper: three tests passed and the truncated-gzip diagnostic test failed as expected. Against the corrected helper, all four passed. The malformed archive now yields a concise `Source verification failed:` diagnostic without a traceback or success output.

The maintenance reference now specifies natural discovery conditions, observable entrypoint loading, positive/near-miss controls, and separation of grading/history files from executor workspaces. No unrelated skill wording was rewritten.

Both initial reviewers found the source account and format summary consistent with the archived originals. Neither reported a blocker or major defect. Their suggestions for broader downstream testing were retained as coverage limits, not promoted into claims of a demonstrated production failure.

## Round 2

Both fresh reviewers returned PASS with no substantiated finding. Both scored frontmatter, description, procedure, progressive loading, resources, and anti-patterns 2/2. They independently verified the 13-source archive, ran the four helper tests with the disposable import root adapted, exercised malformed inputs, and sampled the format/research claims against their originals.

The reviewers did not launch coding-agent sessions or claim runtime discovery coverage. Those checks were performed separately below by the implementer, with graders and prior reports withheld from each executor's workspace.

## Corrective behavioral checks

Four fresh CLI sessions used the new discovery contracts without a slash command, a named skill request, or a preloaded entrypoint. Both skill catalogs were installed; grading assertions and historical reports were absent from execution copies. Each case ran once per client, so these are regression observations rather than reliability estimates.

| Client and case | Observed trace and outcome |
| --- | --- |
| Codex: review-only near-miss | Completed `cat .agents/skills/skill-reviewer/SKILL.md`, read the audit fixture/checklist, reported the missing required `description`, and did not load the engineering entrypoint. Fixture stayed byte-identical. |
| Claude Code: review-only near-miss | `Skill` event selected `skill-reviewer`; subsequent `Read` events inspected the fixture and checklist. Report identified the missing `description`; no engineering-skill activation or fixture mutation occurred. |
| Codex: natural authoring control | Read the engineering entrypoint before authoring, read `runbook.txt` and operational references, and created `output/check-release-notes/SKILL.md`. Artifact preserved config-first discovery, exit-2 repair/rerun, exit-3 stop, and the no-publish rule. |
| Claude Code: natural authoring control | `Skill` event selected `agent-skill-engineering`, followed by runbook/reference reads and creation of the requested skill. The artifact preserved the same required decisions and disclosed that target-project execution was untested. |

All four assertions for each case passed by trace and artifact inspection. Input fixtures were independently compared with their original bytes. Codex CLI was `0.164.0`, model/effort undisclosed; Claude Code was `2.1.301`, usage reported `claude-opus-5-5`, effort undisclosed. No model overrides were applied. Codex used ephemeral sessions and workspace-write; Claude used project-only settings, an empty strict MCP config, no persistence, and allowlisted file/skill tools without a shell. Global/built-in agent knowledge was not asserted absent; the Codex authoring trace also read its built-in skill-creator instructions.

These traces close the specific false-positive grading gap. They do not prove natural activation across arbitrary phrasing, models, budgets, or conflicting skill catalogs.

## Final checks and limits

- All 165 repository tests passed, including the four new CLI regressions in [test_agent_skill_sources.py](../../tests/test_agent_skill_sources.py).
- Source verification passed for all 13 original archived files; the archive and source manifest were unchanged.
- The skill quick validator passed. Full lousy-agents lint passed with zero errors using the repository's CI-equivalent materialized skill tree. Four optional-field warnings remain, with the rationale already recorded in [initial validation](validation.md).
- The lousy-agents MCP instruction analyzer was also used; its structural repository-instruction result is not presented as a skill behavior score.
- Final JSON/resource-link and whitespace checks passed. No commit, publication, or external mutation was performed.

Remaining coverage boundary: authoring tests inspect the generated release-check skill; they do not execute it against a functioning target release project. Such downstream success or recovery is not claimed. Original-source currency, paper publication/license verification, broad trigger reliability and production behavior remain outside these checks.

# Second blind adversarial loop — 2026-10-25

## Protocol

Five rounds, two fresh reviewers per round: one checking fidelity to the archived sources and attacking the checker, one checking usability and functional gaps while applying the `skill-reviewer` checklist. Each round got a newly built snapshot without this file, `validation.md`, earlier findings, or a list of fixes. The implementer reproduced or source-checked each finding before acting on it. The loop ran its maximum of five rounds. Findings shrank from two Blockers/Majors per lens in round 1 to Minors and test-coverage gaps in round 5. The round-5 fixes have not been re-reviewed.

## Findings and corrective actions

| Round | Finding | Action |
| --- | --- | --- |
| 1 | Unlicensed paper redistributed in a public repository, contrary to the skill's own maintenance rule (both reviewers) | Paper removed from the archive; manifest keeps its hash with `"bundled": false`; archive now holds 12 CC-BY-4.0 documentation files |
| 1 | Checker verified a manifest with a cited source dropped, or with an empty file list | Requires schema version 1, a non-empty typed file list, every `source_ids` value and the license path listed, license bundled |
| 1 | No test of the shipped archive; nested-JSON traceback; boolean sizes accepted | In-place shipped-package test, `RecursionError` handled, type checks |
| 1 | README inconsistent with other skills; not in catalogs although `npx skills add` installs it | Install line, section order, separator, `plugin.json`, marketplace and `skills.sh.json` entries |
| 1 | `design.md` cited D-DESCRIPTION for advice the guide does not give | Rewritten to the guide's optimization-loop text |
| 1–2 | Possible routing collision with `skill-reviewer`, whose description also lists fixing | Measured, not changed (see below) |
| 2 | Missing CC-BY attribution in the installed package; undocumented exit 2; unfailable eval assertion; manifest trust anchor undocumented | `NOTICE.md`, license URL, epilog, gradable assertion, documented manifest limit |
| 3 | Eval rubrics shipped inside the skill and linked from `SKILL.md` | Suite moved to `evals/agent-skill-engineering/` |
| 3 | `--external ""` silently ran the full check and reported success; D-BEST coherent-units attribution inverted | `is not None` check with test; citation corrected |
| 4 | `--external` only recognizes the original Markdown copy, but docs implied any obtained copy would verify | Docs state the ledger is the portable account and no canonical locator exists |
| 4 | Round-3 fix contradicted D-EVAL's `evals/evals.json` convention; two citations narrowed or unsupported | Rule re-scoped to "executor gets a copy without grading files"; citations corrected |
| 4–5 | Mutation testing found checker guards with no test | Tests added; each guard was mutated and the mutation was caught |
| 5 | Lifecycle table row missing; stale base64 and bundled-paper wording in docs and evals | Fixed |

## Routing measurements

Real headless Claude Code `2.1.310` sessions ran in disposable workspaces with project-only settings and no MCP servers. Each condition ran 3 times. Model and effort were the CLI defaults, not recorded.

| Catalog | Prompt | Skill activated |
| --- | --- | --- |
| this skill + skill-reviewer (unmodified) | fix a skill that never triggers | agent-skill-engineering 3/3; description edited, procedure intact |
| same | review-only audit | skill-reviewer 3/3; fixture unchanged |
| + Anthropic skill-creator | runbook to new skill | agent-skill-engineering 3/3 |
| + Anthropic skill-creator | fix a skill that never triggers | no Skill-tool activation; skill-creator files read and its eval scripts run, 3/3 |

`skill-reviewer`'s description was left unchanged: the overlap did not cause misrouting between the two repository skills. The skill-creator preference for repair prompts is a documented catalog limitation; both skills are legitimate handlers. Three runs per condition is not a reliability estimate.

## Limits

The `validation.md` and first-loop statements about a 13-file archive describe the earlier package. R1 claims can no longer be source-checked from the package. Downstream behavior of generated skills remains untested.

# Third blind adversarial loop — 2026-10-25

## Protocol

Three more rounds (6–8) were run with the same two lenses and sanitization as the second loop. Rounds 7 and 8 also had the usability reviewer install the skill alone into an empty project and work through its procedure: authoring in round 7, and in round 8 a refinement of a toy skill with a planted defect. The fidelity reviewer in round 8 ran the CLI behavior the references describe. Each finding was reproduced or source-checked before any change was made.

## Findings and corrective actions

| Round | Finding | Action |
| --- | --- | --- |
| 6 | Six checker guards had no test (e.g. `schema_version: 2` verified under v1 rules) | Tests for unsupported versions, string `bundled`, negative size, malformed digests, non-string path, `files` as a mapping |
| 6 | `design.md` placed local scope reasoning under a D-BEST citation; `implementation.md` cited D-SCRIPTS for D-BEST/D-EVAL advice | Local inference labeled; citations corrected |
| 6 | `plugin.json` declared only BSD-2-Clause although CC-BY-4.0 files ship | `BSD-2-Clause AND CC-BY-4.0` |
| 6 | "User-supplied" paper wording misleads after a downstream install (noted, not raised) | Says the skill's original author supplied it |
| 7 | D-DESCRIPTION's sample detector reads `.messages` from `claude -p --output-format json`, which Claude Code 2.1.310 does not emit, so every query scores as untriggered | `maintenance.md` says to confirm the detector on a known activation and gives the stream-json `Skill` tool_use check |
| 7 | Root `lint --skills` prints "No skill(s) found" and passes, so following "run the required checks" gives a false green here | `implementation.md` says to lint a copy in a real `.github/skills/` and treat that output as an unrun check |
| 7 | "Skills supply instructions, not new tool permissions" contradicted D-SPEC's `allowed-tools` | Reworded as not portable, citing D-SPEC and D-CLIENT |
| 7 | D-EVAL's no-leftover-state guidance labeled local practice | Attributed to D-EVAL |
| 8 | `--external` skipping manifest validation, an uncompressed tar, and a 65-character digest on an unbundled entry all left the tests green | Tests added; the round-8 harness's 32 mutants are all caught |

Round 8's usability reviewer reported no findings. The planted defect, a rule kept only in an unread reference, reproduced 3/3 on the previous version; inlining the rule, as the skill's refinement table directs, gave 3/3 correct with a 2/2 boundary case. Both round-8 reviewers confirmed the stream-json detector and the lint behavior against Claude Code 2.1.310 and the current CLI.

## Limits

The round-8 test additions were checked by re-running that round's mutation harness, not by a further blind review. The round-8 refinement walk was a single reviewer's run on toy fixtures, with three runs per condition.

# Fourth blind adversarial loop — 2026-10-25

Rounds 9–11 used the same sanitization, with new lenses: real headless sessions in an unrelated project (9), authority and prompt injection plus real `codex exec` runs (10), and over-correction on legitimate agent runbooks (11). No nested session used a permission-bypass flag except two round-9 authoring runs, which a reviewer started with `bypassPermissions` inside scratch directories.

| Round | Finding | Action and re-test |
| --- | --- | --- |
| 9 | Empty `license_archive_path` rejection untested | Test added; mutant killed |
| 9 | Trap prompt led to `find /` for the unbundled paper (2/2) | Check only a user-supplied copy; re-test 0/3 scans, 3/3 still refused the false claim |
| 10 | Generated skills deferred to an injected runbook (3/5) and rarely told the user (1/5) | Authority item 4 extended; re-test 0/3 deferred, 3/3 told |
| 10 | Codex sandbox refused `.agents/` writes; one run made unrequested `AGENTS.md`/runbook edits | Staging-path rule in `implementation.md`; Codex re-test 2/2 staged and reported, no extra edits |
| 11 | Round-10 wording read as stripping legitimate agent-directed procedure; agents overrode it 3/3 | Narrowed to text that directs the authoring agent; re-test kept every runbook gate 3/3 with no disclaimers; hostile line dropped 5/5, disclosed 4/5 |
| 11 | Behavior tests of side-effecting skills used a fixed shared path or the live repo | Stubbed disposable copy in a unique directory, else report not run |
| 11 | `.github/skills` link omitted; lint copy location ambiguous | All three links listed; lint copy outside the repository |

Limits: round-11 fixes were re-tested in small batches, not re-reviewed blind; one of five mixed-runbook runs dropped the hostile line without telling the user.

# Fifth blind adversarial loop — 2026-10-25

Rounds 12–14 kept the sanitization and two lenses per round, and moved to unexercised tasks: a maintainer refreshing the pinned documentation (12, 14), running this suite literally as its protocol says (12, 13), and fresh full passes including repo policy and CI portability (13, 14). Executors in rounds 13–14 ran in `mktemp -d` workspaces outside the scratchpad, without permission-bypass flags.

| Round | Finding | Action and re-test |
| --- | --- | --- |
| 12 | No reproducible archive rebuild; a refresh could drop the license and pass; refresh fields and NOTICE commit untracked; dropped sources could leave citations | `scripts/build_archive.py` (reproduces the shipped archive byte for byte); checker requires `license_archive_path` when a license is declared; refresh steps list every field; tests pin the NOTICE commit and that every cited ID exists |
| 12 | Suite protocol let executors write into the grader's tree; output directory unnamed; inline skill fixture; source-recovery assertions graded tool availability | Executors start outside grading trees; output named; skill fixture moved to `fixture_files`; blocked steps graded as environment-blocked; assertion added for reporting only observed checker output |
| 13 | Write rule failed every Claude Code case on harness state; shell reads uncounted | Rule judged from executor tool calls; shell reads count |
| 13 | `build_archive.py` followed `../`, absolute paths and symlinks | Refused, with tests; guard mutants killed |
| 13 | research-overclaim A6 missed in 1/2 runs (production transfer limit unstated) | Not changed: `evidence.md` already states it and was read; recorded as residual |
| 14 | Real refresh runs (3/3 correct) left staged archives in the package or repo; `working_tree_clean` undefined | Stage outside the repository; field defined; test that `provenance/` holds only the manifest and archive |
| 14 | Byte-for-byte rebuild test failed under zlib-ng; builder accepted empty, duplicate, case-colliding manifests and output inside the source tree; one-script wording | Test compares tar bytes everywhere and the gzip hash under stock zlib (passes on Fedora 41 zlib-ng and Ubuntu 24.04); builder refuses those inputs; wording updated |

Limits: round-14 fixes were checked by tests, containers and mutation, not a further blind review. A refresh that adds or drops a source, or changes the license file, has not been exercised by a real agent.

# Review scope change — 2026-10-25

The maintainer's intent is for this skill to help implement, update, and review skills, complementing `skill-reviewer` rather than routing all review away. The description, "When to use", a new "Reviewing a skill" section, Output, README, plugin and marketplace descriptions were updated; `skill-reviewer` was not changed. Purely structural or lint review stays with `skill-reviewer`, so `routing-near-miss` is unchanged; `behavioral-review` was added.

Real headless Claude Code 2.1.310 sessions, both skills installed, a toy `changelog-writer` skill with an unauthorized publish step, a missing script, and an unsupported "3x under 50 lines" claim; 3 runs per cell, `mktemp -d` workspaces, read-only tools:

| Prompt | Before | After |
| --- | --- | --- |
| Structural/frontmatter defects only | skill-reviewer 3/3 | skill-reviewer 3/3 |
| "Will it behave as claimed, are its claims backed up?" | skill-reviewer only 3/3 | agent-skill-engineering 3/3, with skill-reviewer loaded or read 3/3 |
| "Tell me what's wrong with it" | skill-reviewer only 3/3 | skill-reviewer only 3/3 |

Both versions found the three planted defects in every behavioral run. After the change, behavioral reviews stated the skill was not run and had no evals (3/3 vs 0/3) and checked the claim against `evidence.md`; they took 9–12 turns instead of 5–6. Files were unchanged in all 18 runs. Three runs per cell is a direction, not a rate.
