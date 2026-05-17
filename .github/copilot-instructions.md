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
