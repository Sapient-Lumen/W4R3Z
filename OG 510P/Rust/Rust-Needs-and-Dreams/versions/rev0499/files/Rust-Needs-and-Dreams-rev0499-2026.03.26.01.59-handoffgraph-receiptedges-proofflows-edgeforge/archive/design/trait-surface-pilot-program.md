# Design: Trait Surface pilot program (native dyn, opaque-return/RTN, native async/RPITIT non-dyn, adapter dyn, split families, and solver-sensitive coverage)

## Goal
Turn **Trait Surface Kit** into a ranked pilot program that proves Rust teams can publish honest trait-family semantics without waiting for the language to settle every open trait-system question first.

This pilot should make the archive prefer **lane-aware trait packs, dyn and return-shape profiles, adapter-lossiness reports, migration notes, and solver-sensitive vectors** over another proc macro, one dyn badge, or one generic “trait readiness” summary.

## Why this now deserves a pilot
The strategic timing is unusually strong:
- Rust’s 2026 flagships keep **return type notation**, **async fn in dyn trait**, **next-solver stabilization**, and **evolvable trait hierarchies** on the active roadmap.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H1 async goal explicitly tracks **implementable trait aliases**, **async fn in dyn Trait**, and **Dynosaur 1.0** as part of the path for usable public async traits.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- The evolving-traits goal directly targets `Receiver`/`Deref` and splitting `tower::Service` into non-`Sync` and `Sync` layers.
  https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- The next-solver goal says solver replacement is intended to fix soundness issues and unblock future type-system work, which makes solver-sensitive acceptance evidence part of the real ecosystem problem.
  https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- Current crate/docs surfaces already show the lane split directly: docs.rs dyn-compatibility sections, `async-trait`, `dynosaur`, and `trait-variant` all encode different present-tense trait lanes.
  https://docs.rs/async-nats/latest/async_nats/jetstream/context/traits/trait.Requester.html
  https://docs.rs/embedded-hal-async/latest/embedded_hal_async/delay/trait.DelayNs.html
  https://docs.rs/async-trait
  https://docs.rs/dynosaur/latest/dynosaur/attr.dynosaur.html
  https://docs.rs/trait-variant/latest/trait_variant/attr.make.html

See the normative lane split in [`design/trait-surface-lane-map.md`](./trait-surface-lane-map.md).

## Pilot artifacts
The pilot should exercise a small but durable artifact family:
- `trait-surface/v0`
- `trait-semantics-profile/v0`
- `dyn-dispatch-profile/v0`
- `return-shape-profile/v0`
- `impl-coverage-profile/v0`
- `trait-adapter-profile/v0`
- `trait-vector-set/v0`
- `trait-check-report/v0`
- `trait-pack/v0`

Every stage should prefer a few small example vectors and explicit caveats over giant generated snapshots.

## Ranked rollout

### Stage 1 — native dyn baseline and docs-surface truth
Subjects:
- one clearly dyn-compatible trait with ordinary named returns
- one current docs.rs page with explicit dyn-compatibility surface

Why first:
- this establishes the baseline difference between “traits exist” and “native dyn is part of the contract”
- it gives the archive a visible docs-surface and artifact-surface alignment story
- it keeps the lane map grounded before async and opaque-return complexity arrives

Outputs:
- one baseline `trait-surface/v0`
- one `dyn-dispatch-profile/v0` showing native dyn posture
- one small vector set proving native dyn use rather than only static usage

### Stage 2 — opaque-return / RTN-bound truth
Subjects:
- one trait using `-> impl Trait` or async-return semantics where per-method bounds matter
- one Tower-style or middleware-shaped example where `Send` (or similar) changes the usable contract

Why second:
- this makes per-method return-bound truth explicit early
- it proves the archive can talk about RTN-sensitive contracts without collapsing into generic “async trait” language
- it creates a clean comparison against ordinary named-return traits

Outputs:
- one `return-shape-profile/v0`
- one vector showing method-specific bound expectations
- one note separating semantic obligations from current workaround choices

### Stage 3 — native async / RPITIT non-dyn truth
Subjects:
- one native AFIT or RPITIT trait family
- one docs-surface example showing the trait is not dyn compatible today

Why third:
- this is the most important “native but not all dispatch modes” lane
- it stops the archive from equating language-native syntax with full portability or dyn closure
- it exposes the need for later adapter and migration reporting

Outputs:
- one `trait-surface/v0` plus `dyn-dispatch-profile/v0` marked native-non-dyn
- one vector set for static success and dyn failure / unsupported posture
- one migration note pointing to later dyn-adapter stages

### Stage 4 — dyn-via-adapter comparison
Subjects:
- `async-trait`
- `dynosaur`
- optionally one small comparison with `dynify` or another stand-in if it sharpens a mismatch

Why fourth:
- this is where native and adapter dyn stories can be compared honestly
- it forces allocation / boxing / erasure / wrapper identity into the artifact family
- it creates the exact evidence users need while native dyn support is still moving

Outputs:
- one `trait-adapter-profile/v0` per adapter lane
- one vector comparing native static, adapter dyn, and unsupported cases
- one explicit lossiness note for boxing / erased / wrapper behavior

### Stage 5 — split-family / local-send / evolving hierarchy truth
Subjects:
- `trait-variant`
- one local/send trait family
- one evolving-hierarchy note such as `Receiver` / `Deref` or a Tower-style split

Why fifth:
- this is where migration and family relationships become first-class
- it keeps “base trait” versus “stricter variant” from being buried in prose
- it gives the archive an honest path for the evolving-traits roadmap without pretending it is already finished

Outputs:
- one family-oriented `trait-surface/v0`
- one `impl-coverage-profile/v0` documenting generated or blanket relationships
- one migration note covering naming and downstream impact

### Stage 6 — blanket/adaptation coverage and solver-sensitive acceptance
Subjects:
- one blanket-impl-heavy surface
- one associated-type / HRTB / next-solver-sensitive case

Why sixth:
- this is where semantic intent and currently accepted compiler behavior need to be kept distinct
- it prevents trait packs from becoming optimistic marketing documents
- it gives the archive a disciplined place for `watch`, `partial`, and `blocked` posture

Outputs:
- one `trait-check-report/v0` with compile-pass / compile-fail / watch lanes
- one vector set that keeps solver-sensitive acceptance explicit
- one explicit downstream note for what may and may not be concluded today

## Practical design rules
- Do not skip from Stage 1 straight to one universal trait schema.
- Every stage should attach at least one **semantic mismatch**, **partial**, or **unsupported** outcome so the pack proves honesty, not just success.
- Every stage should preserve exact lane meaning from [`design/trait-surface-lane-map.md`](./trait-surface-lane-map.md).
- Dyn posture should never be buried inside generic trait docs.
- If a language-native feature is still moving, say `watch` / `migration-lane` instead of implying convergence.

## What success looks like
A good pilot outcome would let a reviewer answer:
- whether the trait is static-only, native-dyn, or adapter-dyn,
- which methods impose hidden return-bound obligations,
- whether async or RPITIT syntax is native but still non-dyn,
- how local/send or base/strict families relate,
- what behavior comes from direct impls versus blanket or adapter structure,
- and what remains solver-sensitive or migration-bound.

If the pilot cannot answer those questions with artifacts, the archive is still leaning on trait folklore.

## Boundaries
- **Pointer Surface Kit** still owns receiver and pointer semantics beneath the trait surface.
- **Lending Surface Kit** still owns borrowing-aware sequence semantics above individual trait methods.
- **Compile Guidance Kit** still owns developer-facing explanations and diagnostics.
- **Borrowing Frontier Stack** imports this truth; it does not erase it.

## Near-term recommendation
Treat this pilot as the next concrete move for the broader **Borrowing Frontier Stack**: trait-surface lane truth first, then tighter pointer/lending/init cross-links after the trait lanes are made explicit rather than assumed.
