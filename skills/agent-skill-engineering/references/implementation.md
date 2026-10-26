# Portable implementation

## Format contract

The authoritative source is D-SPEC, archived under `docs/specification.mdx`:

- A skill is a directory with exactly named `SKILL.md`, containing YAML frontmatter followed by Markdown instructions.
- Required `name`: 1–64 characters, lowercase alphanumeric and hyphens, no leading/trailing or consecutive hyphens, matching the parent directory. ASCII lowercase slugs avoid the source's ambiguous wording about Unicode.
- Required `description`: nonempty, up to 1,024 characters; explain capability and activation intent.
- Optional portable fields: `license`, `compatibility` (1–500 characters when present), `metadata` (string keys and values), and experimental `allowed-tools` (a space-separated string).
- The body has no mandated section schema. Optional directories and their names are conventions, not the only legal resource organization.

Client-specific fields such as `argument-hint`, `user-invocable`, or `disable-model-invocation` are not part of the pinned portable specification. Unknown-field acceptance and permission semantics vary. Use a client extension only when the intended behavior needs it and the target client supports it; do not assume it enforces anything elsewhere. Quote YAML scalar values when punctuation makes parsing ambiguous.

## Files and execution paths

Create only the files the workflow needs. A simple skill can be one file. Use relative links from the skill root; resolve them to actual locations before reading or running commands. Script paths remain relative to the skill root even when mentioned inside a reference. The target project's working directory may be different.

State both locations when needed: run the skill's helper by its resolved path and pass the target repository as an argument. Avoid silently changing directories and making subsequent project commands operate on the skill repository. Avoid machine-specific paths and mandatory sibling repositories.

Keep shared instructions independent of `$ARGUMENTS`, client-specific dynamic shell substitutions, tool names, or mandatory model IDs. Treat invocation arguments as the user's request, regardless of the harness's syntax. Use only capabilities exposed by the current runtime. If a needed tool is absent, choose an equivalent permitted operation or report the specific gap.

## Discovery and client boundaries

The format defines skill contents, not installation paths. D-CLIENT describes project/user scopes, deterministic collision handling, trust considerations, and file-read versus dedicated-tool activation as implementation choices. A lenient client loading invalid metadata does not make that metadata portable.

In the originating `lousy-agents/skills` repository, inspect the existing links before changing configuration: `.agents/skills`, `.claude/skills`, and `.github/skills` all resolve to `skills/`. A new folder under `skills/` uses those routes. Root `npx -y @lousy-agents/cli lint --skills` does not follow them and reports "No skill(s) found" with a passing status; lint a copy placed in a real `.github/skills/` directory inside a scratch directory outside the repository (copying into the repository's `.github/skills` link writes back onto `skills/`), and treat "No skill(s) found" as an unrun check. These are facts about the source repository, not assumptions about a copied installation. A skill created elsewhere should follow that repository's discovery convention or the user's installation target.

A harness sandbox can refuse writes to its own discovery directory (observed locally: Codex's workspace-write sandbox refusing `.agents/`, headless Claude Code refusing `.claude/skills/`). If installation is refused, write the skill to a staging path in the workspace, report installation as a blocked step with the exact move or link command, and do not substitute an `AGENTS.md` entry, an edit to the source document, or another pointer the user did not request.

Codex users can explicitly request `$agent-skill-engineering`; Claude Code users can request `/agent-skill-engineering` for the local skill. Plugin-installed skills may have a namespace; use the name the client exposes. Explicitly reading the entrypoint by path is a fallback when automatic discovery has not refreshed. Verify discovery separately from testing execution with a supplied path. A client name alone does not establish tested compatibility.

Do not rely on a skill to grant permissions portably: `allowed-tools` pre-approval is experimental and client-dependent [D-SPEC], and allowlisting or permission enforcement is a client choice [D-CLIENT]. Resolve available review tools and MCP servers from actual runtime discovery. Follow repository-required integrations where available; if absent, report the missing check and perform available local checks without claiming equivalence. Do not invent tool names or install external services to conceal a missing capability.

## Scripts as reliable interfaces

Bundle repeated logic when execution traces show agents recreating it [D-BEST: Bundling reusable scripts; D-EVAL: Bundle repeated work], or when a command is too complex to get right on the first try. Prefer an existing package for a short one-off operation. Pin versions and state prerequisites; do not assume `uv`, Node, Bun, or another runtime exists. Inline dependency metadata can make scripts self-contained where the runtime supports it. [D-SCRIPTS]

For a bundled script:

- Accept flags, environment, or stdin; do not block on interactive prompts.
- Provide concise `--help`, actionable validation errors, and meaningful documented exit codes.
- Separate structured result data on stdout from diagnostics on stderr.
- Validate input and handle expected failure paths. Design retries and repeated execution deliberately.
- Bound output or write large results to an explicit file; truncation may conceal critical evidence.
- Use dry-run or other safeguards for stateful operations where justified by actual risk and authorization.

Test the interface and meaningful failure behavior. Avoid tests that merely mirror implementation details or match exact instructional wording.

## Repository composition

When implementing here, read canonical policy and use installed specialty skills when their actual workflow applies. `skill-reviewer` owns structural review; this skill owns evidence-grounded design and behavioral implementation. `instruction-style` owns general instruction-file prose; `optimize-prompt-loop` owns task prompt optimization. Do not duplicate their full workflows or turn ordinary skill work into unrelated audits.

If a specialist is unavailable, carry out the relevant checks supported by the current environment and state the limitation. Local policy may make an unavailable check a submission blocker; that does not prevent preparing a reversible, reviewable implementation.
