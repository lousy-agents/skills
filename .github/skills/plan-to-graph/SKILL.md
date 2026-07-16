---
name: plan-to-graph
description: "Converts an approved local spec, master plan, or GitHub epic issue into a GitHub Issue dependency graph with native sub-issues and blocking relationships. Use when asked to 'convert plan to issues', 'create GitHub sub-issues', 'populate issues from a spec', 'plan to graph', or 'break down a GitHub epic into tasks'."
argument-hint: "GitHub epic issue URL/number, or path to a local spec or master plan; include a target repository for local files"
effort: medium
allowed-tools: Read, Grep, Glob, Bash
---

# Plan to Graph

Translate an approved plan into GitHub Issues. Do not implement code or modify the source plan. GitHub Issues are the only durable work-item store: use native sub-issues for hierarchy and native blocking relationships for dependencies.

## When to Use

- Convert an approved `*.spec.md`, master plan, or roadmap into GitHub Issues.
- Turn a GitHub epic's `## Tasks` section into native GitHub sub-issues.
- Preserve task requirements and verification as issue bodies while representing explicit dependencies as blocking edges.

Do not use this skill to implement a plan, triage unrelated issues, or create speculative project-management work.

## Prerequisites and Input

Require authenticated GitHub CLI access. Resolve the target repository before drafting:

```bash
gh auth status
gh repo view <OWNER/REPO> --json nameWithOwner,url
```

- For a GitHub epic URL, derive `<OWNER/REPO>` from the URL, then verify it with `gh repo view`.
- For a GitHub epic number or a local file, require the user to provide `<OWNER/REPO>`; do not infer it from the current checkout.

Before drafting, confirm that the installed GitHub CLI supports the required native-relationship flags and returns every required issue JSON field. These checks are read-only:

```bash
gh version
gh issue create --help
gh issue edit --help
gh issue view --help
```

Record the `gh` version. Confirm the `create` help output includes `--parent`, the `edit` help output includes `--add-blocked-by`, and the `view` help output lists `blockedBy`, `blocking`, and `subIssues`. For a GitHub-epic source, also confirm the complete read succeeds:

```bash
gh issue view <EPIC> --repo <OWNER/REPO> --json number,title,body,labels,url,subIssues,blockedBy,blocking
```

If any check fails, stop before drafting or mutating and report the installed `gh` version plus the missing capability. Ask the user to upgrade to a GitHub CLI version that supports native sub-issues and blocking relationships; do not emulate either relationship with labels, body checklists, comments, or an external tracker.

Accept exactly one source:

- A GitHub epic issue URL or number. Derive the target repository from a URL; require a supplied target repository for a number.
- A readable local spec or master-plan file. The user must also provide a target repository; derive one epic title from the plan title.

If authentication, repository resolution, source access, or the epic issue cannot be verified, stop and report the exact blocker. Never substitute labels, body checklists, or an external tracker for native relationships.

For a GitHub epic, read its complete title, body, labels, URL, and existing hierarchy before parsing:

```bash
gh issue view <EPIC> --repo <OWNER/REPO> --json number,title,body,labels,url,subIssues,blockedBy,blocking
```

Treat every task entry under `## Tasks` as a proposed direct child. Existing metadata is context only; do not copy it into a child unless that task explicitly includes it.

## Procedure: Parse and Map

1. Read the complete source before mapping any issue. Identify the epic title, every task heading, each explicit `Depends on` statement, and the complete structured task content.
2. Preserve every task title exactly. Preserve each task body verbatim from its heading through the line before the next task, including **Objective**, **Context**, **Affected files**, **Requirements**, **Verification**, and **Done when**. Put that content in the child issue body; do not split it into comments.
3. For a GitHub epic, use that issue as the parent. For a local source, propose one new epic issue using the source title, then make every task a direct child of it.
4. Map only explicit dependencies. `Task B` with `Depends on: Task A` means B is blocked by A. If a task title, dependency target, scope, or local-plan epic title cannot be mapped unambiguously, stop and ask for clarification. Do not invent tasks, dependencies, labels, or metadata.

## Mandatory Draft Gate

Before any `gh issue create` or `gh issue edit` mutation, present a draft containing:

| Source task | Proposed issue title | Parent epic | Blocked by | Body retained |
| --- | --- | --- | --- | --- |
| Task N | exact title | issue URL/number or proposed epic | explicit task IDs | Objective, Context, Affected files, Requirements, Verification, Done when |

Also show the dependency edges in `blocked ← blocker` form and list every unmapped or ambiguous source section. Ask for explicit confirmation. A draft is read-only; do not create issues until the user confirms it.

## Create and Wire the Confirmed Graph

After confirmation, make one mutation at a time and record every returned issue URL and number.

1. For a local source, create the confirmed epic first and record its URL/number. Write the epic body to a temporary file so Markdown is preserved exactly:

   ```bash
   gh issue create --repo <OWNER/REPO> --title "<Epic Title>" --body-file <EPIC_BODY_FILE>
   ```

2. Create each confirmed child with its full, verbatim structured task content in the body. Every child-creation command must explicitly include the resolved `--repo <OWNER/REPO>`:

   ```bash
   gh issue create --repo <OWNER/REPO> --parent <EPIC> --title "<Task Title>" --body-file <TASK_BODY_FILE>
   ```

   Use a temporary body file or standard input when needed to preserve Markdown exactly. Do not add task content through issue comments.

3. Translate every confirmed dependency only after all child URLs/numbers are known:

   ```bash
   gh issue edit <CHILD> --repo <OWNER/REPO> --add-blocked-by <BLOCKER>
   ```

4. If any GitHub mutation fails, stop immediately. Report the exact command/error and the issue URLs already created; do not continue or guess at recovery.

5. Verify the resulting hierarchy and graph:

   ```bash
   gh issue view <EPIC> --repo <OWNER/REPO> --json subIssues,blockedBy,blocking
   gh issue view <CHILD> --repo <OWNER/REPO> --json parent,subIssues,blockedBy,blocking
   ```

   Confirm every child's `parent` is the epic and every explicit edge appears in the relevant `blockedBy`/`blocking` data. Stop and report any mismatch.

## Dependency Mapping Example

If a source task says `Task B` **Depends on** `Task A`, draft `B ← A` and create the corresponding native blocking relationship. Always derive every edge from the current source; never reuse an example graph, issue number, repository, or task mapping from a prior run.

## Completion Output

Report the epic URL, each created child URL/number, the verified `blocked ← blocker` edges, and any source sections deliberately not mapped. Do not claim completion until the GitHub verification output confirms the hierarchy and dependency graph.
