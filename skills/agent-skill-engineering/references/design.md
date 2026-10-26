# Design decisions

Source keys below refer to `provenance/sources.json`. D-SPEC defines format; the other D-* guides recommend techniques. R1 is empirical evidence, with limits in `references/evidence.md`.

## Extract expertise rather than inventing it

Start from a real successful task, correction, failure, runbook, schema, API contract, or review history. Capture the non-obvious sequence, inputs, outputs, exceptions, and project facts. Generic advice such as "handle errors appropriately" supplies no recovery action. If the entire task already works reliably without added guidance, first establish what a new skill would contribute. [D-BEST: Start from real expertise; Spending context wisely]

Write down this compact contract before drafting:

| Decision | What to identify |
| --- | --- |
| Outcome | The user's observable result and completion condition |
| Activation | Intents that need this expertise, including indirect phrasing |
| Boundary | Similar tasks that need another capability |
| Added knowledge | A fact, procedure, or invariant the agent otherwise misses |
| Authority | Which actions are authorized and where policy comes from |
| Evidence | Demonstrated failure or supplied domain artifact; assumptions labeled |

This is working analysis, not a mandatory extra document in every generated skill.

## Coherent scope and routing

Treat a skill as a coherent reusable unit, analogous to a function. Too narrow means several skills must load for one task, risking overhead and conflicting instructions; too broad makes precise activation hard. [D-BEST: Design coherent units] By local inference, designing, implementing, and maintaining the same artifact can be coherent; unrelated product workflows are not unified merely because one agent can perform them.

At discovery time the agent generally has the name and description, not the body. Put the capability and activation boundary there. A body-only exclusion cannot reliably prevent initial activation. Describe user intent rather than internal implementation. List the contexts where the skill applies, including requests that do not name its domain; the guide advises erring on the side of being pushy. [D-DESCRIPTION: Writing effective descriptions] When should-trigger queries fail, broaden scope or add context about when the skill helps; when near-misses false-trigger, add specificity about what the skill does not do or clarify its boundary with adjacent capabilities. Either way, address the general category rather than appending a failed query's keywords. [D-DESCRIPTION: The optimization loop]

For trigger tests, use realistic prompts with paths, context, casual language, and varying specificity. Positives should include indirect requests; negatives should share vocabulary but need a different task. For systematic description optimization the guide suggests about 20 queries; a smaller set can screen an obvious routing fix first (local practice). Repeat runs because activation is nondeterministic; keep a fixed, stratified train/validation split and use only training failures to revise wording. Select on held-out results and sanity-check fresh queries. The guide's counts, ratios, and thresholds are starting recommendations, not format requirements. [D-DESCRIPTION: Designing trigger eval queries; Avoiding overfitting]

## Instruction content

- Add what the agent lacks: exact commands, relevant paths, ordering constraints, API behavior, and concrete gotchas. R1 supports testing operational rules that introduce missing information; it does not justify packing arbitrary command names into prose.
- Give a default procedure and a justified escape hatch when multiple approaches work. Avoid menus of equally weighted choices with no decision criteria. [D-BEST: Calibrating control]
- Explain why a constraint matters when that helps adaptation. Be exact when deviation breaks correctness or authority; leave judgment where valid approaches vary.
- Teach a reusable method rather than hardcoding one task's answer. A short input/output example or template can settle ambiguity more effectively than another paragraph.
- Keep non-obvious gotchas visible before the agent encounters them. A conditionally loaded reference works only if the agent can recognize its loading condition.
- For batch or destructive operations, an intermediate plan checked against authoritative input can catch mistakes before execution. Use this where the task warrants it, not as an automatic approval gate.

## Progressive disclosure

Keep purpose, essential invariants, routing, and shared procedure in `SKILL.md`. Put large or conditional detail in focused references; templates and output resources belong in assets; repeated executable transformations belong in scripts. Link resources directly from the entrypoint and say when to load them. [D-SPEC; D-BEST]

The documentation recommends under 500 lines and about 5,000 tokens for the entrypoint. These are budgets, not targets or guarantees. Mandatory body headings are not specified. Follow local repository conventions where applicable without mislabeling them as standard requirements.

Moving text does not prove it remains effective: verify the reference is selected, the relevant text reaches context, and the agent acts on it. Reading a long file may be truncated. Preserve critical invariants before relocating them; use bounded reads or focused references when output limits hide important content. [R1: sections 5.2.4–5.2.5; practical inference]

## Refinement decisions

| Observation | Candidate intervention | Check before claiming improvement |
| --- | --- | --- |
| Skill not selected | Fix description, discovery, or collision | Was it actually registered and selected? |
| Loaded but rule unseen | Fix reference routing or truncated delivery | Was the instruction displayed? |
| Rule seen but ignored | Clarify applicability, procedure, or default | Did the required action occur? |
| Action occurs, result wrong | Fix domain procedure or verification | Is the final artifact correct? |
| More cost, unclear value | Compare traces; test removal or rewrite | Outcome and cost under a controlled baseline |

These are diagnostic hypotheses. Do not automatically rewrite an entrypoint when the failure is in the harness or source data.
