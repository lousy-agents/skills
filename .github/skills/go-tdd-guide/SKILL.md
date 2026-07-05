---
name: go-tdd-guide
description: "Use when writing, adding, or improving Go tests, developing or refactoring Go code using TDD, test-first, or red-green-refactor, reviewing Go code for testability, or explaining Go test patterns. Guides unit tests, table tests, subtests, helpers with t.Helper, dependency injection, httptest, io/fs boundaries, context cancellation, concurrency tests, property tests, and standard-library-first design from learn-go-with-tests patterns."
argument-hint: "Optional: package, file path, bug, feature, or chapter-style topic to work on"
allowed-tools: "Read, Write, Edit, Bash, Grep, Glob, read_file, edit_file, create_file, run_in_terminal, list_directory_contents"
---

# Go TDD Guide

Guide Go development with tests in the style of `learn-go-with-tests`: small behavior first, executable examples, clear boundaries, and incremental refactoring.

## When to Use

Use this skill when the user asks to:

- Build or change Go code using TDD, tests first, or red-green-refactor.
- Add, improve, or explain Go tests.
- Design Go code around interfaces, `io.Reader`/`io.Writer`, `fs.FS`, `http.Handler`, `context.Context`, goroutines, channels, or storage boundaries.
- Refactor Go code while preserving behavior.
- Review Go code for testability or missing test cases.
- Learn or demonstrate Go concepts through tests.

Do not use this skill for non-Go projects, generic CI setup, or broad architecture work where tests are not part of the task.

## Core Rules

- Prefer the standard library unless the repository already uses a focused dependency.
- Start from externally visible behavior: exported function, method, handler, CLI, file reader, or concurrent contract.
- Write the smallest failing test that names the behavior.
- Make the smallest production change that passes.
- Refactor only after behavior is covered.
- Keep test helpers small and mark them with `t.Helper()`.
- Use interfaces at boundaries, not everywhere.
- Keep production APIs zero-value friendly where practical.
- Do not hide meaningful errors from tests; assert them.
- Avoid sleeps in tests unless the behavior is explicitly timing-based. Prefer fake clocks, channels, contexts, or retry helpers.

## Procedure

1. **Orient**
   - Inspect `go.mod`, package layout, existing tests, and naming conventions.
   - Identify the smallest package or file that owns the behavior.
   - If `go` is available, run the narrowest baseline test first:

     ```bash
     go test ./path/to/package
     ```

2. **Choose the Test Shape**
   - Pure functions: use direct assertions, then table tests once cases multiply.
   - Methods with mutation: assert state before and after, and cover error paths.
   - HTTP handlers: use `net/http/httptest`; assert status, headers, body, and store interactions.
   - CLI or printing code: inject `io.Reader` and `io.Writer`; assert output and side effects.
   - File parsing or rendering: prefer `fs.FS`, `strings.Reader`, `bytes.Buffer`, temp files, and approval-style fixtures when useful.
   - Concurrency: test the contract with channels, `sync.WaitGroup`, `context.Context`, and timeouts that fail fast.
   - Properties or reversible transformations: add `testing/quick` after concrete examples establish the expected behavior.

3. **Write the First Failing Test**
   - Name the behavior with `t.Run` when multiple cases are expected.
   - Put expected values in the test, not hidden inside helpers.
   - Introduce helpers only after the test starts repeating setup or assertion detail.

4. **Implement Simply**
   - Hard-code when that is the honest smallest step.
   - Parameterize once the second test forces it.
   - Extract functions, interfaces, or generic helpers only when tests show repeated structure.

5. **Refactor Under Tests**
   - Move side effects behind small interfaces or function fields.
   - Keep core calculations pure and adapters thin.
   - For application code, split composition roots (`cmd/.../main.go`) from reusable package logic.

6. **Verify**
   - Run the narrow package test after each meaningful change.
   - Run broader tests before finalizing when the change touches shared APIs:

     ```bash
     go test ./...
     ```

   - If the local environment lacks Go or dependencies, report that clearly and include the exact command that should be run.

## Test Patterns

Use idiomatic Go test structure:

```go
func TestThing(t *testing.T) {
    t.Run("describes one behavior", func(t *testing.T) {
        got := Thing(input)
        want := expected

        if got != want {
            t.Errorf("got %v, want %v", got, want)
        }
    })
}
```

Use helpers when they make intent clearer:

```go
func assertEqual[T comparable](t testing.TB, got, want T) {
    t.Helper()

    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }
}
```

Use spies and stubs at boundaries:

```go
type SpyStore struct {
    recorded []string
}

func (s *SpyStore) RecordWin(name string) {
    s.recorded = append(s.recorded, name)
}
```

## Chapter Pattern Reference

For more specific guidance from the explored repository, read [`references/chapter-patterns.md`](./references/chapter-patterns.md) when the task involves:

- Recreating a `learn-go-with-tests` style chapter progression.
- Choosing between test styles for a particular Go topic.
- Working on HTTP, JSON, file IO, CLI, time, websocket, context, concurrency, reflection, generics, Roman numeral, rendering, or Q&A-style examples.
- Explaining why a Go design is testable in the style of this repo.

## Output Expectations

When reporting work:

- State which package/files changed.
- State which tests were added or changed.
- State the verification command and result.
- If tests could not run, state why without implying they passed.
