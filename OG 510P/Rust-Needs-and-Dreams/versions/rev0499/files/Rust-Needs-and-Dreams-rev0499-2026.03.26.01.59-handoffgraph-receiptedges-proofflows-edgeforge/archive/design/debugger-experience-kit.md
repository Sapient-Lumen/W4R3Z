# Design: Debugger Experience Kit (`cargo debugx` + `debug-pack/v0`)

## Goal
Make Rust debugging portable, reviewable, and regression-testable by standardizing the shared contract layer above existing debuggers, visualizers, IDE adapters, and async-runtime inspection tools.

This should **not** replace GDB, LLDB, CDB/WinDbg, CodeLLDB, RustRover, Tokio Console, or debugger-adapter protocols. It should make their support claims legible and testable.

## References (signals)
- Rust debugging survey 2026:
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust Reference — `debugger_visualizer`:
  https://doc.rust-lang.org/reference/attributes/debugger.html
- Rust compiler development guide — debugger visualizers:
  https://rustc-dev-guide.rust-lang.org/debuginfo/debugger-visualizers.html
- `console-subscriber` docs:
  https://docs.rs/console-subscriber/latest/console_subscriber/
- `tokio-console` docs:
  https://docs.rs/crate/tokio-console/latest

## Problem framing
Today’s Rust debugging experience is split across at least five layers:
1. debugger family and version (`gdb`, `lldb`, `cdb`/WinDbg),
2. target OS + debuginfo format,
3. toolchain wrappers and standard visualizers,
4. crate- or project-supplied visualizers,
5. runtime-specific async instrumentation and IDE/debug-adapter presentation.

Projects routinely collapse all of that into one misleading statement like “debugging works” or “CodeLLDB supported.”

The kit should instead make support a structured object:
- what tuple was tested,
- what type families render well,
- what async metadata is available,
- whether expression evaluation works,
- and what repro pack demonstrates a bug or success case.

## Core UX: `cargo debugx`
### `cargo debugx doctor`
Print a support summary for the local tuple:
- debugger family/version discovered,
- target triple and debuginfo posture,
- visualizer sources loaded,
- async adapter availability,
- known limitations and likely missing prerequisites.

### `cargo debugx capability`
Emit a machine-readable `debug-capability-report/v0` for CI, issue attachments, or release notes.

### `cargo debugx viz export`
Export a `viz-pack/v0` containing project visualizers, tested coverage metadata, version bounds, and checksums.

### `cargo debugx async export`
Emit an `async-debug-profile/v0` describing runtime instrumentation requirements and exposed task/resource metadata.

### `cargo debugx pack`
Bundle a minimized debugger repro into `debug-pack/v0`.

### `cargo debugx battery`
Run a debugger compatibility battery over selected tuples and produce a `debug-battery-report/v0`.

## Artifact family
### 1) `debug-profile/v0`
Describes the debugging environment for a build or repro.

Fields:
- toolchain version / channel / commit hash when available
- target triple
- platform / debuginfo format (`DWARF`, `PDB`, etc.)
- profile settings relevant to debugging:
  - debuginfo level
  - split-debuginfo
  - LTO
  - optimization profile
  - strip posture
- debugger family and version
- wrapper used (`rust-gdb`, `rust-lldb`, `rust-windbg.cmd`, direct invocation, IDE adapter)
- symbol file locations or references
- workspace/crate identity

### 2) `debug-capability-report/v0`
Machine-readable answer to “what does this tuple support?”

Capabilities:
- `std_visualizers`
- `crate_visualizers`
- `synthetic_children`
- `async_task_visibility`
- `async_resource_visibility`
- `rust_expr_eval`
- `breakpoint_basic`
- `conditional_breakpoints`
- `backtrace_quality`
- `source_loc_accuracy`
- `watch_expressions`

Each capability should record:
- `supported` / `partial` / `unsupported`
- evidence source (`battery`, `manual`, `imported`, `assumed`)
- tested debugger/version/OS/toolchain tuple
- notes and known caveats

### 3) `viz-pack/v0`
Portable visualizer bundle.

Contents:
- raw visualizer files (Natvis, GDB scripts, future LLDB formatters or generated equivalents)
- manifest of covered type families
- source of truth (`toolchain`, `crate`, `generated`, `hand-authored`)
- std/runtime layout compatibility bounds
- optional performance notes:
  - expected expansion depth limits
  - known slow types/paths
- checksums and provenance

Design rule: a visualizer pack is a releasable ergonomics artifact, not a hidden miscellaneous file.

### 4) `async-debug-profile/v0`
Describes async-inspection posture.

Fields:
- runtime identity (`tokio`, `async-std`, `smol`, custom, none)
- adapter identity (`console-subscriber`, custom adapter, none)
- instrumentation prerequisites:
  - crate features
  - cfg flags
  - env vars
  - tracing targets / levels
- exposed entities:
  - task ids
  - task names
  - spawn locations
  - task states
  - resource identities
  - wait relationships where available
- transport/wire posture
- stability notes / experimental status
- supported versions and gaps

This must allow “Tokio + unstable tracing + console wire protocol” to be expressed honestly instead of pretending async debugging is native and universal.

### 5) `expr-eval-profile/v0`
Records Rust-expression-evaluation posture.

Fields:
- evaluator origin (`native debugger`, `adapter`, `none`)
- supported expression fragments (field access, indexing, simple arithmetic, method calls, trait-based pretty views, etc.)
- limitations
- side-effect posture
- performance notes
- known unsupported constructs

### 6) `debug-battery-report/v0`
CI/test artifact for compatibility runs.

Fields:
- matrix of tuples tested
- test scenarios:
  - std containers
  - enums / options / results
  - crate-specific visualizers
  - async task listing
  - async resource listing
  - expression-eval smoke tests
- result status (`pass`, `fail`, `flaky`, `unsupported`)
- screenshots/log pointers if present
- regression classification against prior battery run

### 7) `debug-pack/v0`
Portable repro pack for issues and release verification.

Contents:
- `debug-profile.json`
- optional `debug-capability-report.json`
- optional `viz-pack/`
- optional `async-debug-profile.json`
- optional `expr-eval-profile.json`
- minimized repro source or pointer
- debugger invocation transcript
- expected vs actual behavior note set
- optional screen capture pointers or stack snapshots
- issue metadata / bug-class tags

## Reference workflows
### A. Library shipping custom visualizers
1. author visualizer files using `debugger_visualizer` where possible;
2. run `cargo debugx viz export`;
3. run battery tests on supported tuples;
4. attach `viz-pack/v0` and `debug-battery-report/v0` to release or CI;
5. downstream users can see which debugger families were actually tested.

### B. Async service with Tokio Console integration
1. instrument runtime with `console-subscriber` / tracing settings;
2. export `async-debug-profile/v0`;
3. record which task/resource fields are visible and which require unstable flags;
4. attach those facts to docs, CI, and issue repro packs rather than burying them in setup lore.

### C. Regressed debugger support after toolchain upgrade
1. run `cargo debugx battery` before and after;
2. diff `debug-battery-report/v0` and `debug-capability-report/v0`;
3. attach the resulting `debug-pack/v0` to upstream bug reports;
4. preserve whether the regression came from a debugger update, std layout change, or visualizer break.

## Integration points
- **Replay Kit:** reuse minimized repros and transcripts when a debugger bug accompanies a runtime failure.
- **Diagnostic Surface Kit:** failure renderings and debugger support stay separate but can be attached together for issue triage.
- **Synchronization Surface Kit / Async Lifecycle Kit:** define the concurrency semantics; `async-debug-profile/v0` records how much of that truth is observable.
- **Terminal Surface Kit:** terminal capabilities matter for TUI debug consumers like Tokio Console but remain a separate concern.
- **Release Pipeline Kit:** projects may attach `viz-pack/v0` and compatibility reports as release artifacts for developer-facing ergonomics.

## Design principles
1. **Model tuples, not brands**
   - Support is a property of debugger version + OS + toolchain + target + adapter, not just “LLDB”.

2. **Separate native debugger truth from side-channel async inspection**
   - Tokio Console-style views are valuable, but they are not the same thing as native stepping/backtrace/debugger-expression support.

3. **Treat visualizers as performance-sensitive product code**
   - The dev guide is explicit that visualizers can become painfully slow. Coverage without latency truth is incomplete.

4. **Let unsupported stay unsupported**
   - The kit should be comfortable reporting gaps rather than claiming complete parity.

5. **Prefer attachable evidence over anecdote**
   - A debugger regression report should come with a `debug-pack/v0`, not only a screenshot and “it used to work.”

## Non-goals
- Building a new debugger.
- Standardizing one universal visualizer format in v0.
- Pretending async runtimes expose one shared task/resource model.
- Replacing IDE-specific UX or debug-adapter protocols.
- Guaranteeing Rust-expression evaluation parity before the substrate exists.

## Evaluation plan
Use [`design/debugger-pilot-program.md`](./debugger-pilot-program.md) as the ranked execution layer above this design.

Pilot on three tracks:
1. **std/container track**
   - `Vec`, `String`, maps, sets, options/results, nested enums.
2. **crate visualizer track**
   - at least one library shipping custom visualizers via `debugger_visualizer` / Natvis / GDB script.
3. **async track**
   - Tokio task/resource visibility with explicit instrumentation requirements.

Initial tuple matrix:
- Linux + GDB
- Linux + LLDB
- macOS + LLDB
- Windows MSVC + CDB/WinDbg or Visual Studio-compatible Natvis lane

Success bar for v0:
- projects can publish a real capability matrix instead of vague debugger claims,
- visualizer support can ship as a reviewable artifact,
- async-debug requirements are explicit,
- and upstream bug reports can carry portable repro packs.
