# Lousy Agents Skills - Foundational Mandates

**Core Philosophy:** This repository builds skills focused on creating secure, resilient, rugged, and production-ready software. Every action MUST improve defense, expose vulnerabilities, enable rigorous analysis, or accelerate structured engineering workflows.

## Skill Creation & Modification Workflows
- **Skill Reviewer (CRITICAL):** Before submitting any modifications to a `SKILL.md` or creating a new one, you MUST use the `activate_skill` tool with the name `skill-reviewer`. You MUST fix any major or blocker anti-patterns detected before proceeding.
- **MCP Linting:** You MUST utilize the `lousy-agents` MCP server (configured in `.mcp.json`) to evaluate and lint your skills.
- **Architecture & Format:** Adhere to the standard `SKILL.md` format with appropriate frontmatter. Keep `SKILL.md` under ~500 lines by offloading detailed templates and conversational flows to a `./references/` directory.

## Pull Request & Git Workflows
- **Template Completion:** Every PR MUST fully complete the PR template at `.github/PULL_REQUEST_TEMPLATE.md`. No section may be left blank or filled with placeholder text.
- **Duplicate Check:** Before preparing a PR, you MUST search for existing PRs that address the same problem and reference them in your new PR.
- **Human Verification (CRITICAL):** You MUST present the complete git diff to the user in the chat and obtain explicit approval before running `git commit` or opening a PR.

## Strict Negative Constraints (NEVER DO THESE)
- **NEVER implement Happy-Path or Superficial Fixes:** Do not generate only happy-path tests. We require evil tests, mutation hunting, chaos scenarios, and rigorous workflows.
- **NEVER perform Blind Automation:** Do not blindly apply automated review suggestions without verifying the claim against the actual code. If implementing a fix, you MUST verify the failure first.
- **NEVER make superficial "Compliance" Changes:** Do not restructure or reword skills just to comply with generic documentation standards without providing extensive adversarial evaluation evidence.
- **NEVER submit Bulk, Speculative, or Fabricated Content:** Every change must solve a real, experienced problem. Do not bundle multiple unrelated changes into a single PR. Do not invent claims or hallucinate functionality.
