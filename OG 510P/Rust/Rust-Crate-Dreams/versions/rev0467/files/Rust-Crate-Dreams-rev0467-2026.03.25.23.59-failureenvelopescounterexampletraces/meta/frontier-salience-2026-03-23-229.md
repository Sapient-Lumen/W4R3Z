# Frontier salience refresh (2026-03-23, pass 229)

## Main judgment

Applying the archive’s own epic-crate scorecard to the current frontier does **not** overturn the repo.
But it does clarify two things:

1. the top of the archive is still mostly **control-plane crates** that publish decisions, support contracts, or evidence bundles,
2. and **P-0538 Concurrency Contract Kit** belongs back in the top salience cluster even if the immediate ship queue still starts with pathfinder, debuggability, docs.rs parity, and build/native support.

## Salience board now

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0486 Debuggability Support Contract Kit**
3. **P-0538 Concurrency Contract Kit**
4. **P-0472 Docs.rs Build Parity & Evidence Kit**
5. **P-0535 Dependency Lifecycle Transition Kit**
6. **P-0489 Cargo Build-Dir Consumer Transition Kit**
7. **P-0484 Toolchain & Target Support Contract Kit**
8. **P-0536 Crate Knowledge Pack Kit**
9. **P-0058 Native Deps Kit**
10. **P-0046 Buildscript UX Kit**
11. **P-0537 Compile Iteration Feedback Kit**
12. **P-0125 Cargo SBOM Precursor Workbench Kit**

## Practical near-term queue now

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0486 Debuggability Support Contract Kit**
3. **P-0472 Docs.rs Build Parity & Evidence Kit**
4. **P-0489 Cargo Build-Dir Consumer Transition Kit**
5. **P-0046 Buildscript UX Kit**
6. **P-0058 Native Deps Kit**
7. **P-0538 Concurrency Contract Kit**
8. **P-0535 Dependency Lifecycle Transition Kit**
9. **P-0484 Toolchain & Target Support Contract Kit**
10. **P-0536 Crate Knowledge Pack Kit**

## Why P-0538 rises in salience without taking the first build slot

### Async is still central ecosystem pain

The March 2026 Rust challenges post says async was consistently something many users had issues with and that people using async still encounter problems, while the same post also says crate choice remains hard and that some domains still lack mature crate support.
That means a receiver-facing async/concurrency contract layer still answers a live ecosystem problem rather than a theoretical one.

### The 2026 flagship slate keeps async on the front line

Rust’s 2026 flagships still treat **Just Add Async** as a long-running flagship theme, with milestones around return type notation, async fn in dyn trait, immobile types / guaranteed destructors, and ergonomic ref-counting.
That means async ergonomics are not “solved upstream”; they are still active substrate, which strengthens the case for a crate that publishes honest support contracts above that substrate.

### Concurrency contract is broad, but not the easiest immediate ship

P-0538 scores very highly because it cuts across backend, embedded, GUI, safety-critical, and mixed-runtime work.
But it still needs scenario packs, fixture discipline, and careful claim ceilings to stay honest.
So it belongs **higher in salience** than some build lanes, while still sitting **slightly later in the immediate build queue**.

## Why the build/docs/native queue still stays ahead in shipability

Current official sources still make several build-facing seams unusually implementation-ready:
- Cargo is actively asking people to test the build-dir transition.
- Cargo still documents hard-to-read rebuild diagnostics and conservative build-script rerun behavior.
- docs.rs still documents a constrained, sandboxed environment, explicit CI/local testing advice, and concrete metadata controls.

Those are strong signs that **P-0472**, **P-0489**, **P-0046**, and **P-0058** have unusually sharp near-term product surfaces.

## Reading rule going forward

The archive should now preserve two separate judgments whenever it reranks:

1. **salience** — how much ecosystem pain and leverage the crate addresses,
2. **shipability** — how believable and reviewable the next `0.1` is under current substrate.

Do not let future passes quietly collapse those into one fake ranking.

## Sources

- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Prototype Cargo build analysis — https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build scripts reference — https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ — https://doc.rust-lang.org/cargo/faq.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
