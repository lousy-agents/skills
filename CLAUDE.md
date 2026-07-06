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
Imported from `.github/copilot-instructions.md`.

## Verification
Imported from `.github/copilot-instructions.md`.

## Feedback Loop
Imported from `.github/copilot-instructions.md`.

## Mandatory
Imported from `.github/copilot-instructions.md`.

## Before Commit
Imported from `.github/copilot-instructions.md`.

## Validation Suite
Imported from `.github/copilot-instructions.md`.
