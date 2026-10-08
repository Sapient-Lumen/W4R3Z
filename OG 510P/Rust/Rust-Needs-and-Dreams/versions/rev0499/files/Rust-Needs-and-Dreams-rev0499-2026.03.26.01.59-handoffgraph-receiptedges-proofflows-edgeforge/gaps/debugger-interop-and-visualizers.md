# Gap: Debugger interop, visualizer coverage, async-runtime inspection, and debugger capability truth

## Summary
Rust now has clearer upstream intent around debugging, but the ecosystem still lacks a boring, reviewable substrate for saying **what debugging experience a project actually supports** across debugger families, operating systems, toolchains, standard-library layouts, and async-runtime styles.

That missing layer matters because Rust no longer lacks raw ingredients:
- the compiler team’s 2026 debugging survey says “stellar debugging” should include support for multiple debugger versions across GDB/LLDB/CDB on multiple operating systems, high-quality visualizers, first-class async debugging, and Rust-expression evaluation;
- the 2025 State of Rust survey still lists debugging among the leading non-trivial productivity problems;
- the Rust toolchain already ships `rust-gdb`, `rust-lldb`, and `rust-windbg.cmd` support scripts, and Rust now has a stable `debugger_visualizer` attribute for embedding visualizer files into debug information;
- Tokio Console and `console-subscriber` already prove that async debugging can use explicit runtime instrumentation and a wire protocol instead of remaining pure folklore.

What is still missing is the shared contract layer above those pieces.

## Why the existing toolbox is not enough
The current ecosystem is not one thing called “Rust debugging.” It is several partially overlapping lanes:
- debugger wrappers and pretty printers shipped with the toolchain,
- debugger-family-specific visualizer formats (GDB Python, Natvis, LLDB formatters),
- IDE/debug-adapter translations layered above those debugger outputs,
- runtime-specific async-inspection surfaces,
- and project-specific repro instructions scattered across issue templates, README notes, and maintainer memory.

The 2026 debugging survey is unusually direct that support quality varies significantly across debuggers and operating systems, and that internal representation changes in the standard library or debugger releases can silently break the experience.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

The Rust compiler development guide makes the same point from the implementation side:
- the Rust toolchain ships launcher scripts that preload Rust visualizers,
- visualizers often have to reconstruct useful synthetic children from low-level debug info,
- `#![debugger_visualizer]` currently works for GDB and Natvis,
- LLDB support is still a different and unresolved story,
- and visualizer performance matters because debugger UIs may request whole frames at once.
  https://rustc-dev-guide.rust-lang.org/debuginfo/debugger-visualizers.html
  https://doc.rust-lang.org/reference/attributes/debugger.html

Async debugging is also clearly real, but fragmented. `console-subscriber` and `tokio-console` already define a real instrumentation/consumer split, but currently require runtime support, Tokio tracing instrumentation, and `tokio_unstable` configuration for richer functionality. That proves the value of explicit async-debug metadata, while also proving that a portable cross-runtime contract is still missing.
  https://docs.rs/console-subscriber/latest/console_subscriber/
  https://docs.rs/crate/tokio-console/latest

## Concrete missing pieces
1. **Debugger capability matrices**
   - Which debugger family/version/OS/toolchain tuples are actually supported?
   - Which tuples can render std collections well?
   - Which tuples can step async frames reasonably?
   - Which tuples can evaluate Rust expressions, and with what limitations?

2. **Versioned visualizer coverage artifacts**
   - Which std or crate types have tested visualizers?
   - Which debugger families consume them?
   - Which std/runtime layout versions were the visualizers validated against?
   - What performance or depth limits apply?

3. **Async-runtime debug adapter profiles**
   - Which runtime emits inspectable task/resource metadata?
   - What instrumentation flags or features are required?
   - What is native debugger support versus side-channel console/tracing support?
   - Which task/resource IDs, state labels, and source locations are exposed?

4. **Expression-evaluation posture**
   - Can a given stack support Rust expression evaluation at all?
   - Is it native, adapter-based, or absent?
   - Which language fragments are expected to work?
   - What safety/performance caveats apply?

5. **Issue-attachable repro packs**
   - minimized repro sources,
   - debugger/toolchain/OS profile,
   - symbol and debuginfo posture,
   - expected vs actual visualization behavior,
   - optional async instrumentation and session transcript attachments.

## Desired properties
- **Capability truth, not fake parity.** A good design must let “works on GDB/Linux, partial on LLDB/macOS, unsupported on CDB” remain explicit.
- **Visualizer support should be a releasable artifact.** The ecosystem should stop treating visualizer scripts as hidden incidental files.
- **Async inspection should be adapter-based.** The contract must allow runtime-specific adapters instead of pretending all runtimes expose the same task model.
- **Expression evaluation must be described honestly.** “No support yet” is better than implying full debugger parity.
- **Regression testing must be routine.** Debugging support should survive debugger upgrades and std-layout shifts because there is a portable battery and report layer, not because one maintainer remembers to check.

## Distinction from nearby archive entries
- **Diagnostic Surface Kit** is about failure messages and renderings in the running program or API surface. This gap is about interactive debugging support in external debugger tooling.
- **Replay Kit** captures failing executions for reproduction. This gap captures debugger capability/support truth and debugger-specific repro attachments.
- **Synchronization Surface Kit** and **Async Lifecycle Kit** describe concurrency semantics. This gap is about how those semantics become visible to debuggers and async-inspection tools.
- **Terminal Surface Kit** covers terminal I/O/render/input semantics. This gap covers debugger UX and visualizer contracts above debuginfo.

## Why this would be worthy
A good debugger-experience substrate would not merely make one plugin nicer. It would:
- lower one of the ecosystem’s durable productivity pain points;
- convert debugger support from lore into testable compatibility claims;
- give crate authors a real way to ship visualizer support as part of public ergonomics;
- make async-runtime inspection composable instead of Tokio-only folklore;
- and help toolchain teams catch debugger regressions before users rediscover them one bug report at a time.

That is exactly the sort of boring, ecosystem-shaping contribution the Rust ecosystem is still missing.
