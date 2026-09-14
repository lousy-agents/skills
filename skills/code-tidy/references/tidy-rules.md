# Tidy rules

SOLID phase only. Applies to the **post-coach** tree. Load this before
step 4. Production edits here are extract / rename / narrow / collapse
/ move. No further behavior change.

## Framework Orient

Inspect imports, config, nearby tests, and project instructions
**before** any rename, split, or restructure. Use only the real
container nodes of the framework that is already there. Do not invent
a node.

Real nodes = whatever the in-scope files already import from the
runner. The table below is **examples, not prescriptions**. If the
repo does not use a node, you may not introduce it. If the repo
already uses a node that is not in the table (`afterEach`,
`beforeAll`, `test.describe`, …), keep using it.

| Ecosystem | Real nodes (if already imported / configured) |
| --- | --- |
| Ginkgo | `Describe` / `Context` / `When` / `It` / `BeforeEach` / `By` |
| Vitest / Jest | `describe` / `it` / `test` / `beforeEach` / `afterEach` / `beforeAll` / `afterAll` |
| Playwright | `test.describe` / `test` / `test.beforeEach` / `test.afterEach` |
| RSpec | `describe` / `context` / `it` |
| Go stdlib | `t.Run`, table tests |

Go repos: read `go-testable-design` for unit vs acceptance form and
package fitness. Do not copy its stdlib-default unit shapes onto an
acceptance suite that already uses another runner. Do not switch
vehicles.

A stdlib-testing Go repo must not grow Ginkgo (or any other) nodes.
That is issue #18 / PR #27.

## Tests first

- Nest real nodes so names carry purpose, scenarios, fixtures, and
  controls. The nested structure is the documentation. A comment is
  the last choice.
- Rename each test so the name makes a behavioral claim.
- One clear behavioral claim per test. Split only when failure modes
  are independent. Keep a coherent scenario together.
- Assert observables, not mock interactions. Delete a test that
  asserts only the shape of the implementation, and only in the same
  commit that adds or confirms result-based coverage. Do not delete
  the last test that holds a behavior you will restructure. Keep an
  interaction test that *is* the external contract (port, adapter,
  protocol). Doubtful case → Ruling required.
- A test verifies behavior; it does not define it. Keep each
  assertion at least as strong as it was. If a change makes a test
  fail, repair the code or revert. Do not weaken or delete a test to
  reach green. A test that looks incorrect → Ruling required; leave
  it.
- Add coverage for each new behavior this PR already added.
- Characterization tests before restructuring production code.
- Make assertions and structure stronger so the tests document
  non-obvious behavior, invariants, and edge cases — instead of a
  comment in production code.

## Structure

One behavior-preserving step at a time. Keep the tests green vs the
post-coach baseline.

- Extract until each function reads as prose. Smallest change that
  gives clarity. A primary goal is to remove the need for a comment.
  Do not extract *only* to delete a comment, but extract or rename
  when that removes the need and keeps the code easy to read.
- Rename an unclear name. Split a type that has more than one real
  reason to change.
- Narrow an interface that causes stubs or has unused methods, only
  when every consumer is in scope. Otherwise Ruling required.
- Remove hidden side effects. Remove sentinel error returns and
  boolean error returns.
- Use the abstractions that are there. Do not invent one. Remove a
  speculative abstraction (interface with one impl and no second use,
  unnecessary factory). Keep an intentional seam for a plugin or for
  testability.
- Delete a comment in the same step that makes it obsolete.
- After each step, run the smallest covering tests. Full suite before
  each commit. Red vs baseline and not quickly fixable → return to
  the last green commit.

## Comment keep-bar

Delete by default. A comment does not execute and becomes incorrect
with time. Prefer clear production code. Prefer executable tests more.

Both gates must be true before you keep a comment:

1. You cannot refactor further (names, extractions, intermediate
   values, predicates, control flow) to make the choice
   self-explanatory.
2. You cannot improve the tests (real-node nesting, stronger
   assertions, clearer structure) to document the requirement, edge
   case, or reason — without speculative abstraction and without too
   much scaffolding.

If either route is still open, take it and delete the comment. Only
when both are closed may you keep one, and only if it also matches:

- A reason improved code and tests cannot show (external defect,
  forced external constraint, legal or protocol requirement).
- A citation of a specification, RFC, or published algorithm.
- A machine-readable directive (`//nolint`, `# type: ignore`,
  `#[allow]`).
- A license or SPDX header.
- Public API documentation that a generator or external tool uses.
  Keep it if you are not sure.
- An invariant the language cannot express and a test cannot hold.

Dense logic you cannot reduce (bit manipulation, numerical methods,
protocol layouts) can agree with these. First put the maximum
explanation into structure and tests.

**Delete:** comments that repeat the code, section banners, AAA
labels (`// Arrange`, `// Act`, `// Assert`, `// Act & Assert`),
changelog notes, attribution notes, ticket notes, commented-out code,
signature-repeating docstrings, ownerless TODOs, comments that only
explain a name.

A project instruction to *structure* tests as arrange-act-assert is
not a conflict with deleting AAA *comment labels*. Nest real nodes
and name the tests so the structure is the documentation. Record a
ruling only if the instruction explicitly requires the comment text
to remain.

Keep machine directives, including `// biome-ignore`,
`//nolint`, `# type: ignore`, and triple-slash references
(`/// <reference ... />`).

Keep prose out of a long identifier, a string constant, a commit
message, and a paragraph-length test name.

**Calibration.** This bar is intentionally difficult. Almost no
comment in ordinary application code stays. In protocol, numerical,
security, and interoperation code, more stay, but only the ones you
cannot reduce. A comment in a test has the same bar, or a harder one.

Decide every comment in every in-scope file, then mark the file
`clean`.

## Ruling required

Record in the state file. Collect in the report. Do no work on the
item in this pass or a later pass until a ruling comes.

- A change to a public API, a cross-service interface, a serialized
  format, or a schema.
- Behavior that looks incorrect but can be intentional, when the
  tests and the PR description say nothing or do not agree.
- A test that looks incorrect.
- Behavior with no test and no clear requirement.
- A refactor that needs changes to files far outside the PR set.
- An interface to narrow when a consumer is not in scope.
- A requirement with two readings that give very different designs.
- A change to performance-sensitive, security-sensitive, or
  concurrency-sensitive code that can cause a regression.
- A project instruction or a license constraint that does not agree
  with these rules.
- A pure data file, schema file, or configuration file, where these
  rules do not apply.
- Coach Stage-B whose only fix changes a public contract, a schema,
  or layer policy itself.
