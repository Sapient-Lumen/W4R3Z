> Revision note (rev0403): read this proposal now as the epic shell for a **Harness Protocol Contract**.
> The promoted seam is **pre-execution capability/discovery/adapter truth**, not a universal runner and not a run-result format.
> The strongest current sources are the 2026 **better test tooling** flagship signal, RFC 3455 (Testing Team), the libtest-JSON goal, Cargo 1.94's unfinished-work note, and Cargo's still-uneven bench/doctest/custom-harness surface.

# Epic Proposal: Harness Protocol Kit (`cargo harness`)

## One-sentence pitch
Give Rust a portable harness contract so tests, benches, doctests, and custom frameworks can publish capability/discovery truth that Cargo, runners, IDEs, and CI can consume without scraping output or standardizing on one runner.

## Deliverables
- `cargo-harness` reference implementation
- Schemas:
  - `harness-capability-report/v0`
  - `harness-discovery-report/v0`
  - `harness-adapter-report/v0`
  - `harness-pack/v0`
- Adapters:
  - libtest capability/discovery export
  - nextest adapter report
  - custom-framework experiment lane
  - benchmark subject / metric-family export
  - doctest posture import lane
- Docs:
  - runner-adapter guide
  - capability reason-code reference
  - harness-pilot-program guide

## Why now (signals)
- The Testing Team RFC says Rust needs an overarching vision for testing across Cargo, libtest, rustdoc, IDEs, CI, and external tools.
  https://rust-lang.github.io/rfcs/3455-t-test.html
- The libtest JSON RFC explicitly wants Cargo UX to sit on top of programmatic output and anticipates a future Cargo RFC so custom test harnesses can opt into that protocol.
  https://rust-lang.github.io/rfcs/3558-libtest-json.html
- The same RFC names bench support, parameterization, dynamic skipping, test markers, doctests, locations, and metrics as design-relevant capabilities.
  https://rust-lang.github.io/rfcs/3558-libtest-json.html
- Cargo still documents `#[bench]` as unstable while allowing `cargo bench` to drive custom harnesses, which is strong evidence that benchmark interop needs a portable contract rather than another one-off convention.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- Cargo 1.94 still lists the libtest JSON experiment among live needs without owners.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Non-goals
- Replacing libtest, nextest, Criterion, Divan, or rustdoc
- Forcing every test/bench tool onto one execution engine
- Owning final pass/fail evidence or CI matrices
- Claiming benchmark-comparison policy
- Pretending doctest behavior is more stable than it really is

## Strategic value
This kit has high leverage because it supplies the missing upstream boundary for:
- Cargo `test` / `bench` UX,
- nextest and future runner experiments,
- custom frameworks,
- IDE test/bench navigation,
- doctest-aware consumers,
- and benchmark-oriented ecosystems.

It makes the testing ecosystem more composable **without** requiring consensus on one runner or one harness.

## Milestones
1. **Pilot 1 / v0**
   - libtest capability + discovery export
   - unstable/stable capability reason codes
2. **Pilot 2 / v0.2**
   - nextest adapter reports
   - explicit lossiness notes
3. **Pilot 3 / v0.3**
   - custom-framework opt-in experiment
   - partial-capability support
4. **Pilot 4 / v0.4**
   - benchmark subject + metric-family lane
   - stronger boundary with Perf Labs
5. **v1**
   - doctest posture import
   - IDE-facing location support
   - tighter guidance for Cargo integration proposals

## What success looks like
- Cargo can explain more of test/bench behavior through declared capabilities instead of tool-specific folklore.
- nextest can consume shared discovery/capability truth without becoming the only de facto standard.
- Custom frameworks can participate without pretending to be just hidden libtest wrappers.
- Bench and doctest lanes gain honest integration points instead of being perpetually “special cases”.

## Execution order
For the ranked rollout order, see `design/harness-protocol-pilot-program.md`.
