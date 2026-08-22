# skills

Professional-grade skills for **agentic software engineers** who use coding agents to plan, implement, test, and review production software. These skills turn vague requests into spec files or GitHub issues, expose weak tests and brittle defenses, and prevent blind acceptance of automated review feedback. Compatible with [GitHub Copilot, Gemini CLI, Claude Code, and 50+ other agents](#supported-agents) via the [Agent Skills](https://agentskills.io/) spec. Claude Code users can also install individual skills via the [plugin marketplace](#claude-code-plugin-marketplace).

[![skills.sh](https://skills.sh/b/lousy-agents/skills)](https://skills.sh/lousy-agents/skills)
[![CI](https://github.com/lousy-agents/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/lousy-agents/skills/actions/workflows/ci.yml)

## Available Skills

| Skill | Phase | Description |
| --- | --- | --- |
| [`feature-to-plan`](#feature-to-plan) | Planning | Converts feature requests and issues into an EARS spec file or one new GitHub issue |
| [`issue-refine-loop`](#issue-refine-loop) | Planning | Rewrites a GitHub issue, then splits it into session-sized children with only real blockers |
| [`spec-auditor`](#spec-auditor) | Planning / Hardening | Adversarially audits specs, PRDs, issues, and plans before coding starts |
| [`plan-to-graph`](#plan-to-graph) | Planning | Converts specs, master plans, and GitHub epics into GitHub sub-issue dependency graphs |
| [`go-testable-design`](#go-testable-design) | Implementation | Guides Go development with TDD: small tests first, public behavior, IO at the edges |
| [`rugged-evil-tester`](#rugged-evil-tester) | Testing / Hardening | Generates adversarial, security, and chaos tests for TypeScript code |
| [`mutation-hunter`](#mutation-hunter) | Testing / Hardening | Finds test coverage gaps by running mutation testing on TypeScript, Go, or Python |
| [`triaging-pr-reviews`](#triaging-pr-reviews) | Code Review | Triages PR review comments: verifies claims, classifies concerns, and decides what to act on |
| [`curate-release`](#curate-release) | Code Review / Release | Rewrites a PR's commits into a coherent release story semantic-release can publish |
| [`skill-reviewer`](#skill-reviewer) | Tooling / Meta | Validates and lints `SKILL.md` files for quality, discoverability, and correctness |

---

## Workflows

Skills are designed to be composed. The sections below show two common patterns: a planning workflow that produces a spec file, a new GitHub issue, or a rewritten epic, and a map of where each skill belongs across the broader delivery lifecycle.

For agentic software engineers, the value is not simply "more prompts." Each skill gives your agent a specific harness-engineering role with explicit standards, evidence requirements, and failure modes:

- **Before coding:** convert intent into a spec file or one new GitHub issue, or rewrite an existing GitHub issue, before an agent implements it.
- **Before scheduling:** turn approved work into dependency-aware issues that preserve verification context.
- **Before merge:** generate hostile tests, find mutation survivors, and triage review comments by verifying claims against code.
- **Before publishing skills:** review skill instructions themselves so the agent behavior stays discoverable, portable, and robust.

### Hi-Fi Planning

**Hi-fi planning** is writing acceptance criteria and tasks before implementation. The four planning skills share that bar — EARS criteria, personas, value assessment, Mermaid design — but they are stages with one destination (an executable GitHub issue graph), not a single pipeline:

- **Author a spec file** — `feature-to-plan` → `spec-auditor` → `plan-to-graph`
- **Author one new GitHub issue** — `feature-to-plan` (ask it to keep the plan on GitHub) → `issue-refine-loop` **or** `plan-to-graph` if the tasks are already session-sized
- **Rewrite an issue that already exists** — [`issue-refine-loop`](#issue-refine-loop)

`feature-to-plan` **creates** a new artifact. `issue-refine-loop` **rewrites** an existing issue in place. `plan-to-graph` **fans out** an approved task list. When both authoring skills are installed, `issue-refine-loop` uses `feature-to-plan`'s format rules for EARS and task anatomy. It does not read or write the spec file.

```
                        ┌─ spec file ──► spec-auditor ──► plan-to-graph ──┐
freeform idea ──► feature-to-plan                                          ├──► parallel-ready
                        └─ new GitHub issue ─┬─ issue-refine-loop ─────────┤     issue graph
                                             └─ plan-to-graph ─────────────┘
existing thin issue ─────────────────────────► issue-refine-loop ──────────┘
```

**Rewrite an existing GitHub issue with `issue-refine-loop`**

Requires an issue number or URL — it will not create the issue from a freeform idea. It snapshots the original body as a comment, adds acceptance criteria, design, and tasks to that issue, then splits those tasks into child issues on GitHub. Each child is sized for one coding-agent session (roughly one to three files). A child lists `Depends on` only when another child actually blocks it; independent children have no blocker and are labeled `refined`, so they can be picked up in parallel. It does not write files in your repo. If `plan-to-graph` is installed and authenticated `gh` can create native sub-issues, child creation uses it; otherwise the skill creates the children itself.

```bash
npx skills add lousy-agents/skills --skill issue-refine-loop --skill feature-to-plan
```

`feature-to-plan` is optional on this path. Install it too if you want the shared format skill present — `issue-refine-loop` prefers it for EARS and task anatomy — or if you need it to **create** the starting issue from a freeform idea first.

> *"Refine issue #47"*
> *"Use issue-refine-loop on https://github.com/owner/repo/issues/162"*

**Write a spec file in the repo**

**Step 1: Draft the spec with `feature-to-plan`**

Point the skill at a GitHub issue number, a freeform idea, or nothing (it will ask). Default output is a Markdown spec under `.github/specs/` with personas, EARS acceptance criteria, Mermaid diagrams, and a task checklist. Ask it to keep the plan on GitHub and it creates **one new issue** with the same section set instead — a drafted plan, not a refined epic, and not a child graph. That is a new issue, not a rewrite of an issue you already have.

```bash
npx skills add lousy-agents/skills --skill feature-to-plan
```

Invoke it in your agent:

> *"Draft a spec for adding OAuth login to the API"*
> *"Use feature-to-plan on issue #47"*
> *"Draft this as a GitHub issue and keep it on GitHub"*

**Step 2: Audit the spec with `spec-auditor`**

Before implementation, run the draft through an adversarial review. `spec-auditor` finds contradictions, missing edge cases, untestable acceptance criteria, ambiguous ownership, and handoff risks that cause coding agents to build the wrong thing or falsely report completion. It returns structured findings with severity, evidence, Socratic questions, suggested spec patches, verification implications, and downstream agent instructions.

```bash
npx skills add lousy-agents/skills --skill spec-auditor
```

Invoke it in your agent:

> *"Audit .github/specs/oauth-login.spec.md for coding-agent failure risks"*
> *"Use spec-auditor on issue #47 before implementation"*

**Step 3: Convert the approved spec to a dependency graph with `plan-to-graph`**

Feed the approved spec or a GitHub epic to `plan-to-graph`. It parses the tasks, drafts a graph for your review, then creates native GitHub sub-issues with the full task content preserved in each body and explicit blocking dependencies.

```bash
npx skills add lousy-agents/skills --skill plan-to-graph
```

Invoke it in your agent:

> *"Convert .github/specs/oauth-login.spec.md into GitHub sub-issues in OWNER/REPO"*
> *"Create the task graph for GitHub epic #47"*

**Install all three at once:**

```bash
npx skills add lousy-agents/skills --skill feature-to-plan --skill spec-auditor --skill plan-to-graph
```

> **Prerequisite:** `plan-to-graph` requires a resolvable target repository and a way to create native sub-issues and blocking relationships: authenticated [`gh`](https://cli.github.com/) with `gh issue create --parent` and `gh issue edit --add-blocked-by`, or GitHub MCP / the harness's built-in GitHub tools when `gh` is absent or lacks those flags. The skill checks this before it creates anything and stops if neither works.

---

### Regular SDLC

The full set of skills spans the software delivery lifecycle. The table below shows the natural entry point for each skill as features move from idea to production.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│  Planning          │  Implementation  │  Testing     │  Review                 │
├────────────────────────────────────────────────────────────────────────────────┤
│  feature-to-plan   │  go-testable-    │  rugged-     │  triaging-pr-reviews    │
│  issue-refine-loop │  design          │  evil-tester │  curate-release         │
│  spec-auditor      │  (your agent or  │  mutation-   │                         │
│  plan-to-graph     │    engineers)    │  hunter      │                         │
└────────────────────────────────────────────────────────────────────────────────┘
```

| Skill | When in the lifecycle |
| --- | --- |
| `feature-to-plan` | Before implementation begins: when you want a spec file or one new GitHub issue from an idea or seed |
| `issue-refine-loop` | Before implementation begins: you have a GitHub issue to split into session-sized, parallel-ready children |
| `spec-auditor` | Before implementation begins: you have a draft spec or issue and want findings, not edits |
| `plan-to-graph` | After the spec is approved: to turn tasks into tracked work items |
| `go-testable-design` | During implementation: to write Go code test-first and design testable boundaries |
| `rugged-evil-tester` | During or after implementation: to harden new code against adversarial inputs |
| `mutation-hunter` | During or after implementation: to audit whether your test suite would catch real regressions |
| `triaging-pr-reviews` | At review time: to process Copilot or human review comments without blindly applying them |
| `curate-release` | At merge time: to curate a PR's commits so the release notes tell a coherent story |
| `skill-reviewer` | When authoring or updating a `SKILL.md`: a contributor/meta tool, not part of the delivery flow |

---

### `feature-to-plan`

**Install:** `npx skills add lousy-agents/skills --skill feature-to-plan`

Converts feature requests — either freeform or seeded from a GitHub issue — into an EARS spec file by default, or into **one new GitHub issue** with that same plan when you ask to keep it on GitHub. It supports both single-shot generation and interactive, multi-turn drafting.

**Use when you want to:**
- Turn a freeform idea or a seed issue into a spec file before writing code
- File that same drafted plan as one new GitHub issue instead of a file
- Break down feature requirements into specific Personas, User Stories, and Tasks
- Automatically generate Mermaid diagrams (data-flow, sequence) for your proposed architecture

**Do NOT use when:**
- You want an existing GitHub issue rewritten into an epic. Use `issue-refine-loop` instead.
- You want an approved task list fanned into child issues. Use `plan-to-graph` instead.

**Outputs** a Markdown spec file (e.g., in `.github/specs/`) by default, or one new GitHub issue on request — unchecked task lists, no children, no blocking edges, no lifecycle label unless you opt in to `needs-refine`. `issue-refine-loop` rewrites an existing issue in place and splits it; `plan-to-graph` fans an already-approved task list into the graph.

**Requires** GitHub access (`gh` or the agent's GitHub tools) only for issue output or for seeding from / commenting on an issue. Spec-file output does not.

---

### `issue-refine-loop`

**Install:** `npx skills add lousy-agents/skills --skill issue-refine-loop`

Rewrites an existing GitHub issue — title-only, one-sentence, or an epic missing acceptance criteria, design, or tasks — then splits the work into child issues. Each child is sized for one coding-agent session (roughly one to three files). Dependencies are recorded only when one child actually blocks another; independent children have no blocker and are labeled `refined`, so agents can take them in parallel instead of walking a serial task list. The original body is snapshotted as a comment first. No files are added to your git repo; the issue body, labels, comments, and new child issues change on GitHub.

**Use when you want to:**
- Fill in a GitHub issue that is too thin to implement (title-only, one sentence, or missing acceptance criteria, design, or tasks)
- Break a large issue into session-sized children that can proceed in parallel except where one truly blocks another
- Keep the plan on an issue that already exists, instead of authoring a new spec file or a new issue

Uses the same EARS, persona, and task format as `feature-to-plan`. When both are installed, this skill loads that format instead of its fallback. It does not read or write a spec file.

**Do NOT use when:**
- You want a new spec file, or one new GitHub issue from a freeform idea. Use `feature-to-plan` instead.
- The epic is already approved and you only need child issues. Use `plan-to-graph` instead.
- You want a findings list and nothing changed. Use `spec-auditor` instead.
- The target is a pull request, discussion, or project card. Only issues.

**Requires** GitHub access (`gh` or the agent's GitHub tools) and write permission on the issue.

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
- You want to draft a spec file or one new GitHub issue from a feature idea. Use `feature-to-plan` instead.
- You want to refine a GitHub issue in place into an epic. Use `issue-refine-loop` instead.
- You want to convert an approved spec into GitHub sub-issues. Use `plan-to-graph` instead.
- You want to triage PR review comments or Copilot feedback. Use `triaging-pr-reviews` instead.

**Outputs an audit report** with severity (Blocker / High / Medium / Low), confidence, evidence, Socratic questions, recommended spec patches, verification implications, and downstream agent instructions. Ask for JSON output to get a machine-readable findings object, useful when piping findings into a spec-improvement loop or another agent. Includes an optional Python lint script for deterministic structure checks, but the skill's primary value is adversarial, evidence-grounded review.

---

### `plan-to-graph`

**Install:** `npx skills add lousy-agents/skills --skill plan-to-graph`

Converts Lousy Agents specs, master plans, roadmaps, and GitHub epics into native GitHub sub-issues with explicit blocking dependencies. It drafts the graph for confirmation before creating any issue.

**Use when you want to:**
- Convert a `*.spec.md` file or master plan into GitHub Issues
- Break a plan's tasks into one epic and a single level of sub-issues with explicit blocking dependencies
- Preserve each task's complete structured content in its child-issue body

**Requires** a target GitHub repository and authenticated [`gh`](https://cli.github.com/) with native sub-issue and blocking-relationship support, or GitHub MCP / the harness's built-in GitHub tools when `gh` is absent or lacks those flags. Re-running against an epic that already has sub-issues will not duplicate them — the skill detects the collision and stops.

---

### `go-testable-design`

**Install:** `npx skills add lousy-agents/skills --skill go-testable-design`

Guides Go development with tests: smallest failing test first, start from public behavior, keep IO out of decision packages, and match the repo's existing acceptance tests. Informed by patterns from [`learn-go-with-tests`](https://github.com/quii/learn-go-with-tests).

**Use when you want to:**
- Build or change Go code using TDD, tests-first, red-green-refactor, or outside-in / acceptance-first starts
- Design testable boundaries around interfaces, `io.Reader`/`io.Writer`, `fs.FS`, `http.Handler`, `context.Context`, goroutines, or channels
- Refactor Go code while preserving behavior, or review Go code for testability gaps

**Standard-library-first.** Covers table tests, subtests, `t.Helper()`, constructor injection, `httptest`, goroutine/concurrency tests, property tests, and acceptance suites that follow the repository's existing test harness.

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

Applies semantic mutations to TypeScript, Go, or Python source code — swapping operators, removing null guards, inverting conditions — and identifies mutations that survive without causing any tests to fail. Each surviving mutation is a concrete test gap with actionable advice on how to close it.

**Use when you want to:**
- Audit whether your test suite would catch real behavioral regressions
- Get a coverage grade (A–F) based on mutation survival rate
- Identify exactly which boundary conditions, operator assumptions, and null-handling paths are untested

**Works on TypeScript, Go, and Python** — language is detected from the repo. Outputs a JSON report with killed/survived mutations, coverage grade, and per-gap advice. Reverts all mutations before finishing — the codebase is always left clean.

---

### `triaging-pr-reviews`

**Install:** `npx skills add lousy-agents/skills --skill triaging-pr-reviews`

Processes PR review comments — from humans or automated reviewers like GitHub Copilot — by verifying each claim against the actual code before acting on it. Automated reviewers frequently cite the wrong lines, describe behavior that can't occur, or suggest fixes that introduce the vulnerability they claim to prevent.

**Use when you want to:**
- Work through Copilot or CodeRabbit suggestions without blindly implementing them
- Catch review direction left as a plain conversation comment, not only as inline comments
- Skip threads an earlier round already resolved, instead of re-verifying them
- Classify comments by root concern (security, correctness, style) and prioritize fixes
- Automatically reply to review threads and resolve them after fixes land

It triages **every comment whose thread is still unresolved**, plus conversation-tab comments and review summaries — not the most recent batch. One submitted review's comments do not share a timestamp, so grouping by time splits a single review and leaves part of it untriaged.

**Requires** an authenticated [`gh`](https://cli.github.com/) CLI and `jq` locally, or GitHub MCP / the harness's built-in GitHub tools when `gh` is absent — including Claude Code cloud sessions, which do not pre-install `gh`. The bound surface must also be able to read review threads and their resolution state. A surface that cannot is rejected during the probe, with the missing capability named, rather than binding and then re-triaging threads that were already closed.

---

### `curate-release`

**Install:** `npx skills add lousy-agents/skills --skill curate-release`

Rewrites the commits on a pull request's head branch so the release notes semantic-release generates read as a coherent story. Types each commit by customer impact rather than by which files moved — a real fix typed `chore` does not merely go unmentioned, it can leave the entire release unpublished. The tree at HEAD stays byte-identical to the tree it started from; only commit boundaries and messages change.

**Use when you want to:**
- Turn `wip` / `address review` / `fix typo` commits into Conventional Commits before merge
- Run curation unattended from a gate label, with preflight gates that abort on drafts, forks, squash-only repos, and already-curated branches
- Know what release type and publish channel a PR will actually produce, including pre-release and maintenance branches

**Requires** a repository that merges by merge commit or rebase — squash-only repositories get a proposed squash title instead of a rewrite.

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
/plugin install issue-refine-loop@lousy-agents
/plugin install plan-to-graph@lousy-agents
/plugin install go-testable-design@lousy-agents
/plugin install rugged-evil-tester@lousy-agents
/plugin install mutation-hunter@lousy-agents
/plugin install spec-auditor@lousy-agents
/plugin install triaging-pr-reviews@lousy-agents
/plugin install curate-release@lousy-agents
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

Skills live in `skills/<name>/SKILL.md`. The `.agents/skills`, `.claude/skills`, and `.github/skills` discovery paths are compatibility links to that canonical tree. To scaffold a new skill:

```bash
npx -y @lousy-agents/cli new skill <name>
```

Before submitting a pull request, run the full lint suite — the same check the CI job runs:

```bash
npx -y @lousy-agents/cli lint
```

For the complete contributor checklist (validation gates, mandatory steps, before-commit workflow), see [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
Codex and Copilot CLI users should start from [`AGENTS.md`](AGENTS.md), Claude Code users from [`CLAUDE.md`](CLAUDE.md), and Gemini CLI/Antigravity users from [`GEMINI.md`](GEMINI.md) — all three route back to the same canonical checklist without duplicating it.
