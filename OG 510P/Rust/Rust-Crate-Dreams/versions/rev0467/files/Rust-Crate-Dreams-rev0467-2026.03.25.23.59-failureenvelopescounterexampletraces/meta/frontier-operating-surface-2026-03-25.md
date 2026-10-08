# Frontier operating surface — 2026-03-25

This note sharpens the current frontier without changing its broad shape.

The archive already knew the top lanes should emit packets.
This pass adds the missing question:

**What is the operating surface that lets another team actually run those packets, re-run them later, and know what still counts as true?**

That sharper missing layer is the **operating surface**.

## Definition

An operating surface is the smallest honest combination of:
- receiver,
- repeated question,
- imported inputs,
- runner and cadence,
- artifact family,
- recheck trigger vocabulary,
- scenario corpus,
- and refusal boundary.

Without that combination, a crate may still be interesting.
It is not yet a strong near-term ecosystem contribution.

## Why this got stronger now

Because the official ecosystem increasingly exposes machine-usable substrate:
- crates.io exposes Security-tab posture, Trusted Publishing posture, SLOC, and `pubtime`;
- docs.rs exposes build recipe facts, metadata knobs, documentation archives, and rustdoc JSON;
- Cargo goal work keeps moving toward build analysis, programmatic test output, clearer build-dir semantics, and better API-boundary substrate;
- and safety-critical / Rust-for-Linux / build-script work all emphasize stable tooling, evidence, and bounded behavior.

The missing value is no longer only “collect information”.
It is “collect, freeze, rerun, explain drift, and stop before overclaiming”.

## The operating spine for the current frontier

### 1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**

#### Repeated question
Which crate or crate stack best fits *this* task profile under *this* evidence floor?

#### Imported surfaces
- crates.io trust/timing/size surfaces
- docs.rs metadata/build/download/rustdoc JSON surfaces
- local `cargo metadata` / lock / manifest state
- manually imported policy or target notes when required

#### First operators
- individual engineer during evaluation
- tech lead during review
- CI or scheduled recheck job for drift

#### First commands
- `cargo pathfinder intake`
- `cargo pathfinder compare`
- `cargo pathfinder freeze`
- `cargo pathfinder recheck`
- `cargo pathfinder summary`

#### First artifact family
- `task-profile.json`
- `candidate-import.json`
- `decision-pack.json`
- `starter-set.lock.json`
- `recheck-ticket.json`
- `decision-revalidation.report.json`
- `decision-summary.md`

#### First scenario families
- greenfield web task
- air-gapped enterprise intake
- alternate-registry or mirror-aware choice
- regulated boundary-narrowing choice
- same task under different policy profiles

#### Claim ceiling
Pathfinder should claim **reviewable recommendations**, not universal choice automation.

### 2. **P-0536 Crate Knowledge Pack Kit**

#### Repeated question
What pinned evidence basis supports this recommendation or support claim?

#### Imported surfaces
- docs.rs build metadata
- docs.rs download archive routes
- docs.rs rustdoc JSON routes
- packaged crate witnesses and repository witnesses where available

#### First operators
- reviewer or release engineer
- tooling that materializes a frozen evidence pack

#### First commands
- `cargo knowledge import`
- `cargo knowledge pin`
- `cargo knowledge materialize`
- `cargo knowledge diff`
- `cargo knowledge cite`

#### First artifact family
- `basis-lock.manifest.json`
- `citation-locator.json`
- `build-surface.report.json`
- `target-surface.report.json`
- `knowledge-summary.md`

#### First scenario families
- hosted docs differ from local build
- floating `latest` route differs from pinned version
- rustdoc JSON exists but version parsing changes
- download archive is available but still needs further processing offline

#### Claim ceiling
Knowledge Pack should claim **pinned witness bundles**, not final task-fit judgment.

### 3. **minimal P-0535 Dependency Lifecycle Transition Kit**

#### Repeated question
What changed since the frozen answer, and does that change require keep/pin/exception/re-evaluate/migrate/replace?

#### Imported surfaces
- advisories
- new releases and yanks
- source / registry route changes
- previously frozen decision and knowledge artifacts

#### First operators
- maintainer
- dependency steward
- CI or scheduled continuity job

#### First commands
- `cargo continuity intake`
- `cargo continuity revalidate`
- `cargo continuity transition`
- `cargo continuity summary`

#### First artifact family
- `trigger-intake.receipt.json`
- `decision-revalidation.report.json`
- `transition-plan.json`
- `continuity-summary.md`

#### First scenario families
- advisory with no replacement yet
- version bump with no policy change
- yank or publication anomaly
- alternate-registry divergence

#### Claim ceiling
Lifecycle should claim **reviewable rechecks and transition routes**, not automatic maintenance truth.

### 4. **P-0472 Docs.rs Build Parity & Evidence Kit**

#### Repeated question
What does docs.rs show, what recipe produced it, and how does that compare to local or intended package reality?

#### First outputs
- `docsrs-preflight.report.json`
- `hosted-local-diff.report.json`
- `docsrs-parity-summary.md`

#### Why it matters
Because docs.rs uses nightly, sandboxed builds, configurable targets/features, and target defaults that may differ from a maintainer’s local assumptions.

### 5. **P-0484 Toolchain & Target Support Contract Kit**

#### Repeated question
What target/toolchain/components claim is actually supportable for this crate or stack?

#### First outputs
- `target-support.report.json`
- `component-availability.report.json`
- `support-ceiling.note.md`

#### Why it matters
Because cross-target truth, build-std, Rust-for-Linux, and safety-critical tooling realities all sharpen the gap between “builds somewhere” and “supportable promise”.

### 6. **P-0486 Debuggability Support Contract Kit**

#### Repeated question
What debugging support exists for this crate/stack across debugger, version, operating system, async mode, and type presentation?

#### Why it stays slightly later
It remains highly salient, but it should inherit the same operating-model discipline:
- named runner,
- explicit corpus,
- and bounded debugger/OS/version ceilings.

## Most buildable next slice

The strongest next slice is still not a giant new lane.
It is to make the front door and frozen basis runnable as one operating surface:

1. **Pathfinder** chooses and freezes.
2. **Knowledge Pack** pins the witness basis.
3. **Lifecycle intake** reopens that basis only on named triggers.
4. **Docs/target imports** enrich rechecks without pretending to settle them automatically.

That slice is both broad in receiver value and narrow enough for a truthful `0.1`.

## What a worthy crate should provide other people here

At minimum, the crate should give another team:
- a repeated operating answer,
- not just a one-time report;
- a pinned basis,
- not just live-page impressions;
- a rerun path,
- not just a past conclusion;
- a small golden corpus,
- not just persuasive examples;
- and a refusal boundary,
- not just smooth wording.

## Refusal boundary

An operating-surface crate should explicitly refuse to claim:
- universal compatibility,
- complete supply-chain safety,
- complete semver or support truth from one source alone,
- or enterprise qualification without imported policy/evidence.

## One-sentence takeaway

The next worthy crate contribution is increasingly the one that turns Rust ecosystem signals into a runnable, reviewable operating loop for other teams.
