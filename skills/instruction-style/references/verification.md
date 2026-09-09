# Measuring without manufacturing defects

## A negative result is a hypothesis, not a finding

Your instrument is likelier to be wrong than the artifact. Before reporting
anything as removed, dead, missing, or miscounted, confirm the absence a second
time by a different means: search for the concept rather than the exact string,
resolve the path from its real base, read the surrounding text. Report a defect
only when two methods agree.

This is a general rule because the specific ways a check lies cannot be
enumerated. Three that have already produced false defects against correct
files:

- An identifier is **re-backticked** — a bare `lint` becoming `npm run lint` —
  and an exact-group search reads it as dropped.
- A relative link resolves **from its containing file's directory**, so every
  link in a relocated page reads as dead when checked from the repository root.
- Markdown emphasis and other spans **cross line boundaries**, so a line-based
  tool such as `grep` undercounts them. Read the whole file when the structure
  you are counting is not line-bounded.

Assume there is a fourth.

## Reporting a number

Every count you report is accompanied by the command that produced it. A number
without its command is not evidence: the next reader can only take it on faith,
or recompute it by another method and find a difference neither of you can
resolve.

A before-and-after comparison runs the **identical** command on both revisions,
not an equivalent one. Two detectors differing by one pattern produce two rates
that are not comparable, and the difference reads as a change in the artifact.

**Validate a detector against the text before reporting the rate it produces.**
Read a sample of what it flagged. A rate drives decisions, so a detector that
over-reports by missing one phrasing — a reason carried in the next sentence
rather than by a "because" — turns a small gap into a manufactured problem and
buys a fix nothing needed.

## Presenting two or more options

This shape is for a **report to a human**. Never write it into an instruction
file, and never carry its voice there: a decision record and a durable
instruction are different genres, and the close-formula below reads as
boilerplate once it lands in a file an agent loads every session.

- Analyze each option on its own.
- State its mechanism, then its limits, operational cost, and failure domain.
- Close each option with the condition that decides it: `While <context>, this
  option is the better choice. If <constraint> is violated, it fails.`
- Close the set with one table: Complexity, Failure Surface, Resource Demand.
- Give a recommendation. Do not present a survey.
