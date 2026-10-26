# Evidence ledger

This ledger separates source claims from engineering inferences. Source IDs resolve through `provenance/sources.json`. Documentation originals are bundled; the paper is not, because its redistribution license is unknown, so this ledger is the package's only account of it. The manifest pins the hash of the original Markdown copy, which `scripts/check_sources.py --external` can recognize; no canonical locator was available, and other copies or formats will not match. The paper is a Markdown copy the skill's original author supplied, not an independently verified publication record. Its supplement and replication package were not examined during grounding.

## Authority map

| Source | Role | Boundary |
| --- | --- | --- |
| D-SPEC | Agent Skills format requirements | Explanatory guides and implementations add no normative format rules |
| D-BEST | Authoring guidance | Recommended techniques, not mandatory headings or blanket rewrite authority |
| D-DESCRIPTION | Description testing guidance | Counts, splits, and thresholds are suggested starting values |
| D-EVAL | Output evaluation guidance | Example schemas and procedures; empirical benefit still needs testing |
| D-SCRIPTS | Script interface guidance | Runtime availability and permissions remain harness-dependent |
| D-CLIENT | Client implementation guidance | Discovery, collisions, leniency, compaction, trust, and optional delegation are implementation choices |
| D-QUICKSTART, D-HOME | Tutorial and conceptual overview | Examples do not extend the specification |
| R1 | Empirical study of skill revisions | Restricted rules, tasks, models, and scaffold; not universal prescriptions |

D-CLIENT recommends preserving skill context through compaction and deduplicating activation. A skill author cannot assume the active harness implements either. Likewise, a tutorial's dice command or a guide's example of permission allowlisting does not establish current runtime behavior.

## R1: Agent Skill Evolution: How Revisions Affect Coding Agents

Authors: Jiajie Wang, Yutong Zhao, Tianlin Li, Huashan Chen, Jinfu Chen, Kebin Peng, and Sen He. The skill's original author supplied a local Markdown copy as recent research; it is not the user of an installed copy. Venue, publication date, peer-review status, and redistribution license are not established by the supplied file.

### Design and population

- Corpus: 3,159 skills with histories in 856 repositories; 2,608 first/last pairs differ. A "revision" spans first to last observed content, often multiple commits, not necessarily one isolated edit. [sections 1, 3.1]
- Probes: 396 retained added-directive probes from 200 repositories; 300 shared probes for 16 open models, smaller subsets for closed models and controls. Directives name concrete backticked commands, paths, flags, or identifiers. Only 17% of candidates survive filtering; prohibitions, conditional rules, and permission guardrails are underrepresented. [sections 3.2, 3.4, 7.1]
- Conditions: **none** still includes the skill name and description; **old** and **new** also include the respective body. It is a body comparison, not absence of all skill metadata. [section 3.4]
- Models answer without reasoning modes. Executing agents use mini-SWE-agent with a 12-step, networkless sandbox and 80 tasks. These are not production Codex/Claude Code trials. [section 3.3; section 5.2.2]
- Statistics use paired probes and repository-clustered bootstrap intervals. Small sample negative findings are not equivalence proofs. [sections 3.4, 7.1]

### Findings and allowable interpretations

| ID | Reported result | Qualification | Engineering implication (inference unless identified as author advice) |
| --- | --- | --- | --- |
| R1-A | 55% of differing pairs change a rule or procedure; matched skill-revision commits touch harness config 4.5 percentage points more often | Classifier misses many constraints/conditional lines; co-change is association | Inspect coupled references/configuration when diagnosing drift; do not change them automatically [section 4] |
| R1-B | Mean added-rule single-answer compliance gain about +0.41 across 16 open models | Literal identifier grader includes information exposure; tasks constructed to need the rule | Use this as a conditional behavior signal, not a task-success estimate [section 5.1.1] |
| R1-C | New-token cases gain +0.51 to +0.66; already-present cases gain about +0.08 pooled | Higher baseline leaves less headroom; some "added" rules restate existing ones | Prioritize testing genuinely missing operational information, not redundant wording [section 5.1.3] |
| R1-D | Adding just the directive gives about two thirds of the full revision effect; stating a rule beats token-only exposure by +0.15 | Controls overlap because the rule contains its token; effects cannot be exactly decomposed | Test a specific procedural instruction rather than assuming keyword presence suffices [section 5.1.2] |
| R1-E | Four sandbox agents gain +0.23 action rate on average, 95% CI [+0.15, +0.31] | Action is checked from operations/artifacts, not final response text | Verify actions separately from language compliance [section 5.2.2] |
| R1-F | Three human-judged agents gain +0.10 final correctness pooled, CI [+0.04, +0.17] | Two Qwen agents gain +0.13 pooled; Sonnet 4.5 +0.06, CI [-0.06, +0.18], inconclusive; Devstral not human judged | Keep correctness separate from action; do not promise each agent a significant gain [section 5.2.3] |
| R1-G | On-demand loading retains about 51% of four-agent action gain; three open models about 38%; Sonnet +0.19 under both modes | Reads show only first/last 2,000 characters, hiding rules in some opened files | Diagnose activation, displayed content, and action independently; this does not prove progressive disclosure is harmful [sections 5.2.4–5.2.5] |
| R1-H | Deletion lowers compliance by 0.27–0.33 across eight models | Rule replacement or obsolescence can make reduced compliance desirable | Author advice: check whether the behavior should persist before deleting [sections 5.1.4, 7.2] |
| R1-I | No significant generation interaction in the main corrected tests | Data-derived bound about 0.077; models without reasoning; one new-token subset differs | Do not infer model independence or remove justified runtime adaptation [sections 5.1.5, 7.1] |
| R1-J | Gain falls from 0.424 at low skill occupancy to 0.270 at 75% occupancy; long-context gains also shrink | Usable-input caps, particular models and synthetic histories | Design context budgets for intended runtimes, not a universal optimal line count [sections 5.1.6–5.1.7] |
| R1-K | Added rules cost 18–19% more single-answer input tokens; episode change -2.3% to +3.0%, every interval spans zero | Episode estimates exclude only relatively large increases; fewer steps offset input growth | "No detectable increase" does not mean free; measure complete episodes [section 6] |
| R1-L | Carrying the old body costs 37–57% more episode tokens than name/description only, mean about 50% | Body resent every turn in this scaffold; not a universal billing multiplier | Distinguish carrying cost from revision cost and tokens from money [section 6.2] |
| R1-M | About 20% of rule–model pairs add tokens without detected compliance gain | Five samples; some rules already followed, others ignored | Candidates for controlled removal or rewrite, not automatic deletion [section 6.1.2] |
| R1-N | Estimated 25% of later in-scope commits need a rule, CI 14–40% | Hand-labeled 100 commit–rule pairs, reweighted; not measured natural request traffic | Weight evaluation by applicability; paper's multiplied gains are scenarios, not deployment estimates [section 7.2] |
| R1-O | Irrelevant requests use the added token 2–6 points more often | Six models; small off-target effect compared with needed-rule gains | Include tasks where the rule should not apply [section 5.1.3] |

### Measurement cautions

The string grader has high precision and incomplete recall against human directive-following judgments. Automated artifact checks agree only moderately with human correctness judgments (kappa 0.50–0.55); the authors base their outcome claim on blind human assessment. An answer mentioning a command neither proves it executed nor that the result is right. [sections 3.2, 7.1]

The main corpus excludes repositories above 375 stars because of cloning budgets; a separate high-star set checks some results. Generated probes, selection bias, small closed-model subsets, limited output windows, underpowered Sonnet outcomes, and excluded reasoning modes constrain generalization. Claims about security guardrails require dedicated behavioral evidence; they cannot be inferred from a literal-token benchmark.

## Working synthesis

The documentation and paper support a testable approach: capture non-obvious knowledge, activate it precisely, deliver it economically, verify action and outcome, then retain only changes supported by evidence. This synthesis is our engineering recommendation. It neither changes the format nor authorizes cosmetic rewrites of tuned repository skills.

Documentation retention is lossless at the byte level; the paper is pinned only by hash. This ledger is selective. Consult the archive or a hash-verified paper copy for omitted details and verify fresh versions when currency matters; identical model behavior across sessions cannot be guaranteed.
