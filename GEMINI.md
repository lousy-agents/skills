# Lousy Agents Skills — Gemini CLI Context

## ⚠️ Source of Truth
The foundational mandates, core philosophy, and strict negative constraints for this repository are managed centrally and imported below.

@.github/copilot-instructions.md

## Agentic Parity Mandate
When updating project conventions, pull request requirements, or core mandates, you **MUST** apply those changes to `.github/copilot-instructions.md` rather than this file. This file should only contain Gemini-specific operational instructions.

## Gemini Workflow Instructions
- Utilize the `invoke_agent` and `activate_skill` tools as directed by the imported instructions.
- Ensure all automated behaviors comply with the strict negative constraints.

## Commands
Gemini-specific tool surfaces for the canonical commands documented in `.github/copilot-instructions.md`:
- Run the lint suite via the `run_shell_command` tool: `npx -y @lousy-agents/cli lint`.
- Invoke the `skill-reviewer` skill via the `activate_skill` tool.
- Use `invoke_agent` for any sub-agent delegation called for by the imported instructions.

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
