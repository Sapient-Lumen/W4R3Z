# Cross-sector opportunity map — 2026-03-22

This note exists to keep broad archive scans **wide** without letting them become vague.

A quick internal scan of the current proposal set shows that the archive is already very rich in **interoperability**, **tooling**, **security**, **testing**, **Cargo/devtools**, and domain-specific **conformance** work.
That is useful.
It also means future passes should ask harder questions before adding another niche lane.

## Main judgment

Across sectors, the ecosystem still seems to lack two kinds of crate contributions more than it lacks raw ideas:

1. **shared support-contract infrastructure**  
   compact bundles that make support, review, migration, and trust more portable;

2. **joined handoff layers**  
   crates that combine several already-real substrate pieces into one honest artifact another team can use.

That is why the archive’s highest-salience work remains concentrated in P-0484, P-0011, P-0535, P-0536, P-0120, P-0532, P-0486, P-0469, and P-0490.

## Sector map

### 1. Universal developer workflow pain — highest leverage

Signals:
- docs remain canonical;
- compile-time/resource friction is still a productivity tax;
- debugging still needs stronger support;
- maintainers/support infrastructure remain under strain.

Best crate shapes:
- support contracts,
- drift/diff artifacts,
- policy/authority receipts,
- machine-consumable knowledge packs.

Examples in the archive:
- P-0536 crate knowledge pack
- P-0469 rebuild explanation
- P-0490 lock contention witness
- P-0486 debuggability support
- P-0011 crate health

### 2. Regulated / long-lived systems — very high leverage

Signals:
- safety-critical users need target readiness, dependency lifecycle planning, async runtime requirements, and interop evidence;
- project goals explicitly elevate MC/DC, unsafe documentation, and supply-chain work.

Best crate shapes:
- evidence bundles,
- readiness/support contracts,
- lifecycle transition kits,
- assurance / verification workbenches.

Examples in the archive:
- P-0484 toolchain & target support
- P-0535 dependency lifecycle transition
- P-0532 async runtime assurance
- P-0433 MC/DC coverage workbench
- P-0120 unsafe contract auditor

### 3. Interop-heavy industries — still fertile, but no longer underexplored

The archive already has strong territory in automotive, finance, media, genomics, geospatial, digital twins, identity, supply-chain standards, and protocol conformance.
New additions here should be justified only when they add a **new evidence/interop seam**, not just another parser or SDK.

Rule:
- prefer a domain workbench only if the real missing value is **loss accounting, conformance evidence, portability truth, or replayability**.

### 4. Embedded / edge / device-heavy work — strong demand, but often shared-lane demand

Embedded teams show up in the current challenge story as an ecosystem-maturity audience, but many of the missing answers are actually shared support lanes:
- target support truth,
- dependency lifecycle posture,
- async runtime assurance,
- FFI/interop evidence,
- build friction reduction.

Rule:
- do not open a fresh embedded lane if the sharper missing crate is really a stronger shared support contract.

### 5. Science / data / numerics / GPU — medium-high, but avoid engine fantasies

This sector still has room, especially where layout/device/format/conformance truth matters.
But the archive should resist fantasies about one grand “Rust NumPy / ML / GPU supercrate” unless it has a very sharp support artifact.

Good shapes:
- semantic profile packs,
- format/crosswalk workbenches,
- loss-aware interop kits,
- device/layout contracts.

### 6. AI / agents / assistant-facing work — promising only when artifact-first

This sector is especially prone to repo bloat.
The useful additions here are usually **protocol conformance**, **trace/replay evidence**, or **crate knowledge handoff** — not another model wrapper, portal, or chat UX.

Rule:
- if the proposal mainly depends on prompting or hosted-model behavior, it usually does not belong in the top frontier;
- if it yields a stable, reviewable artifact another tool can consume, it may.

### 7. Desktop / mobile / app shipping — medium, but boundary-focused

The archive already has meaningful packaging, shipkit, accessibility, crash, and CLI surface ideas.
New work should usually target:
- portability/support boundaries,
- packaging integrity,
- diagnostics bundles,
- capability contracts.

## Elimination rules for future broad scans

Before adding a new proposal, explicitly ask:

1. is the missing value really a new crate lane,
2. or is it a product plan / schema / fixture gap inside an existing high-value lane?
3. does the proposal create a receiver-facing artifact another team can review?
4. does it escape existing ownership by P-0536, P-0011, P-0535, P-0484, P-0469, P-0490, P-0486, or P-0120?
5. is it solving a real seam, not just offering a nicer wrapper?

If the answer is mostly “no,” synthesize or eliminate it.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rustfoundation.org/strategic-plan/
