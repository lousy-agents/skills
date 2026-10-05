---
name: to-ears
description: "Draft, convert, review, or derive tests from requirements in EARS (Easy Approach to Requirements Syntax) without inventing behavior. Use when asked to 'write EARS requirements', 'convert these requirements to EARS', 'rewrite acceptance criteria in EARS', 'review my EARS criteria', 'is this requirement testable', 'derive tests from these requirements', or when feature-to-plan, issue-refine-loop, or spec-auditor needs acceptance criteria drafted or reviewed. Do NOT use to author a whole spec or new GitHub issue (use feature-to-plan), to audit a whole spec (use spec-auditor), or to rewrite an existing issue in place (use issue-refine-loop)."
argument-hint: "Requirement text, a file path, or an issue reference; optionally 'review' or 'tests' to pick a mode"
allowed-tools: Read, Grep, Glob, Edit, Write
---

# To EARS

## Overview

EARS is a small set of sentence structures for natural-language requirements. Each structure makes visible the conditions, triggers, states, feature applicability, and required response. This skill turns source material into EARS criteria, reviews existing criteria, and derives tests from agreed criteria.

**EARS is a syntax aid.** A well-formed EARS sentence can still be vague, incomplete, contradictory, untestable, or an implementation prescription. This skill reviews meaning as well as form. It never fills a gap with plausible behavior to make a sentence look complete.

This skill is the canonical home of the EARS method in this repository. Other skills (`feature-to-plan`, `issue-refine-loop`, `spec-auditor`) delegate to it when it is installed, and each keeps a verbatim copy of the compact **EARS Contract** so it still works without this skill.

References:

- [`references/ears-contract.md`](./references/ears-contract.md) — the canonical contract: the five patterns and their combinations, the criterion line format, provenance tags, binding rules, the open-question format, verification rules, and the vague-term list. **Load first in every mode.**
- [`references/authoring.md`](./references/authoring.md) — choosing a pattern, combining conditions, writing a good requirement, the omission sweep, review checklists, and failure modes. **Load for Draft and Review.**
- [`references/test-derivation.md`](./references/test-derivation.md) — oracles, mapping abstract terms to interfaces, pattern prompts, kinds of evidence, and the task Verification format. **Load for Test map, or when a calling skill needs task verification.**
- [`references/evidence-limits.md`](./references/evidence-limits.md) — what the 2009 and 2025 studies show and do not show. **Load before claiming what EARS achieved.**

## When to Use

- Converting prose requirements, a PRD paragraph, or issue acceptance criteria into EARS
- Reviewing existing EARS criteria for form, meaning, and testability
- Deriving requirement-based tests, or task verification items, from agreed EARS criteria
- Another skill delegates criterion drafting or review (Embedded mode)

**Do NOT use when:**

- The user wants a whole spec file or a new GitHub issue. Use `feature-to-plan`, which calls this skill for its criteria.
- The user wants a whole spec audited for contradictions, scope, and architecture fit. Use `spec-auditor`, which may call this skill for its acceptance-criteria pass.
- The user wants an existing issue rewritten in place. Use `issue-refine-loop`.
- The task is code-level test generation. Use `rugged-evil-tester`, `go-testable-design`, or `mutation-hunter`. This skill stops at a reviewable test mapping.

## Hard Constraints

1. **Separate facts from interpretation.** Every criterion carries a provenance tag: `[src: …]`, `[inferred: OQ-n]`, an inline `[TBD … — OQ-n]`, or a rare `[non-EARS: …]`. Never present an inference as a quotation of the source.
2. **Never invent.** Add no threshold, unit, trigger, precondition, exclusion, recipient, or behavior that neither the source nor the user established. If making a criterion testable needs a value nobody chose, the fix is a `[TBD …]` marker plus an open question, never a plausible number.
3. **Code is not intent.** Existing code shows what the system does now, not what it is required to do.
4. **Tests come only from agreed criteria.** An `[inferred …]` criterion gets a test only as a draft labeled with its OQ. A `[TBD …]` clause is a coverage gap, never a test.
5. **Never overclaim.** Do not say EARS found all omissions, proved safety, resolved conflicts, established traceability, or guaranteed coverage.

## Modes

Pick the mode from the request. If the request is unclear, Draft is the default when the input is prose, and Review is the default when the input is already EARS.

| Mode | Input | Output |
| --- | --- | --- |
| **Draft** | Prose requirements, a PRD, an issue, or a conversation | Criteria in contract format, open questions, review findings |
| **Review** | Existing criteria (EARS or not) | Findings per criterion, plus a corrected draft that marks every unresolved clause |
| **Test map** | Agreed criteria, plus interface or code context | Mapping from criterion to oracle to cases, and the coverage gaps |
| **Embedded** | A calling skill's story, source text, and system names | Only the criterion lines, the open-question entries, and one omission-sweep line per story. The caller owns the artifact, the gates, the section layout, and the numbering of stories. |

## Procedure

### 1. Establish context

Before rewriting anything, identify each of these, and record which ones you could not determine:

- **The system boundary and the named responding system(s) or component(s).** Use the agreed names consistently. In a multi-component feature, name the component that owns each response; do not write "the system" for all of them.
- **Actors and event sources.** Who or what produces each trigger.
- **Sources and their identifiers.** Keep the identifiers, and quote or cite the source location for each requirement.
- **Definitions, glossary, interfaces, constraints, product variants.**
- **Requirement level.** Stakeholder, system, or component. EARS was aimed mainly at high-level stakeholder requirements, so check the fit at lower levels.
- **Verification context.** How these criteria will be checked.

### 2. Decompose and classify the source

Separate explicit requirements from implied ones, design guidance, verification statements, rationale, and informative text. For a compound passage, list its distinct obligations, conditions, exceptions, and unwanted scenarios before writing any EARS. Note the source location of each item.

### 3. Sweep for omissions

Run the omission sweep in [`authoring.md`](./references/authoring.md#omission-sweep). Give every relevant prompt a disposition: **covered**, **confirmed by the user**, **out of scope** (with a reason), or **unresolved** (an OQ). The sweep prompts investigation. It is not permission to write criteria.

### 4. Choose a pattern and draft

Identify the response first. Then classify what activates it, using the contract table and [`authoring.md`](./references/authoring.md#choosing-a-pattern). Write one obligation per criterion with a consistent system name, using the contract's criterion line format and provenance tags.

When two patterns fit, record a one-line rationale in the notes.

When no pattern fits honestly, use `[non-EARS: <reason>]`, and do not distort the requirement to fit a template.

### 5. Review meaning

Apply the Form, Meaning, and Intent checklists in [`authoring.md`](./references/authoring.md#review-checklists) to every criterion. Fix form problems directly. For meaning and intent problems: mark the problem, open an OQ, and change the provenance tag. **Do not resolve them by inventing.**

### 6. Validate and trace

- **When the user is available:** ask focused, small-choice questions about every `[inferred …]` criterion and every Blocker or High OQ. Retag each confirmed criterion `[src: user]`.
- **When the user is not available** (unattended or embedded runs): leave the tags and OQs as they are, and state the effect of each unresolved item on the criteria and tests.

Link every criterion to its source, and later to its tests.

### 7. Map tests (Test map mode, or on request)

Follow [`test-derivation.md`](./references/test-derivation.md): oracle, mapping, cases, combinations, setup/action/expected, two-way trace, adequacy. Label each item as requirement-based (with its criterion IDs), `(exploratory)`, `(structural)`, or `(gate)`.

## Output Format

For standalone runs, return these sections:

1. **Context and sources** — the system boundary, named systems, source references, definitions used, and anything you could not determine.
2. **Criteria** — contract-format lines grouped by story or requirement group, with a one-line rationale wherever the pattern choice is debatable.
3. **Open questions and assumptions** — contract-format OQ entries, with severity, the affected criteria, and who must decide.
4. **Review findings** — ambiguity, vagueness, compound behavior, omissions to investigate, conflicts, implementation prescriptions, and verification concerns.
5. **Test mapping** (Test map mode) — criterion ID, abstract conditions and response, the interface mapping, test cases, expected results, and coverage gaps.
6. **Evidence limits** — which items the source establishes, which you inferred, and which you propose.

For Embedded runs, return only the criterion lines, the OQ entries, and the omission-sweep summary. The calling skill places them.

If the source does not support a complete requirement, give the best faithful draft, mark the unresolved clause with `[TBD …]`, and name the exact decision required. Never silently convert uncertainty into a requirement.

## Gotchas

- **A source word is not a pattern.** A source "if" is often an event-driven trigger, and a source "when" can describe a state. Classify the behavior, not the word.
- **A flag is a state, not a feature.** A feature flag that can flip at runtime is a `While` state. `Where` is for what ships in a variant.
- **"Make it testable" is the moment fabrication happens.** A reviewer who asks for a number is asking for a decision, so route the request to an OQ.
- **Positive rules do not close themselves.** An allow rule leaves the deny path unspecified until someone specifies it.
- **IDs are load-bearing downstream.** `plan-to-graph` copies task bodies verbatim into child issues, so a task that cites `AC-2.3` must still make sense there. Never renumber an ID after it has been cited.
- **`spec-auditor`'s lint enforces this contract mechanically.** It recognizes the criterion ID prefix, the `During` keyword, `[non-EARS: …]` exemptions, and the vague-term list, and it flags `[TBD …]` markers as unresolved on purpose. A flagged TBD is correct output, not a lint problem to engineer around.
