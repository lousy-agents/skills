---
name: example-skill
description: A starter template demonstrating the SKILL.md format. Use this as a reference when creating new skills for this repository.
metadata:
  author: lousy-agents
  version: "1.0"
  internal: true
---

# Example Skill

This is a starter template for creating new skills. Copy this directory, rename it, and replace the content below with your own instructions.

## When to Use

- When you want to understand the structure of a skill in this repository
- As a starting point for creating a new skill

## Steps

1. Copy this skill's directory and rename it to your skill name (lowercase, hyphens only)
2. Update the YAML frontmatter:
   - Set `name` to match the directory name
   - Write a clear `description` explaining what the skill does and when to use it
   - Remove `internal: true` when the skill is ready to publish
3. Replace this body with detailed agent instructions
4. Optionally add a `scripts/` folder for helper scripts and a `references/` folder for supporting documentation

## Tips

- Keep the `description` concise — agents use it to decide whether to load the full skill
- Write instructions as if speaking directly to the agent
- Include concrete examples and step-by-step guidance where helpful
