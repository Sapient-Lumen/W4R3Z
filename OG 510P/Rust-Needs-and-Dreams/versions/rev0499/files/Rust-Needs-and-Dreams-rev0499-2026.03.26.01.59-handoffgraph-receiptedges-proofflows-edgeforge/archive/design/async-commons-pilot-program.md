# Design: Async Commons pilot program (`cargo async-commons pilot`, `async-commons-pilot-pack/v0`)

## Why this needs a pilot program
The archive can already describe async lifecycle and reliability, but the missing question is now lower-level and more strategic:
**how does Rust reduce needless async runtime lock-in without pretending runtimes are identical or that all async lanes are equally shared?**

Current signals argue for staged rollout:
- the March 20, 2026 challenges post says async often feels like a separate programming model and explicitly identifies library choices that lock users into a runtime family;
- the 2025H1 async goal says runtime choice and runtime interoperability are still central pain points;
- the July 2025 project-goals update says progress on async traits and generators/streams is meant to unblock the next generation of async libraries;
- the Async Book still says runtime compatibility constraints and higher maintenance burden are part of reality;
- and the ecosystem already has real but partial shared substrate (`Future`, `Spawn` / `LocalSpawn`, `futures-io`) plus real runtime-shaped surfaces (Tokio task/time/I/O, Embassy embedded executors).

That means the next credible contribution is not a universal façade.
It is a **lane-aware proof** that shared substrate, capability profiles, adapters, and `watch` seams can be published honestly.

Read [`design/async-commons-lane-map.md`](./async-commons-lane-map.md) as the rule for what must stay separate.

## Pilot principles
1. **Start where adapters already prove the seam is real.** I/O is a better first lane than abstract ecosystem philosophy.
2. **Prefer capability declarations over fake uniform APIs.** Many libraries need to state spawn/time/local requirements more than they need one universal interface.
3. **Prove one environment contrast early.** Server-runtime and embedded/no-alloc async should not remain hidden under one portability sentence.
4. **Publish at least one explicit `watch` verdict.** Streams/async-sequences matter enough to model, but not enough to flatten today.
5. **Consumers must import the result.** Async Commons only matters if another stack uses it.

## Candidate artifact flow
### `async-lane-profile/v0`
Used first to say which lane is being piloted and what its readiness class is.

### `async-seam/v0`
Used to declare the exact seam and problem scope.

### `async-capability-profile/v0`
Used to declare what a crate or lane actually requires.

### `async-common-surface/v0`
Used to describe the neutral shared vocabulary being claimed.

### `async-adapter-profile/v0`
Used to make runtime/crate mapping and lossiness explicit.

### `async-readiness-report/v0`
Used to publish `promote` / `pilot` / `watch` / `defer` judgments honestly.

### `async-commons-pilot-scorecard/v0`
Should ask:
- did the pilot preserve lane identity honestly?
- did it clarify capabilities instead of waving at portability?
- did it surface at least one real negative or lossy edge?
- did it keep environment posture explicit?
- did one downstream consumer use the exported artifact?
- is widening justified?

## Ranked pilots

### 1) I/O lane pilot
**Why first**
- Rust already has neutral-ish I/O vocabulary in `futures-io` and strong runtime-shaped I/O surfaces in Tokio.
- `tokio-util::compat` proves the adapter problem is real and concrete.
- This is the best first pilot for showing neutral core plus explicit adapter truth.

**Core artifacts**
- `async-lane-profile/v0`
- `async-seam/v0`
- `async-common-surface/v0`
- `async-adapter-profile/v0`
- `async-vector-set/v0`
- `async-readiness-report/v0`

**Acceptance bar**
- The pilot can say which I/O semantics are actually shared, which adapter paths are lossy or partial, and which scenarios are tested.

### 2) Spawn + local capability pilot
**Why second**
- Many async libraries mostly need to say whether they require generic spawning, local spawning, blocking escape hatches, or a specific runtime family.
- The `Send` versus local split is one of the highest-value portability truths to make explicit.

**Core artifacts**
- `async-lane-profile/v0`
- `async-capability-profile/v0`
- optional `async-adapter-profile/v0`
- `async-readiness-report/v0`

**Acceptance bar**
- A library can publish honest executor/local requirements without collapsing them into a fake “works on all runtimes” sentence.

### 3) Time / deadline capability pilot
**Why third**
- Timer requirements are common, strategically important, and not actually a finished shared substrate.
- This lane proves the kit can model a capability requirement without overselling semantic uniformity.

**Core artifacts**
- `async-lane-profile/v0`
- `async-capability-profile/v0`
- `async-readiness-report/v0`

**Acceptance bar**
- A crate can say exactly what timer/deadline support it needs and what environments or runtimes it excludes.

### 4) Stream / async-sequence `watch` pilot
**Why fourth**
- This seam matters a lot, but the archive should prove it can publish a disciplined `watch` verdict instead of racing ahead.
- Language and borrowing/lending motion are still part of the story.

**Core artifacts**
- `async-lane-profile/v0`
- `async-seam/v0`
- `async-readiness-report/v0`
- optional adapter and blocker notes

**Acceptance bar**
- The report clearly separates real ecosystem demand, current adapters, and genuine language/compiler blockers.

### 5) Environment contrast pilot
**Why fifth**
- Tokio-style server runtimes and Embassy-style embedded executors should not remain hidden inside one portability claim.
- This proves the kit can preserve environment lanes instead of flattening them.

**Core artifacts**
- `async-lane-profile/v0`
- `async-capability-profile/v0`
- `async-readiness-report/v0`

**Acceptance bar**
- One comparison clearly shows which capabilities or assumptions stop holding when the environment changes.

### 6) Async Lifecycle consumer-import pilot
**Why sixth**
- This proves Async Commons is not a standalone philosophy document.
- Async Lifecycle should be able to import spawn/time/local/environment truth rather than restating it.

**Core artifacts**
- imported `async-lane-profile/v0`
- imported `async-capability-profile/v0`
- lifecycle-facing notes and consumer diff

**Acceptance bar**
- One lifecycle or reliability artifact becomes sharper because Async Commons exists beneath it.

## What should wait
- Do **not** begin with “the one true portable async facade”.
- Do **not** begin with an all-runtimes compatibility badge.
- Do **not** begin by assuming streams/async iteration already have a final common layer.
- Do **not** begin by treating `std` inclusion as the immediate goal of every pilot.
- Do **not** begin by erasing environment differences between server and embedded async.

Those are downstream possibilities. First prove that a few lane-aware async seams and capability profiles can be exported honestly.

## Immediate archive decision
Treat [`design/async-commons-kit.md`](./async-commons-kit.md), [`design/async-commons-lane-map.md`](./async-commons-lane-map.md), and [`proposals/epic-async-commons-kit.md`](../proposals/epic-async-commons-kit.md) as the schema/epic anchors, and treat this file as the **execution order**. The next credible move is one I/O lane pilot plus one spawn/local capability pilot, not another runtime marketing story.
