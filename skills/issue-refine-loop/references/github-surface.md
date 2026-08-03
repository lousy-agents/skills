# GitHub Surface Reference

> The `issue-refine-loop` skill loads this during Phase 1b (GitHub surface probe). It contains the
> only tool names in this skill. Everything outside this file names abstract operations —
> `read_issue`, `update_issue_body`, `add_comment`, `set_labels`, `create_child_issue` — and the
> mapping below is what binds them.
>
> **Nothing here is a required call.** These are examples of what a probe may find. Bind whichever
> surface is actually present; if the harness exposes something not listed, use it and record it.

## Probe Order

Probe in this order and stop at the first surface that satisfies both a read path and a write path.

### 1. Native MCP or connector issue tools

Highest preference: they are typed, they report hierarchy directly, and they need no shell quoting.

Example names seen in the wild: `mcp__github__issue_read`, `mcp__github__issue_write`,
`mcp__github__add_issue_comment`, `mcp__github__sub_issue_write`, `mcp__github__list_issues`,
`mcp__github__search_issues`, `mcp__github__get_label`, and connector-style variants such as
`github___issue_read` / `github___issue_write`.

Probe by listing available tools and reading their schemas. Do not infer a tool's parameters from
its name — a `*_write` tool that only creates issues cannot serve `update_issue_body`.

### 2. An invocable `yeet`-family skill

Names to check: `yeet`, `github:yeet`, `github-yeet`. Probe by checking the invocable-skill listing
and reading the skill's own description for which issue operations it covers. A `yeet` skill that
only creates issues supplies `create_child_issue` but not `update_issue_body`; in that case keep
probing for a surface that covers the rest, and bind one surface for the whole run.

### 3. Authenticated `gh` CLI

Lowest preference, but complete. Confirm authentication and capability before binding:

```bash
gh auth status
gh issue view --help
gh issue edit --help
gh issue create --help
gh label list --limit 1
```

Read the `--help` output rather than assuming flag support: native sub-issue flags such as
`--parent` on `gh issue create` exist only in recent versions, and their absence is exactly the
"native hierarchy unsupported" degradation. Record the `gh` version.

### Zero write surfaces

Abort. Report every probe attempted and what each returned, and state that the issue is unchanged.
Never fall back to writing a spec file, a draft, or a scratch report inside the repository — that
converts an aborted GitHub run into an unrequested repository change.

## Binding the Abstract Operations

Bind exactly one read path and one write path for the whole run. Record both in the plan comment.

| Operation | MCP / connector | `yeet`-family | `gh` CLI |
| --- | --- | --- | --- |
| `read_issue` | issue-read tool with comments and labels | skill's read verb, if any | `gh issue view <N> --repo <O/R> --json number,title,body,labels,state,comments` |
| `update_issue_body` | issue-write tool in update mode | skill's update verb, if any | `gh issue edit <N> --repo <O/R> --body-file <path>` |
| `add_comment` | issue-comment tool | skill's comment verb, if any | `gh issue comment <N> --repo <O/R> --body-file <path>` |
| `set_labels` | issue-write tool's label fields | skill's label verb, if any | `gh issue edit <N> --repo <O/R> --add-label <l> --remove-label <l>` |
| `create_child_issue` | sub-issue tool, or issue-create plus a link call | skill's create verb | `gh issue create --repo <O/R> --parent <N> --title <t> --body-file <path>` |

Do not mix surfaces mid-run. A body written through one path and labels set through another produce
inconsistent partial-failure states that cannot be diagnosed from the issue thread alone.

### Shell quoting and scratch files

Issue bodies contain Markdown, backticks, `$`, and fenced Mermaid blocks, so pass them through a
file rather than an inline argument when the bound path is the CLI. Create those files **only** in
a `mktemp -d` directory outside any working tree — never inside the repository, where a body file
can be committed by accident — and quote the heredoc delimiter so the shell expands nothing:

```bash
BODY_DIR="$(mktemp -d)"
cat > "$BODY_DIR/body.md" <<'EOF'
<composed body>
EOF
```

Remove the directory once every mutation is verified. If a mutation fails mid-run, leave the
directory in place and name its path in the closing comment so a resumed run can reuse the bodies.

## Capability Facts to Record

Two facts change later behavior and must be recorded explicitly in Phase 1b, not rediscovered
mid-run:

**Native sub-issues.** Can the bound write path establish a parent/child link? Confirm by reading
the tool schema or the CLI help, not by attempting a write. When unsupported, Phase 5 takes the
standalone-children degradation: each child body opens with a `Parent: owner/repo#N` line, the epic
gets a task list linking every child, and the closing comment discloses the degradation. Never
emulate hierarchy with labels or with an external tracker.

**Labels.** Can the bound write path add and remove labels, and can it create a label that does not
exist? Read-only label access still lets the run proceed — it just skips label transitions.

## Label Handling

Canonical lifecycle: `needs-refine` → `refining` → `refined`, plus the terminal `needs-human-input`.

Read-time aliases, accepted as equivalent on input only, never written:

| Alias found on the issue | Treated as |
| --- | --- |
| `unrefined` | `needs-refine` |
| `ready-for-implementation` | `refined` |

Rules:

- Always write the canonical name, even when the issue arrived carrying an alias. Leave the alias
  in place; removing someone else's label is outside the run's purpose.
- When a canonical label does not exist in the repository, create it if the bound write path and
  the run's permissions allow. Suggested colors and descriptions are the automation owner's choice;
  the names are not.
- When creation is not permitted, **skip that label, continue the run, and note the skip in the
  closing comment.** A label the run could not apply never changes the terminal state and never
  aborts a run. The refined body is the deliverable; labels are metadata about it.
- `refining` is also the concurrency lock. A run that observes `refining` already present, and did
  not set it itself, exits immediately without mutating anything.

## Automation Entry Points

Guidance for whoever wires the automation. This skill does not create workflow files, and asserts
nothing about which of these already exist in any repository.

**Label trigger.** Fire on `needs-refine` (or the `unrefined` alias) being added to an open issue.
The entry point sets `refining` before invoking the skill and ensures it is cleared at the terminal
state, including on failure — a stale `refining` label blocks every subsequent run on that issue.

**Scheduled scan.** A periodic job reads open issues, applies the Phase 2 completeness rubric to
each body, and labels failures `needs-refine`. It applies the **same** rubric the loop converges on;
a looser scan bar produces issues that get labeled, refined, and immediately re-labeled. The scan
labels only — it does not itself refine.

**Concurrency.** Two runs must never refine one issue at once: body writes are last-writer-wins, so
the slower run silently discards the faster run's work. Guard with both the `refining` lock above
and whatever native concurrency group the automation platform offers, keyed on `owner/repo#N`.
Prefer cancel-in-progress off and queueing on, so a second trigger waits rather than truncating a
run mid-loop.

**Autonomy mode.** Every automated entry point runs in automation mode: no approval gate, plan
comment mandatory and posted before the first body mutation, no close/reopen/transfer, and the
12-child cap enforced. A run with no human watching leaves its entire decision trail in the issue
thread or it leaves nothing.

**Permissions.** The automation's token needs issue read, issue write, and issue-comment scope;
label creation and sub-issue linking are additional. Nothing in this skill needs repository content
write, workflow write, or push access — if the automation grants those, it is over-scoped for this
job.
