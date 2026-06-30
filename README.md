# skills

Professional-grade skills tailored for **agentic software engineers** to make coding agents more autonomous and effective. Elevate your workflows across spec drafting, rigorous testing, code review, and agent tooling. Compatible with [GitHub Copilot, Gemini CLI, Claude Code, and 50+ other agents](#supported-agents) via the [Agent Skills](https://agentskills.io/) spec. Claude Code users can also install individual skills via the [plugin marketplace](#claude-code-plugin-marketplace).

[![skills.sh](https://skills.sh/b/lousy-agents/skills)](https://skills.sh/lousy-agents/skills)
[![CI](https://github.com/lousy-agents/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/lousy-agents/skills/actions/workflows/ci.yml)

## Available Skills

| Skill | Phase | Description |
| --- | --- | --- |
| [`feature-to-plan`](#feature-to-plan) | Planning | Converts feature requests and issues into structured EARS-format specs |
| [`plan-to-graph`](#plan-to-graph) | Planning | Converts specs and master plans into Beads dependency graphs of epics and tasks |
| [`rugged-evil-tester`](#rugged-evil-tester) | Testing / Hardening | Generates adversarial, security, and chaos tests for TypeScript code |
| [`mutation-hunter`](#mutation-hunter) | Testing / Hardening | Finds test coverage gaps by running mutation testing on TypeScript source |
| [`triaging-pr-reviews`](#triaging-pr-reviews) | Code Review | Triages PR review comments — verifies claims, classifies concerns, and decides what to act on |
| [`skill-reviewer`](#skill-reviewer) | Tooling / Meta | Validates and lints `SKILL.md` files for quality, discoverability, and correctness |

---

## Workflows

Skills are designed to be composed. The sections below show two common patterns: a planning workflow that takes a raw feature idea all the way to an actionable issue graph, and a map of where each skill belongs across the broader delivery lifecycle.

### Hi-Fi Planning

**Hi-fi planning** is the practice of converting a fuzzy idea into a precise, executable plan before a single line of code is written. Two skills make this possible end-to-end:

```
feature idea or GitHub issue
        │
        ▼
  feature-to-plan          ← structured EARS-format spec
        │
        ▼
  plan-to-graph            ← Beads dependency graph (epics + tasks)
        │
        ▼
  executable work items    ← agents or engineers can now implement
```

**Step 1 — Draft the spec with `feature-to-plan`**

Point the skill at a GitHub issue number, a freeform idea, or nothing (it will ask). It produces a Markdown spec under `.github/specs/` with personas, EARS acceptance criteria, Mermaid diagrams, and a task checklist — everything an agent needs to implement the feature faithfully.

```bash
npx skills add lousy-agents/skills --skill feature-to-plan
```

Invoke it in your agent:

> *"Draft a spec for adding OAuth login to the API"*
> *"Use feature-to-plan on issue #47"*

**Step 2 — Convert the spec to a dependency graph with `plan-to-graph`**

Feed the spec file to `plan-to-graph`. It parses user stories and tasks, drafts a summary table for your review, then populates your [Beads](https://beads.sh) (`bd`) database with epics, tasks, explicit dependencies, and verification notes copied from the spec.

```bash
npx skills add lousy-agents/skills --skill plan-to-graph
```

Invoke it in your agent:

> *"Convert .github/specs/oauth-login.spec.md to Beads"*
> *"plan-to-graph on the new spec"*

**Install both planning skills at once:**

```bash
npx skills add lousy-agents/skills --skill feature-to-plan --skill plan-to-graph
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
│  plan-to-graph     │   engineers)     │  evil-tester │  -pr-    │
│                    │                  │  mutation-   │  reviews │
│                    │                  │  hunter      │          │
└─────────────────────────────────────────────────────────────────┘
```

| Skill | When in the lifecycle |
| --- | --- |
| `feature-to-plan` | Before implementation begins — when you have an idea or issue but no spec |
| `plan-to-graph` | After the spec is approved — to turn tasks into tracked work items |
| `rugged-evil-tester` | During or after implementation — to harden new code against adversarial inputs |
| `mutation-hunter` | During or after implementation — to audit whether your test suite would catch real regressions |
| `triaging-pr-reviews` | At review time — to process Copilot or human review comments without blindly applying them |
| `skill-reviewer` | When authoring or updating a `SKILL.md` — a contributor/meta tool, not part of the delivery flow |

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
