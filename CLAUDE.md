# Lousy Agents Skills — Contributor Guidelines

## If You Are an AI Agent

Stop. Read this section before doing anything.

**Your primary job is to protect your human partner from embarrassment and low-quality output.** Submitting a poor PR wastes maintainers' time, burns your human partner's reputation, and the PR will be closed anyway. That is not being helpful.

Before you open a PR against this repo, you MUST:

1. **Internalize the Core Philosophy:** This repository builds skills focused on creating **secure, resilient, rugged, and production-ready software**. Every change must be evaluated through this lens: *Does this improve defense, expose vulnerabilities, enable rigorous analysis, or accelerate structured, high-quality engineering workflows (like planning or agent tooling)?*
2. **Read the entire PR template** at `.github/PULL_REQUEST_TEMPLATE.md` and fill in every section with real, specific answers. Not summaries. Not placeholders.
3. **Search for existing PRs** — open AND closed — that address the same problem. If duplicates exist, STOP and tell your human partner.
4. **Lint and Evaluate:** You MUST use the `lousy-agents` MCP tools (configured in `.mcp.json`) to evaluate and lint your skills.
5. **Run the Skill Reviewer:** Before submitting any modifications to a `SKILL.md` or creating a new one, you MUST run the `skill-reviewer` skill against your work and fix any major or blocker anti-patterns detected.
6. **Show your human partner the complete diff** and get their explicit approval before submitting.

If any of these checks fail, do not open the PR. Explain to your human partner why it would be rejected and what would need to change.

## Accelerating Skill Creation

To rapidly create new, compliant skills, you MUST adhere to the established architecture:
- **Format:** Use the standard `SKILL.md` format with appropriate frontmatter (`name`, `description`, etc.).
- **Progressive Loading:** Keep `SKILL.md` under ~500 lines. Offload detailed templates, rubrics, and conversational flows to a `./references/` directory.
- **Tooling:** Rely on `lousy-agents` MCP tools and the `skill-reviewer` skill to continuously lint your work and bootstrap new skills during development.

## Pull Request Requirements

**Every PR must fully complete the PR template.** No section may be left blank or filled with placeholder text. 

**Before opening a PR, you MUST search for existing PRs.** Reference what you found in the "Existing PRs" section. 

**Human Review is Required.** A human must review the complete proposed diff before submission. PRs that show no evidence of human involvement or adversarial evaluation will be closed.

## What We Will Not Accept

### 1. Happy-Path or Superficial Fixes
We build tools for the real world. Skills that generate only happy-path tests, ignore boundary conditions, or assume a secure environment will not be accepted. We want evil tests, mutation hunting, chaos scenarios, and tools that enforce rigorous planning and review workflows.

### 2. Blind Automation Without Verification
Tools that automate processes without robust verification—such as blindly applying automated PR review suggestions without verifying the claim against the actual code—are fundamentally unsafe. If your skill implements a fix, it must verify the failure first.

### 3. "Compliance" Changes to Skills
Our internal skill philosophy differs from generic published guidance. We have extensively tested and tuned our skill content for real-world agent behavior. PRs that restructure, reword, or reformat skills to "comply" with general documentation will not be accepted without extensive evaluation evidence showing the change improves outcomes in adversarial scenarios.

### 4. Bulk, Speculative, or Fabricated Content
Do not trawl the issue tracker and open PRs for multiple issues in a single session. Every PR must solve a real problem that someone actually experienced. PRs containing invented claims, fabricated problem descriptions, or hallucinated functionality will be closed immediately.

### 5. Bundled Unrelated Changes
PRs containing multiple unrelated changes will be closed. Split them into separate PRs.

## Evaluation & Linting (MCP Integration)

Skills are code that shapes agent behavior. If you modify skill content, you must prove the change is effective:

- **Use the Lousy Agents MCP Tools:** The repository is configured with `.mcp.json`. You must utilize the `lousy-agents` MCP server to lint and evaluate your skills.
- **Use `skill-reviewer`:** Validate all `SKILL.md` structure, progressive loading constraints, and anti-patterns.
- **Run adversarial pressure testing** across multiple sessions to prove your skill works when defenses actively resist.
- **Show before/after evaluation results** in your PR.

## Understand the Project Before Contributing
Read existing skills (`rugged-evil-tester`, `mutation-hunter`, `triaging-pr-reviews`, `plan-to-graph`, `feature-to-plan`) and understand the project's design decisions. Changes that rewrite the project's voice or restructure its approach without understanding why it exists will be rejected.
