# skills

Professional-grade skills for **agentic software engineers** who use coding agents to plan, implement, test, and review production software. These skills turn vague requests into executable specs, audit those specs before an agent writes code, expose weak tests and brittle defenses, and prevent blind acceptance of automated review feedback. Compatible with [GitHub Copilot, Gemini CLI, Claude Code, and 50+ other agents](#supported-agents) via the [Agent Skills](https://agentskills.io/) spec. Claude Code users can also install individual skills via the [plugin marketplace](#claude-code-plugin-marketplace).

[![skills.sh](https://skills.sh/b/lousy-agents/skills)](https://skills.sh/lousy-agents/skills)
[![CI](https://github.com/lousy-agents/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/lousy-agents/skills/actions/workflows/ci.yml)

## Available Skills

| Skill | Phase | Description |
| --- | --- | --- |
| [`feature-to-plan`](#feature-to-plan) | Planning | Converts feature requests and issues into structured EARS-format specs |
| [`spec-auditor`](#spec-auditor) | Planning / Hardening | Adversarially audits specs, PRDs, issues, and plans before coding starts |
| [`plan-to-graph`](#plan-to-graph) | Planning | Converts specs and master plans into Beads dependency graphs of epics and tasks |
| [`rugged-evil-tester`](#rugged-evil-tester) | Testing / Hardening | Generates adversarial, security, and chaos tests for TypeScript code |
| [`mutation-hunter`](#mutation-hunter) | Testing / Hardening | Finds test coverage gaps by running mutation testing on TypeScript source |
| [`triaging-pr-reviews`](#triaging-pr-reviews) | Code Review | Triages PR review comments: verifies claims, classifies concerns, and decides what to act on |
| [`skill-reviewer`](#skill-reviewer) | Tooling / Meta | Validates and lints `SKILL.md` files for quality, discoverability, and correctness |

---

## Workflows

Skills are designed to be composed. The sections below show two common patterns: a planning workflow that takes a raw feature idea all the way to an actionable issue graph, and a map of where each skill belongs across the broader delivery lifecycle.

For agentic software engineers, the value is not simply "more prompts." Each skill gives your agent a specific harness-engineering role with explicit standards, evidence requirements, and failure modes:

- **Before coding:** convert intent into a spec, then adversarially audit the spec so agents do not guess through ambiguity.
- **Before scheduling:** turn approved work into dependency-aware issues that preserve verification context.
- **Before merge:** generate hostile tests, find mutation survivors, and triage review comments by verifying claims against code.
- **Before publishing skills:** review skill instructions themselves so the agent behavior stays discoverable, portable, and robust.

### Hi-Fi Planning

**Hi-fi planning** is the practice of converting a fuzzy idea into a precise, executable plan before a single line of code is written. Three skills make this possible end-to-end:

```
feature idea or GitHub issue
        │
        ▼
  feature-to-plan          ← structured EARS-format spec
        │
        ▼
  spec-auditor             ← adversarial findings + targeted spec patches
        │
        ▼
  plan-to-graph            ← Beads dependency graph (epics + tasks)
        │
        ▼
  executable work items    ← agents or engineers can now implement
```

**Step 1: Draft the spec with `feature-to-plan`**

Point the skill at a GitHub issue number, a freeform idea, or nothing (it will ask). It produces a Markdown spec under `.github/specs/` with personas, EARS acceptance criteria, Mermaid diagrams, and a task checklist. This includes everything an agent needs to implement the feature faithfully.

```bash
npx skills add lousy-agents/skills --skill feature-to-plan
```

Invoke it in your agent:

> *"Draft a spec for adding OAuth login to the API"*
> *"Use feature-to-plan on issue #47"*

**Step 2: Audit the spec with `spec-auditor`**

Before implementation, run the draft through an adversarial review. `spec-auditor` finds contradictions, missing edge cases, untestable acceptance criteria, ambiguous ownership, and handoff risks that cause coding agents to build the wrong thing or falsely report completion. It returns structured findings with severity, evidence, Socratic questions, suggested spec patches, verification implications, and downstream agent instructions.

```bash
npx skills add lousy-agents/skills --skill spec-auditor
```

Invoke it in your agent:

> *"Audit .github/specs/oauth-login.spec.md for coding-agent failure risks"*
> *"Use spec-auditor on issue #47 before implementation"*

**Step 3: Convert the approved spec to a dependency graph with `plan-to-graph`**

Feed the spec file to `plan-to-graph`. It parses user stories and tasks, drafts a summary table for your review, then populates your [Beads](https://beads.sh) (`bd`) database with epics, tasks, explicit dependencies, and verification notes copied from the spec.

```bash
npx skills add lousy-agents/skills --skill plan-to-graph
```

Invoke it in your agent:

> *"Convert .github/specs/oauth-login.spec.md to Beads"*
> *"plan-to-graph on the new spec"*

**Install all three planning skills at once:**

```bash
npx skills add lousy-agents/skills --skill feature-to-plan --skill spec-auditor --skill plan-to-graph
```

> **Prerequisite:** `plan-to-graph` requires the Beads `bd` CLI installed and initialized in the repository. See [beads.sh](https://beads.sh) for setup.

---

### Regular SDLC

The full set of skills spans the software delivery lifecycle. The table below shows the natural entry point for each skill as features move from idea to production.

```
┌─────────────────────────────────────────────────────────────────┐
│  Planning          │  Implementation  │  Testing     │  Review  │
├─────────────────────────────────────────────────────────────────┤
│  feature-to-plan   │  (your agent or  │  rugged-     │  triaging│
│  spec-auditor      │   engineers)     │  evil-tester │  -pr-    │
│  plan-to-graph     │                  │  mutation-   │  reviews │
│                    │                  │  hunter      │          │
└─────────────────────────────────────────────────────────────────┘
```

| Skill | When in the lifecycle |
| --- | --- |
| `feature-to-plan` | Before implementation begins: when you have an idea or issue but no spec |
| `spec-auditor` | Before implementation begins: after a draft spec exists, before an agent receives it |
| `plan-to-graph` | After the spec is approved: to turn tasks into tracked work items |
| `rugged-evil-tester` | During or after implementation: to harden new code against adversarial inputs |
| `mutation-hunter` | During or after implementation: to audit whether your test suite would catch real regressions |
| `triaging-pr-reviews` | At review time: to process Copilot or human review comments without blindly applying them |
| `skill-reviewer` | When authoring or updating a `SKILL.md`: a contributor/meta tool, not part of the delivery flow |

---

### `feature-to-plan`

**Install:** `npx skills add lousy-agents/skills --skill feature-to-plan`

Converts feature requests — either freeform or seeded from a GitHub issue — into structured EARS-format specs. It supports both single-shot generation and interactive, multi-turn drafting.

**Use when you want to:**
- Turn a freeform idea or a GitHub issue into a rigorous spec before writing code
- Break down feature requirements into specific Personas, User Stories, and Tasks
- Automatically generate Mermaid diagrams (data-flow, sequence) for your proposed architecture

**Outputs a Markdown spec file** (e.g., in `.github/specs/`) complete with unchecked task lists, ready for an agent to implement. Optionally integrates with the `gh` CLI to fetch issue context.

---

### `spec-auditor`

**Install:** `npx skills add lousy-agents/skills --skill spec-auditor`

Adversarially reviews feature specifications, implementation plans, GitHub issues, PRDs, and EARS-format specs before coding starts. It looks for the gaps that make coding agents fail: contradictions, vague acceptance criteria, missing edge cases, unclear ownership, unverifiable outcomes, and scope that spans multiple unrelated changes.

When run from a repository, it reads `AGENTS.md`, `CLAUDE.md`, `README.md`, and other instruction files to anchor findings in real project constraints rather than generic advice.

**Use when you want to:**
- Stress-test a spec before handing it to Codex, GitHub Copilot, Claude, or another coding agent
- Find ambiguity, missing critical paths, and untestable requirements while they are still cheap to fix
- Produce structured findings (SA-001, SA-002, …) with stable IDs that can feed a spec-improvement loop or downstream agent handoff

**Do NOT use when:**
- You want to draft a spec from a feature idea or issue. Use `feature-to-plan` instead.
- You want to convert an approved spec into Beads epics and tasks. Use `plan-to-graph` instead.
- You want to triage PR review comments or Copilot feedback. Use `triaging-pr-reviews` instead.

**Outputs an audit report** with severity (Blocker / High / Medium / Low), confidence, evidence, Socratic questions, recommended spec patches, verification implications, and downstream agent instructions. Ask for JSON output to get a machine-readable findings object, useful when piping findings into a spec-improvement loop or another agent. Includes an optional Python lint script for deterministic structure checks, but the skill's primary value is adversarial, evidence-grounded review.

---

### `plan-to-graph`

**Install:** `npx skills add lousy-agents/skills --skill plan-to-graph`

Converts Lousy Agents specs, master plans, and roadmaps into Beads (`bd`) epics and tasks with explicit dependencies and verification notes. It drafts the graph for confirmation before populating the Beads database.

**Use when you want to:**
- Convert a `*.spec.md` file or master plan into Beads issues
- Break user stories, phases, or roadmap items into epics and tasks with dependencies
- Preserve acceptance criteria and verification steps as issue comments

**Requires** the Beads `bd` CLI installed and initialized.

---

### `rugged-evil-tester`

**Install:** `npx skills add lousy-agents/skills --skill rugged-evil-tester`

Generates adversarial tests that prove your defenses actually work. Instead of happy-path coverage, this skill targets security weaknesses, boundary conditions, and chaos scenarios.

**Use when you want to:**
- Test whether input validation rejects SQL injection, XSS, prototype pollution, and similar payloads
- Verify that failures in external dependencies (auth services, databases, caches) cause the system to fail closed
- Add security regression tests to CI that prove defensive layers can't be bypassed

**TypeScript-focused.** Uses Vitest and MSW. Places test files as `<target>.evil.test.ts` alongside source files.

---

### `mutation-hunter`

**Install:** `npx skills add lousy-agents/skills --skill mutation-hunter`

Applies semantic mutations to TypeScript source code — swapping operators, removing null guards, inverting conditions — and identifies mutations that survive without causing any tests to fail. Each surviving mutation is a concrete test gap with actionable advice on how to close it.

**Use when you want to:**
- Audit whether your test suite would catch real behavioral regressions
- Get a coverage grade (A–F) based on mutation survival rate
- Identify exactly which boundary conditions, operator assumptions, and null-handling paths are untested

**Outputs a JSON report** with killed/survived mutations, coverage grade, and per-gap advice. Reverts all mutations before finishing — the codebase is always left clean.

---

### `triaging-pr-reviews`

**Install:** `npx skills add lousy-agents/skills --skill triaging-pr-reviews`

Processes PR review comments — from humans or automated reviewers like GitHub Copilot — by verifying each claim against the actual code before acting on it. Automated reviewers frequently cite the wrong lines, describe behavior that can't occur, or suggest fixes that introduce the vulnerability they claim to prevent.

**Use when you want to:**
- Work through a batch of Copilot or CodeRabbit suggestions without blindly implementing them
- Classify comments by root concern (security, correctness, style) and prioritize fixes
- Automatically reply to review threads and resolve them after fixes land

**Requires** `gh` CLI and `jq`.

---

### `skill-reviewer`

**Install:** `npx skills add lousy-agents/skills --skill skill-reviewer`

Audits `SKILL.md` files for correctness, discoverability, and structure. Checks frontmatter validity, description quality (the primary discovery surface), body structure, progressive loading budget, and common anti-patterns.

**Use when you want to:**
- Validate a new or updated skill before merging
- Debug why an agent isn't discovering or invoking a skill
- Ensure a skill follows the Agent Skills spec and will work across supported agents

## Install

```bash
npx skills add lousy-agents/skills
```

Install a specific skill:

```bash
npx skills add lousy-agents/skills --skill <skill-name>
```

Install to specific agents:

```bash
# GitHub Copilot only
npx skills add lousy-agents/skills -a github-copilot

# Gemini CLI only
npx skills add lousy-agents/skills -a gemini-cli

# Both
npx skills add lousy-agents/skills -a github-copilot -a gemini-cli
```

Install globally (available across all your projects):

```bash
npx skills add lousy-agents/skills -g
```

### Claude Code Plugin Marketplace

Claude Code users can install skills individually through the native plugin system:

```
/plugin marketplace add lousy-agents/skills
```

Install any skill by name:

```
/plugin install feature-to-plan@lousy-agents
/plugin install plan-to-graph@lousy-agents
/plugin install rugged-evil-tester@lousy-agents
/plugin install mutation-hunter@lousy-agents
/plugin install spec-auditor@lousy-agents
/plugin install triaging-pr-reviews@lousy-agents
/plugin install skill-reviewer@lousy-agents
```

## Supported Agents

Skills follow the open [Agent Skills specification](https://agentskills.io/) and are compatible with any agent that supports it, including:

| Agent | `--agent` / `-a` | Project Path |
| --- | --- | --- |
| GitHub Copilot | `github-copilot` | `.agents/skills/` |
| Gemini CLI | `gemini-cli` | `.agents/skills/` |
| Claude Code | `claude-code` | `.claude/skills/` |
| Cursor | `cursor` | `.agents/skills/` |
| Codex | `codex` | `.agents/skills/` |

For the full list of supported agents, see [vercel-labs/skills](https://github.com/vercel-labs/skills#supported-agents).

## License

[BSD 2-Clause](LICENSE)

## Contributing

Skills live in `.github/skills/<name>/SKILL.md`. To scaffold a new skill:

```bash
npx -y @lousy-agents/cli new skill <name>
```

Before submitting a pull request, run the full lint suite — the same check the CI job runs:

```bash
npx -y @lousy-agents/cli lint
```

For the complete contributor checklist (validation gates, mandatory steps, before-commit workflow), see [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
