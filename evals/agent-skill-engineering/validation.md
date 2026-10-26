# Initial validation — 2026-10-25

## Scope and environment

This report records observed implementation checks, not a claim of universal expertise or statistical equivalence. Task contracts are in `evals/agent-skill-engineering/evals.json` (originally `skills/agent-skill-engineering/evals/evals.json`). Runs used separate disposable directories outside the source repository, without the authoring conversation, baseline outputs, grading assertions, or access to sibling eval workspaces. No production deployment command was executed.

- Codex CLI: `0.164.0`; selected model and effort undisclosed by the captured event stream. Sessions used `exec --ignore-user-config --ephemeral --skip-git-repo-check`, workspace-write for authoring and read-only for assessment. No model override.
- Claude Code: `2.1.301`; usage metadata reported `claude-opus-5-5`; effort undisclosed. Sessions used project-only settings, an empty strict MCP configuration, no session persistence, and allowlisted file/skill tools. Shell execution was unavailable in these runs. No model override.
- Skill invocation was explicit. These checks do not measure natural triggering accuracy or name-collision behavior.
- Ten task sessions and one independent `skill-reviewer` session completed successfully. Each configuration was run once; results do not establish reliability rates. The no-skill controls lacked this new skill but were not a guarantee of zero built-in or user-level agent knowledge.
- Raw transcripts and generated artifacts were inspected in a temporary validation workspace. The cases, evidence excerpts, grading conclusions, and limits are retained here; full transcripts are not bundled.

## Observed behavioral results

| Task | Configurations | Assessment and evidence |
| --- | --- | --- |
| Create from runbook | Codex with skill; Codex without; Claude with; Claude without | All four produced a real `output/check-release-notes/SKILL.md` with matching required metadata, config-first path discovery, the checker command, distinct exit-2/exit-3 handling, and no publish permission. All five case assertions passed in each run by artifact inspection. No measurable improvement over baseline on this simple task. |
| Refine planning/deployment failure | Codex with skill; Claude with skill | Both preserved the supplied baseline and changed the procedure to stop after a plan, while retaining an authorized execution branch. Both provided boundary coverage and an authorized-deployment control as a proposed test, explicitly unrun. All five assertions passed. The supplied failure was captured, not reproduced against a deployment harness. |
| Correct research overclaims | Codex with skill; Claude with skill | Both distinguished +0.41 single-answer compliance, +0.23 action, and +0.10 human-judged correctness; qualified applicability and metadata-only baseline; identified truncated delivery; rejected free revisions, automatic deletion from five trials, and extrapolation to reasoning modes. Both proposed controlled experiments. All seven assertions passed by response/artifact assessment; the Codex command trace shows the evidence reference being read. |
| Source-grounded research comparator | Codex with original paper and documentation, without the distilled skill | Reached the same substantive corrections on all six domain assertions. It additionally reported single-answer total-token changes and detailed exposure rates from the original. This is one agreement case, not proof that every source detail survived distillation. The entrypoint-read assertion does not apply to this comparator. |
| Recover missing sibling sources | Claude with skill; file tools only | The stream trace shows reads of the manifest, evidence, helper, design, and maintenance resources. It located the bundled archive without sibling paths, described integrity checking accurately, distinguished recommendations from format rules, and disclosed that it could not run the checker. All five assertions passed. It correctly noticed the then-pending validation report; that link is now populated by this file. |

Evidence excerpts:

- Codex author's artifact: "Exit 3: report the invalid release configuration ... then stop. Do not guess a replacement, edit the configuration, or retry with an invented notes path."
- Codex refinement: "For a planning-only request, draft the deployment plan and stop; do not run deployment commands." It left the description and unrelated config-read step intact.
- Claude refinement's test record: "Status: planned, not run." Its proposed fixture included instruction-like deployment text inside config and a local invocation marker to distinguish actions from final answers.
- Claude research assessment: "That means no large increase was detected, not that the cost is zero." It separately retained the approximate 50% carrying cost.
- Codex research assessment: "The 'none' condition still supplied the skill name and description."
- Claude recovery: "A passing check shows the files match what was recorded when the skill was built. It doesn't show that the recorded files were authentic in the first place, or that their content is correct."

The routing-near-miss contract remains unrun. Generated release-check skills were inspected but not exercised against a real release project; the authoring fixture explicitly supplied none. Refinement tests of the generated deployment skill remain proposed. These limits do not turn artifact-level authoring evidence into downstream production validation.

## Source integrity and mechanical checks

- The archive contains 13 exact source files. Every manifest hash was independently compared with its original local file. Original Markdown, embedded paper figures, documentation configuration, and the documentation license are retained unchanged.
- `python3 scripts/check_sources.py` passed from the source package and a relocated copy with a different working directory.
- Negative checks rejected an altered archive, missing archive, malformed manifest JSON, changed member content with a recomputed outer archive hash, and an unsafe `../outside` member with a recomputed outer hash. Each exited 1 with an actionable diagnostic. No extraction was performed by the checker.
- `skill-creator/scripts/quick_validate.py` passed using an isolated `uv run --with pyyaml` environment. The system Python invocation initially lacked PyYAML; no global package install was performed.
- Full `@lousy-agents/cli lint` passed with zero errors. As CI documents, discovery ignores this repository's skill-directory symlinks, so checks were also run against a disposable copy materializing all 17 skills under `.github/skills`.
- New-skill warnings for missing `allowed-tools` and `argument-hint` were reviewed and retained: a client-specific hint is unnecessary, and tool allowlisting would impose client-specific permission semantics on an otherwise portable workflow. Both fields are optional. Existing missing-`allowed-tools` warnings for `customer-strategy-forge` and `optimize-prompt-loop` were left unchanged.
- The lousy-agents MCP `analyze_instruction_quality` tool was used against canonical repository instructions and a temporary `AGENTS.md` adapter containing the entrypoint. It is an instruction-structure analyzer, not a skill behavior grader or frontmatter validator. Adapter warnings about missing project-policy headings were rejected as inapplicable; inserting those headings would duplicate policy rather than improve this skill. Actual skill frontmatter was checked by the CLI and quick validator.
- Repository script suite: all 161 existing tests passed. JSON parsing, Markdown resource links, and whitespace checks were also checked.

## Skill-reviewer result

An independent Codex session read the existing `skill-reviewer` instructions and checklist, reviewed the new skill/resources, and ran the source-integrity helper. Verdict: **PASS with portability caveats; no confirmed Blocker or Major behavioral defects**.

It scored description, procedure, progressive loading, resources, and anti-patterns 2/2. Its frontmatter caveat came from the review-only staging folder named `target`; the actual installation folder correctly matches `agent-skill-engineering`. Its other minor finding was ambiguity between source-repository facts and destination-repository policy. The final entrypoint and implementation reference now explicitly name the originating `lousy-agents/skills` repository and instruct copied installations to discover destination policy. The final link review confirms the validation-report reference resolves.

## Remaining limits

No implicit-trigger benchmark, repeated reliability study, full knowledge-coverage proof, production integration, or broad model comparison was performed. The paper's publication record, license, and replication package remain unverified. Its archive is retained for the user-requested local grounding; no redistribution grant is inferred and no plugin-marketplace entry was added. The current skill can be used locally in both tested harnesses without claiming those research results were measured in either production client.

## Subsequent adversarial review

The later [blind review loop](adversarial-review.md) records two review rounds, fixes for the helper diagnostic and routing-evaluation gap, four observed natural-discovery runs, and the expanded 165-test suite. The statements above describe the initial implementation checks; the follow-up report supplies the newer coverage and its limits.

## Later package changes

The archive and test counts above predate the [second review loop](adversarial-review.md#second-blind-adversarial-loop--2026-10-25), which removed the paper from the archive (12 files remain) and moved these reports out of the installable skill.
