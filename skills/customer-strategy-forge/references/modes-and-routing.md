# Modes and Routing

Use this reference to choose interaction behavior, invocation role, and the
smallest run graph.

## Invocation Contract

Interpret a request in this shape:

```yaml
mode: paired | autonomous
role: coordinator | synthesizer | critic | product-mapper
inquiry: <question or inquiry file>
decisions_to_inform: []
decision_date: <date>
evidence_cutoff: <date>
requested_artifacts: []
human_owner: <name or stable identifier>
manifest_ref: <optional existing path>
```

Natural-language requests are valid. Resolve explicit values first, then infer
only mode and role:

- direct conversation with a human present -> paired coordinator;
- delegated subagent or “run unattended” -> autonomous;
- “review/criticize these customer artifacts” -> critic;
- “map these passed needs/journeys to our products” -> product-mapper.

Never infer the decision owner, authorization, consent, evidence cutoff, or a
waiver. Paired mode asks; autonomous mode stops.

## Paired Mode

Use short, decision-bearing questions. Ask at most what is needed for the next
gate, then continue.

Ask when:

- the strategic decision or intended artifact is ambiguous;
- two plausible scopes would produce materially different claims;
- an existing authorization cannot be resolved;
- a gate can be addressed through an explicit human choice, such as narrowing
  from a prevalence claim to a qualitative hypothesis; or
- the human must route a clean synthesizer or critic packet.

Do not ask the human to resolve facts already present in approved evidence.
Show evidence and tradeoffs before asking for a decision.

## Autonomous Mode

Autonomous runs do not ask questions, wait for replies, or manufacture human
approval. They:

1. validate the manifest and input boundary;
2. execute only authorized operations;
3. write only declared outputs;
4. use a separate critic when required and available; and
5. terminate with either a supported result or a stop artifact.

A parent agent may prepare a manifest and delegate a role to a subagent. The
subagent treats the manifest as authority only for the decisions explicitly
recorded there.

## Artifact Selection

The Grounding Brief's `required_artifacts[]` is the run graph.

| Requested outcome | Minimum operations |
| --- | --- |
| Determine what evidence can support | Inquiry Grounder + Evidence Auditor |
| Describe a situation or job | Audit + product-blind synthesis + needs/jobs + Critic |
| Develop a persona | Audit + actor/scope as needed + synthesis + segment analysis + persona assembly + Critic |
| Map a journey | Audit + synthesis + needs/jobs as needed + journey synthesis + Critic |
| Interpret progression | A passed customer artifact + optional progression mapping + Critic |
| Map product/portfolio fit | Version-pinned passed customer artifacts + Product mapper |
| Map experience coherence or joy | Passed customer emotion claims; Product mapper when capabilities are included |
| Decide next research | Evidence audit and/or validation planner; research acquisition is a separate invocation |

Dependencies are evidence needs, not a reason to emit every artifact. A journey
does not require a persona when situation-level evidence is sufficient.

## Role Handoffs

### Coordinator to Synthesizer

Pass only:

- product-independent inquiry and decision context;
- evidence-pack pointers and approved records;
- run manifest and provisional output contracts;
- applicable progression model only when that operation is selected; and
- authorized output locations.

Do not pass product goals, feature lists, portfolio hypotheses, solution-led
personas, or the coordinator's product-fit rationale.

### Synthesizer to Critic

Pass the product-independent Grounding Brief, candidate artifacts, complete
Claim Records, relevant approved evidence records/excerpts, manifest, and
access log. Do not pass private reasoning transcripts or product inventory.

### Critic to Product Mapper

Pass only a `pass` verdict with version-pinned artifacts and findings. A
non-pass verdict routes to a new synthesis/research run, never product mapping.

## Examples

Paired:

> Use customer-strategy-forge to determine whether our interview pack can
> support a persona for onboarding decisions. Work with me at the gates.

Autonomous:

> Use customer-strategy-forge in autonomous synthesizer mode. Follow
> research/runs/run-014/manifest.yaml. Produce only the authorized journey
> artifact or a terminal stop artifact.

Independent critic:

> Use customer-strategy-forge in autonomous critic mode with the packet named
> in research/runs/run-014/critic-manifest.yaml. Do not access product files.
