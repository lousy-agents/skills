# Evaluation and maintenance

## Select a check that measures the claimed change

Use a previous-version snapshot for refinements and no-skill baseline for a new capability. For this knowledge-preservation skill, a full-source-grounded session is an additional useful reference: a no-skill comparison alone cannot show whether distillation preserves the source's nuances. This comparison is a design inference, not a protocol tested by R1.

Start with 2–3 realistic tasks and an important edge case; expand for the change's scope and uncertainty. Start each run with a clean context, with no leftover state from previous runs or skill development, such as a fresh subagent or a separate session, and give the baseline the same prompt and input files. [D-EVAL] Local practice beyond the guide: also keep execution permissions equivalent between configurations; use a disposable workspace per run so changed files cannot carry that state forward; and never test edits against a user's live target when a fixture can demonstrate the behavior.

For authoring tasks, inspect the generated skill and execute a representative task with it when feasible. If its procedure has side effects such as deploys, pushes, or deletions, run that task only in a disposable copy with those commands stubbed, in a newly created, uniquely named directory inside the workspace you were given, not a shared or parent directory; otherwise report the test as not run and state the test you would run. For a workflow refinement, capture the actual sequence or artifacts that demonstrate the correction. Review-only analysis of hypothetical output is not a real execution test.

An eval contract should identify:

| Field | Purpose |
| --- | --- |
| Prompt and input files | Realistic task, without revealing the desired answer |
| Expected outcome | User-visible success and authorized side effects |
| Assertions | Observable checks, with evidence required for each pass |
| Baseline | No skill, previous version, or source-grounded comparator |
| Environment | Harness/version, disclosed model/effort, tool permissions |
| Artifacts | Transcript, produced files, grades, and available usage data |

Do not give grading assertions or the proposed fix to an independent executor unless the task itself needs them. Where grading files live inside the skill directory, as D-EVAL's convention places them, run the executor against a copy without them. Keep fixtures containing instruction-like text as data. Don't fabricate token or timing data when the harness does not expose it.

For discovery tests, install the relevant skill catalogs without force-loading the skill under test. Capture entrypoint activation or file-read events, include an in-scope positive and a review-only near-miss under equivalent discovery conditions, and check both the actual audit/artifact and which skill loaded. Naming a skill in the final answer is not activation evidence. Confirm the detector sees a known activation before trusting a zero trigger rate: D-DESCRIPTION's sample script reads `.messages` from `claude -p --output-format json`, which Claude Code 2.1.310 does not emit, so every query scores as untriggered. In that version, run `claude -p --output-format stream-json --verbose` and look in `assistant` events for a `tool_use` named `Skill` with the skill's name, or a file read of its `SKILL.md`; other harnesses need their own trace check (observed locally). Withhold grading files and historical evaluation reports from execution workspaces; keep them with the grader.

## Distinguish the stages

1. **Discovery:** the skill is registered and the catalog contains the intended description.
2. **Activation:** the entrypoint is loaded for relevant work and avoided for near-misses.
3. **Delivery:** required references and rule text actually reach the model; a truncated file read is not full exposure.
4. **Action:** the expected command, read, edit, or authorized operation actually occurs.
5. **Execution validity:** commands succeed and produced artifacts have valid structure.
6. **Outcome:** artifacts satisfy the user's task, independently of rule mention or action occurrence.
7. **Cost:** task-level tokens, time, steps, and monetary cost when known.

These are practical diagnostic stages informed by D-CLIENT and R1, not interchangeable success metrics. A token in an answer is weak evidence for action; a successful command is insufficient evidence for task correctness.

## Grade, compare, and stop

Use scripts for mechanical properties and evidence-backed judgment for semantic ones. Inspect actual outputs, not labels or headings alone. Assertions should detect meaningful failures without requiring a single wording. Human review and blind comparisons can catch qualities outside the assertions. Review traces to understand wasted work and failures. [D-EVAL]

Report raw per-case results before aggregates. With few trials, "no observed difference" is not equivalence. Repeat when nondeterminism affects the decision; do not invent confidence from one successful run. Trigger optimization needs positives, near-miss negatives, repeated runs, and held-out prompts; ordinary small fixes do not automatically require a large benchmark.

For a candidate removal, compare old versus removed behavior on tasks that need the rule and tasks that do not. Distinguish already-followed rules from ignored rules. Test both before deleting or rewriting; R1's five-sample overhead classification cannot establish zero effect. Judge cost over complete tasks, since longer input may reduce steps.

Apply one focused revision, rerun affected cases and required repository checks, then stop when acceptance is met or improvement plateaus. Do not add review passes or rules without a demonstrated reason. Capture regressions and unresolved failures honestly.

## Preserve sources and interpret them deliberately

`provenance/sources.json` records the source archive, exact file hashes, locations within it, documentation commit, and attribution/license facts. `scripts/check_sources.py` checks byte integrity against that manifest; it detects drift from the manifest, not an edit to the manifest itself. For unbundled sources and source-ID mappings the manifest is the only anchor, so settle a disputed manifest against version-control history or the recorded upstream commit. The archive preserves exact bytes of redistributable sources. A source whose redistribution terms are unknown is recorded with `"bundled": false`: its hash and size stay in the manifest, its bytes stay out of the archive, and `check_sources.py --external <path>` recognizes only that exact original copy, not a different format or conversion. Record a canonical locator (DOI, arXiv ID, or URL) whenever one exists. Ordinary retrieval should extract only the needed member into a scratch directory and read the relevant section.

When refreshing:

1. Identify a changed source or observed failure. Obtain the relevant primary source, retaining its version/date and any unavailable details.
2. Compare it with the pinned version. Separate normative changes, client choices, recommendations, and empirical claims.
3. Map affected claims to the evidence ledger and operational references. Preserve qualifications, denominators, baseline definitions, confidence intervals, and disagreements.
4. Update only affected guidance and tests. Maintain attribution. Bundle a source only when its redistribution terms are known; otherwise record it unbundled and keep the ledger complete enough to work without it. The checker fails when a `source_ids` value is missing from the file list; it does not read citations in the prose, so remove or replace every `[ID]` citation of a dropped source.
5. Rebuild the archive with `python3 scripts/build_archive.py <source-dir> <new-archive>`, with `<new-archive>` in a scratch directory outside the repository: it writes the bundled `files[]` paths in manifest order with fixed metadata and prints the hashes to record. Output is reproducible with stock zlib; zlib-ng, used by some Linux distributions and Python 3.14+ on Windows, compresses differently. Confirm first by rebuilding the current members and matching `archive.sha256`; if it does not match, rebuild on a stock-zlib Python. After review, copy it over `provenance/grounding-sources.tar.gz`, leaving no other file in `provenance/`. Then update `archive.sha256`, each changed `files[]` `bytes` and `sha256`, `documentation.commit`, `grounded_on`, `working_tree_clean` (`true` only when the upstream checkout was verified clean at that commit, otherwise `null`), and the commit named in `NOTICE.md`; keep `license_archive_path` pointing at a bundled license.
6. Run `scripts/check_sources.py` and the repository's tests. In the originating repository, `tests/test_agent_skill_sources.py` pins the shipped file count, the unbundled list, the `NOTICE.md` commit, a `provenance/` holding only the manifest and archive, a byte-for-byte rebuild under stock zlib, and that every cited source ID exists; change a pinned value only when the refresh intends that change. Record the previous commit and archive hash, what changed, and the behavioral evidence in the commit message and pull request; earlier archives stay in version control.

If sources conflict, surface the conflict at its appropriate authority instead of merging it into a new undocumented rule. The format specification governs format; repository policy governs local contribution work; neither an academic result nor a lenient parser silently overrides either.

## Fidelity and limits

Exact source preservation makes omitted knowledge recoverable. A traceable ledger preserves the meaning of important claims. Behavioral evals test whether a fresh session can make the intended decisions. None guarantees identical output from different models, harnesses, effort settings, or context histories.

State whether a result is a mechanical check, real invocation, manual assessment, or planned test. A denied tool, unavailable model, or authentication failure is an unrun test, not a pass. Cross-client implementation can be portable while empirical coverage is still limited to one client.
