---
name: instruction-style
description: Author or revise durable agent-facing instruction prose — AGENTS.md, CLAUDE.md, .github/copilot-instructions.md, .github/instructions/*.instructions.md, OpenCode instructions, Codex and Claude subagent and command files, rules files, specs — so an agent reads the right priority, sees why each constraint exists, and does not apply a rule where it does not fit. Use when asked to clean up, tighten, harden, or standardize instruction files, to settle obligation wording on one closed modal set, to place rules across a hybrid harness set (applyTo, paths, imported cores and thin adapters), to check whether instruction files have drifted from the code and CI they describe, or to review an instruction diff for lost meaning. Do NOT use to optimize a one-off task prompt for immediate execution, to lint a SKILL.md against Agent Skills packaging rules, or to audit a feature specification for implementation defects.
argument-hint: "Path or glob of instruction files to revise (or paste the prose); say 'apply' to write files instead of proposing a diff"
allowed-tools: Read, Grep, Glob, Bash(npx @lousy-agents/cli doctor*), Bash(git diff*), Bash(git log*), Bash(git show*)
compatibility: Discovery via `npx @lousy-agents/cli doctor` needs Node.js and network access on first run. Doctor is optional — fallback glob discovery is first-class and carries no prerequisite.
---

# Instruction Style

Write and revise agent-facing prose so an agent reads the right priority,
understands why each constraint exists, and does not apply a rule where it does
not fit.

Misreading is not the failure mode you are preventing. Agents parse English
fine. Instruction files fail three other ways: the agent **misprioritizes**
(two rules apply and nothing says which wins), it **routes around an opaque
rule** (the rule's purpose is invisible, so a clever workaround looks
compliant), and it **over-applies** (a rule written for one case gets used
everywhere). Optimize against those three.

## When to apply

- Shared instruction cores and their adapters: `AGENTS.md`, `CLAUDE.md`,
  `.github/copilot-instructions.md`, OpenCode `instructions` entries.
- Path-scoped instruction files: `.github/instructions/**/*.instructions.md`,
  `.claude/rules/**`.
- Subagent, command, and agent files across harnesses, plus the routing
  `description` of a skill.
- Specs, plans, and architecture notes the agent authors.
- A diff that rewrote any of the above, when the question is what meaning was lost.

Scope is durable instruction prose. A skill or command **procedure body** — the
numbered steps an agent executes — is out of scope: leave its voice alone. A
skill's routing `description` is in scope; the rest of its frontmatter is not.

## When not to apply

- Do not touch source code, identifiers, command names, file paths, vendored or
  lockfile-owned text, or strings that tests assert. Changing those breaks
  builds rather than improving prose.
- Do not rewrite **load-bearing frontmatter** — `applyTo`, `paths`,
  `excludeAgent`, a Copilot agent file's `tools` or `model` — while restyling,
  because those keys decide whether the file loads at all. Creating a new
  path-scoped file may add them; that is a placement task, and only a placement
  request authorizes it.
- Do not override repository instructions, safety rules, or test-locked wording,
  because this contract governs how prose reads and never what it is allowed to
  require.
- Do not edit before the locked-string inventory in Work step 2 exists. Tests,
  hooks, and plugin loaders match on instruction text verbatim.

## Modality: one closed set, declared once

- One word for mandatory, one for recommended, one for plain fact — and no
  other modal carrying obligation anywhere in the file. Which three words is a
  house-style choice, not a correctness one; the failure being fixed is a file
  where `must`, `shall`, `should`, "make sure", and a bare imperative all appear
  and nothing says which outranks which.
- **Detect the file's existing vocabulary and stay inside it.** If a file
  already carries obligation on `MUST`, keep `MUST` and make it consistent.
  Converting a Copilot-owned file, or a shared canonical file that already uses
  `MUST`, over to `shall` fights the house style it lives in and churns a diff
  for no reader benefit. Pick the incumbent, then close the set around it.
- Declare the chosen set once, near the top of the file, so a reader never has
  to infer it.
- Delete hedges attached to real requirements (`try to`, `if possible`,
  `ideally`, `where practical`). An agent reads them literally as permission to
  under-deliver.
- Do not add emphasis (`CRITICAL`, `ALWAYS`, caps, bold) to carry priority.
  Priority comes from the modal verb. When several rules are marked critical,
  the marker stops carrying information.
- Before removing emphasis, check whether it is structural. Tests, hooks, and
  loaders slice instruction files on their formatting — a heading, a numbered
  step marker, the bold span that follows one — so stripping it breaks the
  build. Emphasis a parser depends on is not emphasis carrying priority. The
  lock-surface greps are in `references/discovery.md`.

## Every constraint carries its reason

- State the reason in the same sentence as the rule, or in the next sentence.
  A rule whose purpose is visible gets applied correctly in cases it did not
  anticipate. A bare rule gets routed around.
- Write `Return 503 so a partial read never reads as an authorized empty
  result`, not `Return 503`.
- If you cannot state why a rule exists, report it. An unjustifiable rule is a
  removal candidate, not a rule to reformat.
- **Sweep lists and table cells, not only flowing prose.** A rule living in a
  bullet or a table cell is still a rule, and a pass that rewrites paragraphs
  and skips lists leaves the prohibitions untouched — which is the half where a
  missing reason costs most. Measured on a real pass over an unfamiliar
  repository, every residual out-of-set modal and every bare prohibition sat in
  a bullet list or a severity table, none in prose.

## Form: match the formalism to the content

**Reference content** — contracts, invariants, error conditions, API behavior,
and ordered procedures where exactly one sequence is safe. Give this structure,
and use EARS where a trigger or fault condition needs naming:

- Ubiquitous: The \<actor\> shall \<action\>.
- Event-driven: When \<trigger\>, the \<actor\> shall \<action\>.
- State-driven: While \<state\>, the \<actor\> shall \<action\>.
- Unwanted: If \<fault or condition\>, then the \<actor\> shall \<action\>.
- Optional: Where \<feature exists\>, the \<actor\> shall \<action\>.

Name the exception when one exists: `If the store errors (not a clean miss),
then ...`. The value of these templates is that they force you to name the
trigger, the actor, and the exception. Once those are named, ordinary prose
carries them equally well — the template is an authoring aid, not a
comprehension aid.

**Behavioral content** — how to exercise judgment, when to push back, what good
work looks like, what a role is for. Write this as prose that carries its
reasons. Do not force it into a requirement template: a disposition expressed
as a prohibition loses the judgment it was meant to enable. Prefer a positive
statement of the target over a list of banned outcomes, because a prohibition
against a failure the agent was not going to make can anchor it toward that
failure.

Compare. `Do not add comments` is a prohibition that overfires. `Write code
that reads like the surrounding code: match its comment density, naming, and
idiom` is the same intent as a disposition, and it generalizes.

Three conversions to refuse outright, because each destroys the judgment it
was standing in for:

| Leave as prose | Never render as |
| --- | --- |
| Be skeptical of a passing suite you did not run | The agent shall be skeptical |
| Match the surrounding code's taste | The agent shall match taste |
| Say so in a sentence and continue, when the request looks mistaken | If the request is mistaken, then the agent shall push back |

A role, a taste, and a disposition toward pushing back are not triggers,
faults, or ordered procedures, so no EARS form fits them.

## Structure

- Keep related statements grouped under a shared parent. Do not flatten nested
  structure into sibling bullets: grouping is what tells the reader which facts
  belong to which subject.
- Use bullets and tables for reference data. Use prose for behavior. Bullets
  sever a rule from its reason, and prompt format bleeds into output format —
  a file written as clipped fragments trains clipped fragmentary output.
- Make a requirement individually checkable — one requirement, not three fused
  into a clause a reviewer can only half-satisfy. This is not a one-clause
  sentence rule: keep the causal and contrastive subordinates (`so that`, `even
  though`, `rather than`) that carry the reasoning, and never split a sentence
  merely to shorten it.
- Use one term for one concept throughout a file. Two names for one thing makes
  the reader look for a distinction that is not there.
- Keep the file's existing wrapping convention. Rewrapping a file makes every
  paragraph show as changed, and an unreviewable diff costs more than the line
  count it saves. Human review of the diff is the last defense against the
  rationale loss the keep list guards, so protect it.

## Address

Classify the file before choosing an address. Getting this wrong leaks one
harness's voice into every other harness that loads the same bytes.

- **Shared canonical core** — `AGENTS.md` and any file imported into several
  harnesses. Use the imperative without "you", or name the actor. Never second
  person: several harnesses load this file, and one of them inlines it into a
  system prompt where "you" would address whoever happens to be reading.
- **Single-harness actor file** — a `CLAUDE.md` body below its import, a Copilot
  `*.agent.md`, a subagent definition. Second person, because the file is that
  actor's system prompt and is read in that register.
- **After a hard import A → B**, put shared rules in B and keep A for
  harness-private routing. Do not state a requirement at both ends: the reader
  sees the concatenation, and a rule that appears twice in two voices reads as
  two rules.
- Do not mix registers inside one file, because a reader addressed as "you"
  reads a later third-person rule as being about somebody else.

## What not to remove

A revision pass deletes the highest-value words first unless it is told not to.
Length is not the target; never justify a deletion by word count. Preserve, and
restore if a prior pass removed them:

- **Reason clauses**: `so that`, `because`, `otherwise`, `which is why`.
- **Intent markers**: `deliberately`, `intentionally`, `by design`. These mark a
  choice an agent shall not "repair", and repairing an intentional design is the
  most expensive failure mode in a config-heavy repository. They are not
  qualifiers of degree.
- **Stance words** that set a role's disposition: `adversarial`, `skeptical`.
- **Discriminating detail in routing text** — descriptions of skills, tools, and
  subagents. These are lookup tables, and specifics are what make routing work.
  Under-description is the common failure here, not over-description.
- **Defining clauses** that say what a term means. Without them a paragraph that
  reads as guidance becomes unactionable.
- **Examples** that pin a format-sensitive output shape.
- **Prohibitions** against failures that still occur.

## Size and placement

- **The only size rule is the always-loaded set budget.** Add up everything the
  harness loads unconditionally — the core, every adapter, every unscoped rules
  file — and judge that one number. Per-file word and line figures are advisory
  and are not a target to hit.
- **The keep list outranks any size figure.** Rationale, intent markers, and
  routing discriminators are never what you cut to reach a number. A file over
  its advisory figure because the excess is rationale is the tradeoff working.
  Cut derivable reference first, and stop there.
- One harness enforces a real ceiling rather than a preference: Codex truncates
  the concatenated AGENTS.md chain at `project_doc_max_bytes`, 32 KiB by
  default. See `references/harness-load.md`.
- Growth is cheap in a path-scoped file and expensive in an always-loaded one,
  so spend it accordingly. Where the harness supports scoping — Copilot's
  `applyTo`, Claude Code's `.claude/rules/` `paths` — a scoped file carries long
  reasoning at no cost to a session that never touches those paths. A rewrite
  that doubles a scoped file while holding the always-loaded set flat is the
  placement working, not bloat.
- A harness-private scoped file is a **projection**, not a move. Every harness
  outside that mechanism loses the rationale entirely. Record which harnesses
  no longer see it, and say so in your report; a rule that silently vanishes for
  two of four harnesses is worse than a long shared file.
- Move content an agent can derive from the codebase — directory layouts,
  dependency lists, architecture overviews, benchmark measurements — into docs
  and leave a one-line pointer. Keep pitfalls, rationale, and conventions that
  differ from tool defaults.
- Move documentation about one command into that command's own file.
- Place a rule on the **intersection** of the load paths of the harnesses that
  need it. Triggers differ per harness and are version-sensitive: read
  `references/harness-load.md` before choosing placement.

## Discovering the prompt surface

Enumerate the surface with a command where you can, because a glob finds the
harnesses you thought of and misses the one you forgot. Fallback globbing is
first-class and carries no prerequisite.

Read `references/discovery.md` before this step. It holds the doctor
invocation and filter, the full fallback glob list across all four harnesses,
and the lock-surface greps to run before you strip emphasis or rewrap.

Two rules that hold regardless of method:

- **The inventory is the surface, not the scope.** Most records in any
  repository are skills, and some are owned upstream by a lockfile. Intersect
  the surface with what the invocation and the repository allow.
- **Discovery is topology, not evaluation.** An empty `findings[]` from any
  tool is not a clean bill of health, and it does not excuse the checks below.

## Verify the claims, not just the prose

Instruction files rot factually as the code ships, and nothing re-checks them by
default. An inaccurate instruction costs more than an inelegant one: an agent
following accurate but clumsy prose outperforms one following polished prose
that is false. Check every checkable claim against what it describes, and
correct what has drifted.

- **Counts and inventories** — job names, leaf counts, task lists, file counts.
  Extract ground truth from the source — the CI workflow, the task-runner
  config, the directory listing — and compare, rather than reading the prose
  for plausibility.
- **Coverage claims** — when a file says a task runs "everything except X",
  resolve that task's actual closure and confirm X is the only gap.
- **Scoping globs that match nothing.** A path-scoped instruction file is
  dormant if its glob matches no file, and it fails silently: the content looks
  maintained and never loads. Expand every `applyTo` and `paths` pattern against
  the repository and confirm a non-empty match. One real case: `**/spec.md`
  matched zero files while 2,000 words of spec guidance sat unused.
- **Dangling citations, in both directions.** Grep the codebase for references
  to the file you are editing. Code citing a policy the file does not state is
  a gap in the file, not in the code. A rule that nothing references and
  nothing enforces is a removal candidate.
- **Paths and links** — take these from `doctor`'s `edges[]`, where
  `malformed: true` marks a reference that does not resolve. Resolving paths by
  hand is error-prone: a relative link resolves from its containing file's
  directory, and checking from the repository root reports every link in a
  relocated page as dead.

Report drift you find even when it sits outside the prose you were asked to
revise. Finding it is cheap here and expensive later.

## Work

1. Read the repository's agent instructions and the target files before editing.
2. **Inventory what is locked, before the first edit.** Search tests, hooks, and
   loaders for the headings, step markers, asserted phrases, and load-bearing
   frontmatter keys they match on. The patterns are in `references/discovery.md`.
   List them up front; a grep before each deletion catches the phrase you
   thought to check and misses the one you did not.
3. **Discover the prompt surface.** See `references/discovery.md` for both
   methods. Intersect the surface with the scope: if the invocation names files
   or a glob, that is the scope; otherwise ask before touching a file the
   repository owns from upstream. Do not invent files.
4. **Classify each target file** as a shared canonical core, a single-harness
   actor file, or a path-scoped projection, because address and placement both
   depend on it. Consult `references/harness-load.md` before moving a rule.
5. Run the accuracy pass above. Fix drift in the same change.
6. Keep existing meaning, authority, and names. Change wording and structure.
7. **Propose a unified diff. Do not write files unless the invocation says to.**
   "Clean it up", "tighten this", "harden these files", and "fix these files"
   all mean propose. Only an explicit `apply`, "write the files", or "commit
   these edits" authorizes writing to disk.

   Opening a pull request is a proposal. Committing to a shared default branch
   is not, and is never authorized by this skill. Committing to the agent's own
   working branch is allowed only under an explicit apply phrase.
8. Report what you moved, any rule you could not attach a reason to, any drift
   you found but did not fix, and which harnesses lose visibility of a rule you
   projected into a scoped file.

## Presenting two or more options

When the task ends in a recommendation rather than a diff, use the option-report
shape in `references/verification.md`. It is a report to a human: never write it
into an instruction file, and never carry its voice there.

## Verification

- Obligation inside each file is carried by that file's declared set and no
  other modal. No hedges on requirements, no emphasis substituting for
  priority. Sweep with
  `grep -niE '\b(must|has to|need to|ought to|have to)\b'` across every changed
  file and read each hit, because the count alone over-reports: only a
  **deontic** use — an obligation on the reader — violates the set. A
  **descriptive** use, such as "a list that has to be updated in repository
  settings", states how the world behaves and is not a modal to convert.
- Every prohibition and every non-obvious constraint states its reason.
- EARS forms appear on trigger and fault conditions, not on dispositions.
- Reason clauses, intent markers, routing discriminators, and defining clauses
  survive the edit. **Count across the whole post-edit surface**, source plus
  anything relocated, or every phrase that moved reads as a loss. A reason
  reworded is preserved — judge the clause, not the token.
- Every claim checked in the accuracy pass matches its source.
- Identifiers, paths, frontmatter, vendored text, and test-locked strings
  survive. An identifier that moved inside a different backtick group still
  survives.
- Every count you report is accompanied by the command that produced it, and a
  before-and-after comparison runs the identical command on both revisions.
  `references/verification.md` explains why, and how a detector manufactures a
  defect when it does not.
- Run the verification once. Do not add further review passes.

### A negative result is a hypothesis, not a finding

Your instrument is likelier to be wrong than the artifact. Before reporting
anything as removed, dead, missing, or miscounted, confirm the absence a second
time by a different means. Report a defect only when two methods agree.
`references/verification.md` lists the failure modes that have already produced
false defects against correct files, and why the list cannot be complete.

## Output

- The requested artifact, or a proposed diff, already in this contract.
- A short list of what you moved, any rule you could not justify, and any
  factual drift you found.
- The command beside every number you report, so a reader can rerun it.
- What you could not verify, named plainly. A check you could not run is not a
  check that passed.
- No persona, no process narration.

## What this contract deliberately omits

Earlier versions carried ASD-STE100 rules: sentence-length caps, a ban on
unbound qualifiers, a compound-noun limit, a ban on contractions. They are
omitted on purpose, recorded here so a later pass does not restore them as an
oversight.

STE100 serves a reader whose English is limited. That is not this reader. Its
caps cost subordination, and subordination (`so that`, `even though`, `rather
than`) is where causal reasoning lives. Its qualifier ban cannot tell a
degree-qualifier like `fast` from an intent marker like `deliberately`, so
applying it mechanically strips exactly the words in the keep list.

A closed modal set is kept because it fixes misprioritization and costs nothing
structurally. The contract does not name RFC 2119: that standard's mandatory
word is `MUST`, and mandating a `MUST` → `shall` rewrite would fight the house
style of every Copilot-owned and GitHub-scaffolded file it touched. Closing the
set matters; which words close it does not.

EARS is kept, scoped to triggers, faults, and ordered procedures, because it
has no slot for a reason — an author who applies it everywhere strips rationale
as a matter of course.

## Applying this contract to itself

A skill's routing `description` is in scope. **This procedure body is not.** Do
not convert its steps to a modal set or an EARS form, and do not strip its
structural emphasis: it is a procedure an agent executes, not durable
instruction prose an agent is governed by.
