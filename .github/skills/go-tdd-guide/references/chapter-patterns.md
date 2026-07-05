# Chapter Patterns from `learn-go-with-tests`

Use this reference when a task benefits from the concrete patterns observed in the `learn-go-with-tests` repository.

## Foundation Chapters

Use these patterns for small language concepts and pure behavior.

- `hello-world/`: evolves from `main()` printing text to a pure `Hello` function, defaults, language branching, named subtests, and `assertCorrectMessage`.
- `integers/`: keeps production tiny and adds `ExampleAdd` as executable documentation.
- `for/`: demonstrates loops, constants, `strings.Builder`, and benchmarks.
- `arrays/`: moves from arrays to slices, `range`, variadic inputs, empty-slice edge cases, and `slices.Equal` (Go 1.21+), with later `Reduce`/`Find`.
- `structs/`: moves from free functions to methods, then interfaces and table tests for shapes.
- `pointers/`: uses pointer receivers for mutation, sentinel errors, and helpers like `assertBalance`, `assertNoError`, and `assertError`.
- `maps/`: grows from lookup to add/update/delete, using sentinel/custom errors and subtests for known, unknown, existing, and missing keys.

Good default progression:

1. Write one direct test for one visible behavior.
2. Hard-code the simplest result.
3. Add a second test that forces parameterization.
4. Introduce subtests and helpers once cases repeat.
5. Add error cases before broadening the API.

## Application Chapters

Use these patterns for HTTP servers, JSON APIs, file-backed stores, CLIs, time-based poker examples, and websockets.

- `http-server/`: starts with one `ServeHTTP`, then adds POST behavior, store interaction, `NewPlayerServer`, `http.NewServeMux`, an in-memory store, and integration tests.
- `json/`: adds `/league`, `application/json`, `json.NewEncoder`, `League`, and parsing helpers.
- `io/`: keeps the HTTP shape but adds filesystem persistence, JSON storage, temp-file tests, and a `tape` wrapper over `*os.File`.
- `command-line/`: splits package logic from `cmd/cli` and `cmd/webserver`, then wires the same store through both entrypoints.
- `time/`: introduces game orchestration, blind alerts, input validation, and time-sensitive tests with retry/timeout helpers.
- `websockets/`: adds `game.html`, `/ws`, live websocket integration tests, and bidirectional alert delivery.

Application design defaults:

- Keep `cmd/.../main.go` as composition root only.
- Put reusable behavior in a named package once more than one entrypoint exists.
- Define small interfaces around domain behavior: `PlayerStore`, `Game`, `BlindAlerter`.
- Use `httptest.ResponseRecorder` or `httptest.NewServer` depending on whether the test is unit-level or wiring-level.
- Use spies for interactions and temp files for persistence behavior.

## Advanced and Supporting Chapters

Use these patterns for standard-library boundary work and richer test styles.

- `di/`: inject `io.Writer` to test printing without touching stdout.
- `mocking/`: inject a `Sleeper` interface or function field; use spies to assert ordering and interaction.
- `concurrency/`: run work in goroutines, send result structs on channels, and assert all results arrive.
- `select/`: model races and timeouts with `select`, channels, and `time.After`.
- `sync/`: protect shared state with a mutex and prove it with `sync.WaitGroup`.
- `context/`: pass `context.Context` through the boundary and assert cancellation behavior with spies.
- `reflection/`: recursively walk `reflect.Value` across structs, pointers, slices, arrays, maps, channels, and functions.
- `roman-numerals/`: use a greedy ordered symbol table; back it with table tests plus `testing/quick` for round-trip properties.
- `math/`: split pure geometry from SVG rendering; assert generated XML instead of string-matching large SVGs.
- `reading-files/`: parse structured input from `fs.FS`, not hard-coded OS paths.
- `blogrenderer/`: render Markdown and templates through an `io.Writer`; use embedded templates and approval-style fixtures.
- `generics/`: introduce type parameters only for real repeated behavior; keep zero values predictable.
- `q-and-a/`: use realistic boundaries such as `errors.As`, `os/exec`, context-aware readers, and handler/service separation.

Advanced test defaults:

- For cancellation, assert the collaborator was told to stop, not only that a response returned.
- For concurrency, include a timeout so tests fail instead of hanging.
- For rendering, parse output or compare approved fixtures rather than asserting fragile full strings.
- For custom errors, assert type and behavior with `errors.Is` or `errors.As`.

## Refactoring Heuristics

- Extract helpers only after repetition is visible in tests.
- Extract interfaces only where the caller needs substitution.
- Prefer data-driven tests when behavior differs only by input and expected output.
- Prefer named subtests when failure diagnosis matters.
- Keep assertions close to the test unless a helper improves intent.
- Split pure core from adapter shell: pure calculations, then thin HTTP/CLI/file/websocket adapters.
- When adding generics, keep constraints narrow: `any` for containers, `comparable` for equality assertions or set-like behavior.
