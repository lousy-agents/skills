# Lousy Agents Skills — Foundational Mandates & Contributor Guidelines

## Core Philosophy
This repository builds skills focused on creating **secure, resilient, rugged, and production-ready software**. Every change must be evaluated through this lens: *Does this improve defense, expose vulnerabilities, enable rigorous analysis, or accelerate structured, high-quality engineering workflows (like planning or agent tooling)?*

## Pull Request Requirements
Before opening a PR against this repo, you MUST:
1. **Internalize the Core Philosophy.**
2. **Read the entire PR template** at `.github/PULL_REQUEST_TEMPLATE.md` and fill in every section with real, specific answers. Not summaries. Not placeholders.
3. **Search for existing PRs** — open AND closed — that address the same problem. If duplicates exist, STOP and inform your human partner.
4. **Human Verification (CRITICAL):** You MUST present the complete git diff to your human partner and obtain explicit approval before running `git commit` or opening a PR.

## What We Will Not Accept (Strict Negative Constraints)

1. **NEVER implement Happy-Path or Superficial Fixes**
   We build tools for the real world. Skills that generate only happy-path tests, ignore boundary conditions, or assume a secure environment will not be accepted. We require evil tests, mutation hunting, chaos scenarios, and tools that enforce rigorous planning and review workflows.

2. **NEVER perform Blind Automation Without Verification**
   Tools that automate processes without robust verification—such as blindly applying automated PR review suggestions without verifying the claim against the actual code—are fundamentally unsafe. If implementing a fix, you MUST verify the failure first.

3. **NEVER make superficial "Compliance" Changes**
   Our internal skill philosophy differs from generic published guidance. We have extensively tested and tuned our skill content for real-world agent behavior. Do not restructure, reword, or reformat skills just to "comply" with general documentation standards without providing extensive adversarial evaluation evidence showing the change improves outcomes.

4. **NEVER submit Bulk, Speculative, or Fabricated Content**
   Do not bundle multiple unrelated changes into a single PR. Every PR must solve a real problem that someone actually experienced. Do not invent claims, fabricate problem descriptions, or hallucinate functionality.

## Evaluation & Linting (MCP Integration)
Skills are code that shapes agent behavior. If you modify skill content, you must prove the change is effective:
- **Lousy Agents MCP Tools:** The repository is configured with `.mcp.json`. You MUST utilize the `lousy-agents` MCP server to evaluate and lint your skills.
- **Skill Reviewer (CRITICAL):** Before submitting any modifications to a `SKILL.md` or creating a new one, you MUST run the `skill-reviewer` skill (using `activate_skill` or equivalent tools) against your work and fix any major or blocker anti-patterns detected.
- **Progressive Loading:** Keep `SKILL.md` under ~500 lines by offloading detailed templates and conversational flows to a `./references/` directory.

## Understand the Project Before Contributing
Read existing skills (e.g., `rugged-evil-tester`, `mutation-hunter`, `triaging-pr-reviews`, `plan-to-graph`, `feature-to-plan`) and understand the project's design decisions. Changes that rewrite the project's voice or restructure its approach without understanding why it exists will be rejected.

## Commands
The only tooling required to work in this repo is `npx` (Node 18+). There is no `package.json` — skills are markdown and YAML.

- `npx -y @lousy-agents/cli lint` — full lint suite (skills, agents, hooks, instructions). Run from repo root.
- `npx -y @lousy-agents/cli lint --skills` — frontmatter validation for every `SKILL.md` under `.github/skills/`.
- `npx -y @lousy-agents/cli lint --hooks` — schema validation for `.claude/settings.json` and `.github/hooks/agent-shell/hooks.json` (if present).
- `npx -y @lousy-agents/cli lint --instructions` — quality analysis of `.github/copilot-instructions.md`, `CLAUDE.md`, and other instruction files.
- `npx -y @lousy-agents/cli new skill <name>` — scaffold a new skill folder under `.github/skills/<name>/`.
- `npx -y skills add lousy-agents/skills --skill <name>` — how downstream users install a skill from this repo into their own project.

MCP servers configured in `.mcp.json` (must be enabled in your client to use them):
- `lousy-agents` — provides `analyze_instruction_quality`, `validate_instruction_coverage`, `analyze_action_versions`, `discover_environment`, `discover_feedback_loops`, and related tools.
- `context7` — fetches current library/framework documentation.
- `sequential-thinking` — structured reasoning for complex problems.

## Validation
A change is "validated" when every check below is green and the contributor can name the evidence:
1. **Lint is clean.** `npx -y @lousy-agents/cli lint` exits with 0 errors. Warnings are inspected, not ignored — each one must either be fixed or have a documented rationale for being kept.
2. **Skill-reviewer agrees.** For any modified or new `SKILL.md`, run the `skill-reviewer` skill (or `mcp__lousy-agents__analyze_instruction_quality` for instructions) and fix every Blocker or Major finding before review.
3. **Behavior was tested, not just lint-checked.** Skills shape agent behavior — passing lint proves the file parses, not that the skill works. Invoke the changed skill in a real agent session and confirm the agent reaches the intended behavior.

## Verification
Verification proves the change *does what it claims*, distinct from validation (which proves it meets standards):
- **For skill content changes:** demonstrate the behavior difference in a real agent invocation. Capture before/after transcripts or behavior notes in the PR description.
- **For lint or workflow changes:** show the lint output before and after the change. A workflow change must be exercised in a PR run, not just rendered.
- **For instruction-file changes:** re-run `npx -y @lousy-agents/cli lint --instructions` to confirm the targeted warnings disappear, and re-run a representative agent flow that consumes the instructions to confirm no regression.

## Feedback Loop
The contribution loop for this repo is short and iterative — never a one-shot dump:
1. Change one thing (a single skill, a single instruction section, one workflow job).
2. Run `npx -y @lousy-agents/cli lint`. Read every finding.
3. If a finding asks you to comply superficially (see §3), reject it consciously and note the rejection. If it surfaces a real defect, fix it.
4. Run `skill-reviewer` against any modified `SKILL.md`.
5. Re-run lint to confirm the fix didn't regress another check.
6. Present the diff to the human partner for explicit approval before committing.
7. If a surprise occurred (behavior didn't match prediction, lint flagged something new), capture the lesson — keep the loop's learning visible to the next contributor.

## Mandatory
These steps cannot be skipped, regardless of how small the change feels:
1. Read `.github/PULL_REQUEST_TEMPLATE.md` and answer every section with concrete content. No placeholders.
2. Search existing open and closed PRs for duplicates before opening a new one.
3. Run `npx -y @lousy-agents/cli lint` locally and resolve all errors before pushing.
4. Run the `skill-reviewer` skill against any `SKILL.md` you touched.
5. Present the complete `git diff` to your human partner and obtain explicit approval before `git commit` or `gh pr create`.
6. Never include `.claude/settings.local.json` or any credentials in a commit — `settings.local.json` is gitignored on purpose.

## Before Commit
Run this checklist in order. If any step fails, fix and restart from step 1:
1. `git status` — review staged and unstaged changes. Confirm no incidental files (local settings, scratch dirs) are staged.
2. `npx -y @lousy-agents/cli lint` — must show 0 errors.
3. For each modified `SKILL.md`: run `skill-reviewer` and fix all Blocker/Major findings.
4. `git diff --staged` — read every hunk yourself before showing the human partner.
5. Human partner reviews the diff and gives explicit approval.
6. Only then: `git commit`.

## Validation Suite
The minimum command set CI runs and contributors must run locally:

```bash
npx -y @lousy-agents/cli lint --skills
npx -y @lousy-agents/cli lint --hooks
npx -y @lousy-agents/cli lint --instructions
npx -y @lousy-agents/cli lint --agents
```

A full run is also fine:

```bash
npx -y @lousy-agents/cli lint
```

CI runs the full suite via the `zpratt/lousy-agents` action defined in `.github/workflows/ci.yml`. The action and the CLI exercise the same underlying lint package, so a clean local run should match CI.
