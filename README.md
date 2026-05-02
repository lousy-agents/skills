# skills

A collection of reusable coding agent skills for AI assistants. Skills follow the [Agent Skills](https://agentskills.io/) specification and work with **GitHub Copilot**, **Gemini CLI**, and [50+ other coding agents](#supported-agents).

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

## Available Skills

<!-- Skills will be listed here as they are added -->

> Skills are coming soon. Check back or watch this repo for updates.

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

## Skill Structure

Each skill lives in its own directory under `skills/` and contains a `SKILL.md` file:

```
skills/
└── my-skill/
    ├── SKILL.md        # Required: metadata + agent instructions
    ├── scripts/        # Optional: helper scripts
    └── references/     # Optional: reference documentation
```

### SKILL.md Format

```markdown
---
name: my-skill
description: Brief description of what this skill does and when to use it.
metadata:
  author: lousy-agents
  version: "1.0"
---

# My Skill

Instructions for the agent to follow when this skill is activated.

## When to Use

- Situation 1
- Situation 2

## Steps

1. First, do this
2. Then, do that
```

## Contributing

1. Fork this repository
2. Create a new directory under `skills/` named after your skill (lowercase, hyphens only)
3. Add a `SKILL.md` file following the format above
4. Open a pull request

### Skill Naming Conventions

- Use lowercase letters, numbers, and hyphens only
- Be descriptive but concise (e.g., `git-conventional-commits`, `pr-review-checklist`)
- The `name` field in `SKILL.md` must match the directory name

## License

[BSD 2-Clause](LICENSE)