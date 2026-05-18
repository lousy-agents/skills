# Lousy Agents Skills — Claude Code Context

## ⚠️ Source of Truth
The foundational mandates, core philosophy, and strict negative constraints for this repository are managed centrally and imported below.

@.github/copilot-instructions.md

## Agentic Parity Mandate
When updating project conventions, pull request requirements, or core mandates, you **MUST** apply those changes to `.github/copilot-instructions.md` rather than this file. This file should only contain Claude-specific operational instructions.

## Claude Workflow Instructions
- Utilize the `.claude/settings.local.json` file for any local Claude configurations as needed.
- Follow the guidelines in the imported instructions for evaluating and linting your work using MCP tools and the `skill-reviewer` skill.

## Commands
Claude-specific tool surfaces for the canonical commands documented in `.github/copilot-instructions.md`:
- Run the lint suite via the `Bash` tool: `npx -y @lousy-agents/cli lint`.
- Invoke the `skill-reviewer` skill via the `Skill` tool (it is listed in the available-skills surface).
- Use the `lousy-agents` MCP server tools directly when you need fine-grained signals: `mcp__lousy-agents__analyze_instruction_quality`, `mcp__lousy-agents__validate_instruction_coverage`, `mcp__lousy-agents__analyze_action_versions`, etc.

## Validation
Claude must validate any change with the same gates listed in `.github/copilot-instructions.md` (Validation section):
1. `npx -y @lousy-agents/cli lint` exits with 0 errors.
2. `skill-reviewer` shows no Blocker or Major findings against any modified `SKILL.md`.
3. The changed behavior was exercised in a real agent invocation, not just lint-checked.

## Verification
Verification differs from validation: it proves the change does what was promised.
- For skill edits, re-invoke the skill in the current Claude session and confirm the new behavior.
- For instruction edits, re-run `mcp__lousy-agents__analyze_instruction_quality` against the changed file and confirm the targeted findings are gone.
- For workflow edits, push the branch and confirm the GitHub Actions run is green before requesting human approval.

## Feedback Loop
Iterate one change at a time. After each edit: run lint → run `skill-reviewer` if a SKILL.md changed → fix surfaced issues → re-run lint → present the diff to the human via the chat surface before any `git commit`. Use the `TaskCreate`/`TaskUpdate` tools to track multi-step fixes so the loop stays visible.

## Mandatory
Claude must, without exception:
1. Read `.github/PULL_REQUEST_TEMPLATE.md` before opening a PR and fill every section with real content.
2. Search existing PRs (open and closed) for duplicates using `gh pr list`.
3. Run `npx -y @lousy-agents/cli lint` and resolve all errors before requesting commit approval.
4. Present the complete `git diff` in the conversation and obtain explicit human approval before any `git commit` or `gh pr create`.
5. Never stage `.claude/settings.local.json`, credentials, or other gitignored artifacts.

## Before Commit
Before invoking `git commit`:
1. `git status` then `git diff --staged` — show both to the human.
2. `npx -y @lousy-agents/cli lint` — must show 0 errors.
3. `skill-reviewer` against any modified `SKILL.md`.
4. Wait for explicit human approval in the conversation. A prior approval on a previous diff does not authorize a new commit.

## Validation Suite
The same commands the GitHub Actions workflow runs, runnable locally via the `Bash` tool:

```bash
npx -y @lousy-agents/cli lint --skills
npx -y @lousy-agents/cli lint --hooks
npx -y @lousy-agents/cli lint --instructions
npx -y @lousy-agents/cli lint --agents
```

These map 1:1 to the lousy-agents CI job in `.github/workflows/ci.yml`. Run them locally to catch failures before CI does.
