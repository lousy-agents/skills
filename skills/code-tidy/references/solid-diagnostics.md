# SOLID diagnostics

Load this before step 4c. Diagnose first, transform second. The
Structure rules in `tidy-rules.md` are remedies; this file decides
whether a remedy is warranted, which one, and how to prove it.

## Rules of engagement

- Diagnose only production files in this pass's work set. Read out-of-scope callers,
  tests, and git history as evidence; edit them only for mechanical
  call-sites.
- Function length is not a finding. A `switch` is not a finding. An
  interface with one implementation is not a finding by itself. Each
  finding needs evidence of an independent reason to change, a broken
  caller expectation, or a dependency that points the wrong way.
- Speculative vs justified: an abstraction with one implementation,
  no second use in the tree, and no test that exercises the seam is
  speculative — remove it under the Structure rules. A boundary with
  two or more concrete consumers or variations already in the tree,
  or a test that needs the seam, is justified — keep it; only narrow
  or move it.
- Do not introduce inheritance or class hierarchies into a repository
  that does not use them. Go interfaces and TypeScript structural
  types (`Pick`, function parameters) are the boundary vehicles.
- Record every accepted finding **before** any edit, in the state
  file's `## Structure findings` section, one line:

  `<path>:<line> → <principle> → <evidence> → <consequence> → <proposed refactoring> → <validation> → apply | defer (<reason>)`

- `apply` only when the remedy is an extract, rename, narrow, collapse,
  or move that stays in scope and preserves behavior. Anything else is
  `defer`: keep the line, put a one-line recommendation under
  `questions`, and add a pending ruling when the ruling list applies.
  A deferred finding never disappears from the record.
- Narrate one line when done: `Diagnose  <n> findings, <n> apply, <n> defer`.

## Single responsibility

- **Signals:** one type or function that persistence, formatting, and
  policy all reach into; unrelated changes landing in the same file
  across the history; a test that needs two unrelated fixtures for
  one unit.
- **Evidence:** `git log --format=%s -- <path>` for independent
  reasons the file changed; callers grouped by concern; the fixtures
  its tests build.
- **Confirmed when:** two concerns would change for different reasons
  and different requesters, and each has its own callers or tests.
- **Not a violation:** a long function whose steps all serve one
  reason to change. Extract it for readability under the Structure
  rules; do not record it as SRP.
- **Example (Go):** `SaveInvoice(inv Invoice, db *sql.DB)` computes
  tax and writes rows; tax policy and storage change independently.
  Remedy: extract `taxFor(inv)` as a pure function, leave the write
  where it is. **(TS):** `formatAndPost(order)` renders HTML and calls
  `fetch`; extract `render(order)`.
- **Validation:** a characterization test on the observable result of
  each concern before the extraction; suite green vs baseline after.
- **Ruling when:** the split changes a serialized format or a public
  API.

## Open/closed

- **Signals:** the same `switch` / `if` chain over a kind repeated in
  several functions, and the history shows each new kind edited all
  of them; a comment saying "add the new case here too".
- **Evidence:** `git log -p -- <path>` shows two or more commits that
  each touched the same chain in two or more places for one new
  variant; the variants have their own tests.
- **Confirmed when:** the variation is real (present in the tree at
  least twice) and every addition forces edits across otherwise
  stable logic.
- **Not a violation:** one `switch` in one place; a variation that has
  happened once. Never add an extension point for a variation that
  has not occurred.
- **Example (Go):** three functions switch on `report.Kind` to pick a
  renderer. Remedy: collapse to one lookup, `renderers[kind]`, in the
  place that already knows the kinds — a move plus a collapse, not a
  new interface. **(TS):** a discriminated union handled by one
  `switch` in one module is fine; the same `switch` copied into three
  modules is the finding.
- **Validation:** the per-kind tests still pass; one test proves an
  unknown kind fails the same way it did before.
- **Ruling when:** the extension point would become part of a public
  API.

## Liskov substitution

- **Signals:** an implementation that panics or throws "not
  supported", ignores an argument the interface documents, needs
  setup the interface does not mention, or returns success without
  doing the work.
- **Evidence:** every caller's expectation of each interface method
  (what it does with the result and the error), compared with each
  implementation's preconditions, guarantees, and side effects.
- **Confirmed when:** a caller written against the interface would
  behave incorrectly with one implementation: a stronger
  precondition, a weaker guarantee, an unsupported operation, or a
  side effect the others lack.
- **Not a violation:** an implementation that is slower, logs more, or
  returns a narrower error than documented.
- **Example (Go):** `Store.Delete(id)` returns nil for a missing id in
  the in-memory implementation and `ErrNotFound` in the SQL one; a
  caller retries on nil. Remedy: make both return the documented
  error, and hold it with one contract test run against every
  implementation (extract the test, not a type). **(TS):** a
  `Notifier.send()` that resolves without sending in production is
  the finding; a test double that does so by design is not.
- **Validation:** one contract test per interface method, run against
  all implementations in scope.
- **Ruling when:** the fix changes the documented contract, or the
  odd implementation's behavior may be intentional and the tests and
  PR description are silent.

## Interface segregation

- **Signals:** consumers that stub or panic in methods they never
  call; test doubles that implement ten methods to exercise one; an
  interface named after a type rather than a capability.
- **Evidence:** for each consumer, the methods it actually calls; for
  each interface, its method count against the widest consumer's use.
- **Confirmed when:** at least one consumer depends on methods it never
  calls, and those methods force stubs or coupling to a wider
  implementation.
- **Not a violation:** a broad implementation consumed through a
  narrow dependency. Width of the type is fine; width of the
  dependency is the finding.
- **Example (Go):** `type Repo interface { Get; Put; Delete; List;
  Migrate }` consumed by a reader that calls only `Get`. Remedy:
  narrow — declare `type getter interface{ Get(...) }` beside the
  consumer and take that; the broad type still satisfies it.
  **(TS):** accept `Pick<Repo, 'get'>` at the consumer.
- **Validation:** the consumer's tests now use a one-method double;
  suite green vs baseline.
- **Ruling when:** a consumer of the interface is out of scope, or the
  interface is exported from a published package.

## Dependency inversion

- **Signals:** business policy that imports a database driver, an HTTP
  client, a clock, or a filesystem directly; constructors that build
  their own infrastructure; policy tests that need a network or a
  real file.
- **Evidence:** the in-scope package's import graph (`go list -deps`,
  or the TS import lines); tests that are skipped or slow because of
  the dependency; a seam that already exists and is bypassed.
- **Confirmed when:** a policy decision cannot be tested without the
  infrastructure, and the infrastructure detail leaks into the
  policy's signature or behavior.
- **Not a violation:** an adapter package importing the driver it
  adapts; a `main` that wires concrete types; a small program with one
  layer.
- **Example (Go):** `pricing.Quote` calls `sql.Open` itself. Remedy:
  move the open to the caller and pass the existing `*sql.DB` (a
  move), or take the narrow consumer-owned interface the policy
  actually needs (`type rateSource interface{ Rate(ctx, sku) }`). Do
  not invent a repository framework. **(TS):** a pricing module that
  calls `fetch` takes a `rates: (sku) => Promise<Rate>` parameter.
- **Validation:** the policy test runs with an in-memory rate source
  and no network; the adapter keeps its integration test.
- **Ruling when:** moving the wiring outward touches files far outside
  the scope list, or the boundary changes a public constructor.

## Deferred findings across passes

Write the line with `defer` and the reason (a ruling name, `out of
scope`, `changes behavior`, or `public API`). Copy a one-line
recommendation to `questions`. Add the pending ruling when the reason
is on the ruling list. The next pass reads the Structure findings
section before diagnosing and does not re-diagnose a deferred finding
whose evidence has not changed.
