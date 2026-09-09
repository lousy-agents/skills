# Harness load rules

Placement advice depends on **what triggers a file to load**, and the four
harnesses differ. Read this before moving a rule into a scoped or nested file.

These rules are version-sensitive. Treat the table as a starting hypothesis and
verify the trigger in the versions actually in use — a nested file that silently
never loads looks identical to one that works.

## The table

| Harness | Files it loads | What triggers a nested or scoped file | Confidence |
| --- | --- | --- | --- |
| **Claude Code** | `CLAUDE.md`, `CLAUDE.local.md`, `.claude/CLAUDE.md`, `.claude/rules/**` | Nested `CLAUDE.md` below the working directory loads when Claude reads a file in that directory. `.claude/rules/*` with `paths:` frontmatter loads when Claude reads a matching file. Both are lazy. `@import` is **eager** — an imported file loads at launch, so an import is not a context saving. | Verified against current docs |
| **Codex** | `AGENTS.override.md` then `AGENTS.md`, one file per directory | Walks project root **down to the working directory**, collecting one file per directory on that path, and concatenates with the nearest last. A file below the working directory is not on that path and does not load. Combined chain is capped at `project_doc_max_bytes`, 32 KiB by default. | Path rule verified against current docs; byte cap from Codex configuration docs, not independently exercised |
| **OpenCode** | `AGENTS.md` / `CLAUDE.md` by upward traversal, plus every glob in `opencode.json`'s `instructions` array | Initial load walks **upward** from the working directory. Whether a nested `AGENTS.md` below that directory is later injected on read is **disputed** — see below. The `instructions` array is the reliable mechanism, and it loads eagerly. | Upward traversal verified; nested-injection behavior unresolved |
| **GitHub Copilot** | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`; nearest `AGENTS.md` wins | `.github/instructions/**/*.instructions.md` with an `applyTo` glob is the scoped mechanism, and it loads when a matching file is in play. | Reported by the reviewer; not independently verified here |

## The unresolved OpenCode question

Published OpenCode documentation describes discovery as upward-only from the
working directory and states that it does not automatically scan nested
subdirectories. Two open feature requests on the project ask for exactly the
missing behavior — auto-selection of nested `AGENTS.md` based on file context,
and loading `AGENTS.md` from a directory when files there are accessed.

A reviewer reports that OpenCode v2 does inject a nested `AGENTS.md` below the
session location when a read or list touches that directory.

Both cannot be true of the same version. Do not rely on nested loading under
OpenCode without testing it in the installed version. Where the answer matters,
`opencode.json`'s `instructions` array resolves it — it takes globs such as
`packages/*/AGENTS.md` and loads them regardless of traversal, at the cost of
loading them always.

## What follows for placement

- Place a rule on the **intersection** of the load paths of the harnesses that
  need it. Only Claude Code offers lazy loading triggered by file access across
  the whole tree; Codex and OpenCode key off the working directory, and sessions
  usually start at the repository root.
- A nested `AGENTS.md` is portable in syntax and inert in effect on any harness
  that resolves from the working directory when the session starts at the root.
  That is worse than a long shared file, because the content silently vanishes
  rather than merely costing tokens.
- Prefer a shared `AGENTS.md`, or a document plus a one-line pointer from each
  core, when the harnesses disagree. Plain documents need no mechanism: every
  harness reads them with ordinary file tools when a task calls for them.
- Claude Code reads `CLAUDE.md`, not `AGENTS.md`. A repository standardizing on
  `AGENTS.md` needs a thin `CLAUDE.md` that imports it, and that import is
  eager.
- Treat a harness-private scoped file as a **projection**. Record which
  harnesses no longer see the rationale, and say so in the report.
