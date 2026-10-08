# Design: Harness Protocol Contract 2026Q1

## Goal
Promote the archive's testing substrate from “interesting machine-readable test work” to a first-class **Harness Protocol Contract**: a reviewable boundary for **what subjects exist before execution, what a harness can honestly declare, what a runner may assume, and where adapter loss starts**.

This contract should sit:
- **above** raw libtest CLI behavior, nightly custom-framework mechanics, and framework-specific harness folklore;
- **below** run-result packs, coverage/fuzz/replay/device-lab attachments, and CI policy;
- and **beside** Cargo, rustdoc, and ecosystem runners rather than trying to replace any of them.

The point is not to standardize on one runner.
The point is to stop making Cargo, IDEs, CI, nextest-like runners, benchmark tools, and custom harnesses rediscover the same pre-execution truth by scraping output, cargo metadata side effects, or private conventions.

## Why this seam matters now
The case for a first-class harness contract is stronger in 2026 than it was even a year ago:
- Rust's 2026 flagship themes now explicitly include **better test tooling** under **Building blocks**, which means test infrastructure is official roadmap terrain rather than a side quest.
- The Testing Team RFC already says Rust's testing experience spans Cargo, libtest, rustdoc, IDEs, CI, and custom tools, and needs coordinated stewardship.
- The libtest JSON work is explicit that the real value is not “JSON because JSON”, but shifting reporting responsibility upward toward the runner, making custom runners more capable, and lowering the barrier for custom harnesses.
- Cargo still documents benches, doctests, and `harness = false` custom targets through a mix of stable, unstable, and caveated behavior.
- Cargo 1.94 still lists the libtest JSON experiment as unfinished work needing owners, which is strong evidence that the boundary is live design terrain.

That combination means the missing contribution is no longer “a nicer test runner”.
It is a **portable harness contract** that keeps pre-execution capability/discovery truth separate from post-execution result truth.

## References (signals)
- Rust 2026 flagships: **Building blocks** includes **better test tooling**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- RFC 3455 created a Testing Team because Rust's automated testing experience spans multiple components and teams.
  https://rust-lang.github.io/rfcs/3455-t-test.html
- The 2025H2 libtest-JSON goal says people rely on programmatic output, wants reporting to shift from harnesses to Cargo, and explicitly calls out custom runners and custom harnesses.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- Cargo 1.94 still lists finishing libtest JSON as a goal needing owners.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- `cargo test` warns that doctest execution details are not guaranteed and may change in the future.
  https://doc.rust-lang.org/cargo/commands/cargo-test.html
- `cargo bench` says Cargo passes `--bench` to either libtest or a custom harness, while the built-in `#[bench]` world remains unstable/nightly-only.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
  https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- The unstable `custom_test_frameworks` feature already exists, which proves non-libtest harnesses are real even if the stable contract is not.
  https://doc.rust-lang.org/beta/unstable-book/language-features/custom-test-frameworks.html

## Working thesis
A worthy contribution here should make it easy to answer all of these without scraping or folklore:
1. What **subjects** exist: test cases, suites, generated or parameterized cases, benches, doctests, fixtures, or setup subjects?
2. What **capabilities** does the harness claim: list, filter, markers, retries, multiple failures, locations, metric families, doctest awareness, partial discovery?
3. Which parts are **harness semantics** and which parts are **runner semantics**?
4. What does an adapter lose when it imports the harness into Cargo UX, an IDE, a CI pipeline, or an alternate runner?
5. Where do **benches** and **doctests** attach honestly without silently claiming they are just ordinary tests?
6. How can a custom harness participate without pretending it is just libtest in disguise?

If the design cannot answer those questions, then Rust still lacks the testing contract layer it needs.

## Contract shape
Read the existing kit as a contract with six visibly separate layers:

### 1) Subject-discovery truth
The contract must publish what the harness believes exists **before** execution:
- suites and case ids
- parameterized or generated expansions
- ignored/disabled posture and reasons
- source locations when available
- bench subjects and doctest subjects when supported

### 2) Capability truth
The contract must declare what consumers may rely on:
- list/filter modes
- location support
- markers/tags
- process model hints
- retry/shuffle support
- multiple-failure or captured-output support
- metric-family support
- doctest/custom-framework posture

### 3) Harness semantics
What the harness itself means by subjects, grouping, markers, filtering, benches, doctests, and suite membership.
This layer belongs to the harness, not the runner.

### 4) Runner-adapter semantics
How Cargo, nextest-like runners, IDEs, CI wrappers, or custom adapters import the harness and what they lose or reinterpret:
- id remapping
- unsupported capabilities
- flattened suites
- dropped metadata
- emulated behaviors
- lossy location or metric projection

### 5) Portable pack semantics
A thin `harness-pack/v0` should preserve capability/discovery/adapter reports together, but it must not silently become a run-result pack.
This contract is about **pre-execution truth and import posture**, not pass/fail outcomes.

### 6) Boundary-to-consumers semantics
The contract must tell downstream systems what they are entitled to conclude:
- Cargo can build UI on top of it
- IDEs can provide navigation and run affordances
- runners can import it
- benchmark tools can reuse discovery and declared metric-family truth
- doctest consumers can stay honest about instability

## What the MVP should look like in theory
A realistic v0 is not “finish the entire future of Rust testing”.
It is:
- one schema family for capabilities, discovery, adapter posture, and bundle packaging;
- one libtest exporter;
- one external-runner adapter proof;
- one non-libtest proof point;
- and one honest bench/doctest story.

Required artifacts:
- `harness-capability-report/v0`
- `harness-discovery-report/v0`
- `harness-adapter-report/v0`
- `harness-pack/v0`

Required rules:
- keep **capability** distinct from **result**;
- keep **discovery** distinct from **execution**;
- keep **harness semantics** distinct from **runner semantics**;
- keep **bench declarations** distinct from **benchmark comparisons**;
- keep **doctest posture** distinct from hosted-doc or learning proofs.

## What the MVP should look like in practice
### Pilot 1 — libtest capability/discovery export
Use ordinary Rust tests and the default harness to prove that Cargo's default lane can export explicit discovery and capability truth.

### Pilot 2 — nextest-style adapter report
Use a serious runner consumer to prove adapter lossiness can be represented honestly rather than smuggled in as “close enough”.

### Pilot 3 — custom-framework opt-in
Use one custom harness or nightly custom-test-framework lane to prove the contract is not just libtest-specific plumbing.

### Pilot 4 — benchmark subject and metric-family lane
Show that stable benchmarking ecosystems can attach without pretending benchmark-comparison policy belongs in the harness layer.

### Pilot 5 — doctest-aware lane
Show that doctest posture can be described explicitly even when execution details remain intentionally unstable.

## Why this should be promoted instead of the broader test-execution stack
The archive already has a broader **Test Execution Evidence Stack**.
That stack is still right, but the next sharpening move is **not** the whole stack at once.

Why this promotion wins now:
- official signals are strongest on the **programmatic harness/reporting boundary**, not yet on one universal run-pack standard;
- the archive already has a clean separation between harness truth and run-result truth;
- promoting the harness contract reduces future risk that result packs, JUnit bridges, nextest recordings, or CI dashboards quietly redefine the upstream surface.

So this revision promotes the **pre-execution / adapter** seam, not the entire testing stack.

## Ranking impact
This does **not** reorder the archive's top band.
It adds one more explicit Tier A/Tier B bridge beneath the current frontier map:
- Build-State Evidence stays #1 overall.
- Adoption Navigation stays #2 overall.
- Debuggability stays high.
- Semantic Context remains the clearest current **context / authority / consumer** move.
- Harness Protocol Contract becomes the clearest next **testing / runner / adapter-shaping** move.

That means it should sit below the broader build/debug/context/control-plane band, but above another round of runner-specific or benchmark-specific folklore.

## What not to build
Do **not** build:
- a new universal runner;
- a mandatory replacement for libtest or nextest;
- a fake one-format-for-all-results story;
- a benchmark policy engine hidden inside discovery reports;
- or a dashboard-first system that infers capabilities from logs.

The winning contribution is thinner and more durable:
**publish explicit harness truth, publish adapter loss honestly, and let multiple consumers reuse that without flattening the ecosystem into one tool.**
