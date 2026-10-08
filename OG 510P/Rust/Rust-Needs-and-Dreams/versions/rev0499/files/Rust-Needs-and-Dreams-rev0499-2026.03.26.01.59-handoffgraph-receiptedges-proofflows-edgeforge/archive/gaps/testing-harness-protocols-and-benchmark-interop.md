> Revision note (rev0403): this gap is now promoted into the archive's explicit **testing / runner / adapter-shaping** frontier.
> Keep reading it as a gap about **pre-execution capability/discovery/adapter truth**; do not let later run-result work flatten it back into generic “machine-readable test output”.

# Gap: Testing harness protocols and benchmark interop

Rust now has real momentum around **machine-readable test output**, but the ecosystem still lacks a stable contract for what a harness can declare **before** and **during** execution:
- what tests, benches, suites, or doctest subjects exist,
- which runner semantics are expected,
- which capabilities are actually supported,
- and how custom harnesses opt into Cargo/IDE/CI UX without pretending they are just libtest clones.

That gap is now more important than it used to be.

## Why this is real now
- The Testing Team RFC says Rust’s automated testing experience spans multiple components and teams — `cargo test`, libtest, rustdoc doctests, CI, IDEs, and custom frameworks — and that the project needs a more holistic testing vision.
  https://rust-lang.github.io/rfcs/3455-t-test.html
- The libtest JSON RFC is explicit that the work is not just about pretty output. It wants Cargo to build its own UX on top of programmatic output, and it expects a future Cargo RFC so **custom harnesses can opt into the same protocol**.
  https://rust-lang.github.io/rfcs/3558-libtest-json.html
- The same RFC also says the format should be evaluated against needs like bench support, parameterized tests, dynamic skipping, test markers, doctests, test locations for IDEs, and metrics such as elapsed time and RNG seed.
  https://rust-lang.github.io/rfcs/3558-libtest-json.html
- Cargo 1.94 still lists finishing the libtest JSON experiment as a goal needing owners, which is a strong sign that the testing contract layer is still live design terrain rather than finished plumbing.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo’s own docs say `cargo bench` can drive either libtest or a custom harness, while `#[bench]` itself remains unstable/nightly-only. That means stable benchmarking already depends on ecosystem-composed harnesses and runner conventions.
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- The unstable `custom_test_frameworks` feature shows Rust already has an experimental path for non-libtest harnesses, but not a stable ecosystem-wide contract for declaring their capabilities to runners and tools.
  https://doc.rust-lang.org/beta/unstable-book/language-features/custom-test-frameworks.html

## The missing questions
Today, important testing questions are still answered by a mix of conventions, CLI scraping, or tool-specific behavior:
1. **What subjects exist?** tests, benches, doctests, fixtures, parameterized cases, setup scripts, generated cases, and suites are not described through one portable discovery/report layer.
2. **What can a runner assume?** parallel execution, retries, markers, ignored reasons, multiple failures, bench metrics, doctest handling, and location data are not exposed through one explicit capability contract.
3. **How should custom harnesses participate?** nightly custom frameworks exist, but there is no stable, reviewable opt-in boundary for Cargo/nextest/IDE consumers.
4. **Where do benchmarks fit?** `cargo bench` can call custom harnesses, but the stable benchmarking story still routes through ecosystem tools like Criterion or Divan instead of one shared harness contract.
5. **How do doctests join the picture honestly?** Cargo’s docs explicitly say doctest execution details are not guaranteed and may change, which means doctest support needs capability declarations rather than folklore assumptions.
  https://doc.rust-lang.org/cargo/commands/cargo-test.html

## What a worthy contribution would look like
A strong contribution here is **not**:
- another universal test runner,
- another benchmark engine,
- another XML bridge,
- or a demand that everything become libtest.

A strong contribution is a **reviewable harness contract** that can describe:
- discovery surfaces,
- suite/case hierarchy,
- capability declarations,
- runner-adapter posture,
- and metric/schema extensions,

while letting libtest, nextest, Criterion, Divan, doctest lanes, and future custom frameworks keep their own semantics.

## Why this deserves its own kit instead of living inside test-run evidence
`cargo testrun`-style work answers **what ran and what happened**.
That is necessary, but it is not the same as answering:
- what the harness can expose,
- what the runner may assume,
- how benches or doctests appear,
- and how custom frameworks opt into a shared UX.

Those questions belong to a separate boundary.

## Winning shape
The winning version is:
- capability-first,
- adapter-friendly,
- explicit about benches/doctests/custom frameworks,
- and narrow enough that Cargo, nextest, IDEs, CI, and ecosystem harnesses can adopt it incrementally.
