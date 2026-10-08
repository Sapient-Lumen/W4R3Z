# Epic Proposal: Debugger Experience Kit (`cargo debugx`)

## One-sentence pitch
Make Rust debugging feel like a supported product surface by standardizing debugger capability reports, visualizer packs, async-debug adapter profiles, expression-evaluation posture, and issue-attachable repro packs.

## Why this is worthy
Debugging is still one of Rust’s durable pain points, and the Rust project is now explicitly treating it as such. The 2026 debugging survey says stellar support should span multiple debugger versions and operating systems, quality visualizers, first-class async debugging, and Rust-expression evaluation. The 2025 State of Rust survey still shows debugging among the leading productivity problems.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

This is therefore not just polish for one IDE plugin. It is ecosystem infrastructure for making debugging support:
- testable,
- releasable,
- discussable in issue reports,
- and resilient to debugger releases and std-layout changes.

## Why now
Rust has enough substrate pieces that convergence is finally realistic:
- the toolchain already ships debugger wrappers and visualizer support scripts;
- the `debugger_visualizer` attribute is a stable public hook for embedding visualizer files;
- the compiler-dev-guide now documents visualizer internals, limitations, LLDB gaps, and performance concerns;
- Tokio Console and `console-subscriber` prove that runtime-specific async inspection can be real and useful, but they also show the current fragmentation and instrumentation burden.
  https://doc.rust-lang.org/reference/attributes/debugger.html
  https://rustc-dev-guide.rust-lang.org/debuginfo/debugger-visualizers.html
  https://docs.rs/console-subscriber/latest/console_subscriber/
  https://docs.rs/crate/tokio-console/latest

Execution anchor: use `design/debugger-pilot-program.md` as the ranked rollout plan so tuple truth, crate visualizer release lanes, async inspection, expression posture, and downstream compatibility consumers stay distinct.

## Deliverables
- `cargo-debugx` reference implementation
- Schemas:
  - `debug-profile/v0`
  - `debug-capability-report/v0`
  - `viz-pack/v0`
  - `async-debug-profile/v0`
  - `expr-eval-profile/v0`
  - `debug-battery-report/v0`
  - `debug-pack/v0`
- Reference assets:
  - std/container battery scenarios
  - crate-visualizer reference examples
  - Tokio async adapter profile
- CI templates:
  - debugger battery runs
  - release attachment workflow for visualizer packs
  - issue template expecting `debug-pack/v0`

## Strategic value
This contribution would help at least four groups at once:
- **application teams** get clearer debugger setup and reproducible bug reports;
- **library maintainers** can ship visualizer support as a first-class ergonomics artifact;
- **IDE/debug-adapter authors** gain structured inputs instead of reverse-engineering every setup story;
- **toolchain/compiler teams** gain regression-testable evidence when debugger support silently breaks.

That is unusually broad leverage for a developer-experience investment.

## Non-goals
- Building a new debugger or replacing native debugger projects.
- Defining a universal debugger protocol beyond existing adapters.
- Claiming full async-debugging parity across runtimes.
- Freezing internal std layouts.
- Hiding unsupported tuples behind a marketing badge.

## Milestones
1. **v0 — capability truth + repro packs**
   - `debug-profile/v0`
   - `debug-capability-report/v0`
   - `debug-pack/v0`
   - initial Linux/macOS/Windows tuple battery

2. **v0.2 — visualizer artifact lane**
   - `viz-pack/v0`
   - std/container scenarios
   - crate-shipped visualizer examples
   - release attachment templates

3. **v0.3 — async-debug adapter lane**
   - `async-debug-profile/v0`
   - Tokio adapter profile and battery coverage
   - explicit separation of native debugger vs side-channel console support

4. **v1 — richer compatibility and expression posture**
   - `expr-eval-profile/v0`
   - stronger debugger-version compatibility dashboards
   - broader ecosystem adoption by IDE/debug-adapter and library authors

## Adoption strategy
Start where the substrate is strongest:
- std/container visualizers,
- toolchain wrappers already shipped by Rust,
- Tokio async inspection,
- issue-attachable repro packs.

Only then widen toward broader runtime families, IDE integrations, and richer expression-evaluation expectations.
