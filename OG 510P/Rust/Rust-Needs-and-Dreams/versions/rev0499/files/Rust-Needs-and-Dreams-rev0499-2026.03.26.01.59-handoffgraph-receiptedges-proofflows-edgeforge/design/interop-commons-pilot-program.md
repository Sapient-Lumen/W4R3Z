# Design: Interop Commons Pilot Program (`cargo commons pilot`, `commons-pilot-pack/v0`)

## Goal
Make **Interop Commons** real with a ranked, reviewable pilot program that proves when Rust ecosystems need a **neutral shared seam** and when they are still better served by honest adapters, watch/wait reports, or no common layer at all.

The problem is not only inventing schemas like `interop-seam/v0` and `adapter-profile/v0`. The harder problem is choosing **which seams to pilot first**, how small the neutral core must stay, what adapter/conformance evidence is required before a seam can be treated as ecosystem infrastructure, and how to publish an explicit **not-ready-yet** verdict without treating that as failure.

A worthy contribution here is not another “unifying abstraction” crate. It is a disciplined rollout program that can prove shared building blocks where they help, reject them where they would hide semantic mismatch, and leave behind reusable evidence for Atlas, docs, CI, and future adopters.

## References (signals)
- Rust’s vision work explicitly recommends smoother interop and says helping users navigate crates.io may require key interop traits or standard building blocks rather than only recommendation prose.  
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says ecosystem complexity, resource pain, and maintainer support remain live concerns while online docs stay canonical and LLM/editor use rises. That increases the value of small, explicit seams that both humans and tools can consume.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s 1.90 development-cycle report explicitly says Cargo cannot be everything to everyone and that plugins matter. That argues for commons as a companion ecosystem layer, not a demand that Cargo or std absorb every shared seam immediately.  
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The `http` crate is existing proof that Rust can benefit from a neutral shared vocabulary without forcing one client/server framework.  
  https://docs.rs/http
- Tower-style `Service` / `Layer` seams and `tower-http` middleware show that explicit shared boundaries can enable reuse across otherwise independent stacks.  
  https://docs.rs/tower  
  https://docs.rs/tower-http
- Rust’s 2026 flagship themes still treat lending iterators / dormant traits and async parity as active future-facing work. That is a warning that some promising seams should first be piloted as **readiness cases**, not prematurely frozen into a common crate.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The reborrow-traits and Polonius goals both make clear that important borrow-friendly sequence seams still have real language/compiler blockers. That is exactly why the pilot system must support explicit watch/wait outcomes.  
  https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html  
  https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html

## Why this needs its own design layer
The main Interop Commons design already defines the canonical artifact family (`interop-seam`, `shared-building-block`, `adapter-profile`, `conformance-vector-set`, `seam-readiness-report`, and so on). What it does **not** fully settle by itself is:
- which seams should be piloted first,
- how small the neutral core must remain,
- how many adapters are enough for credibility,
- which conformance vectors are mandatory versus stretch goals,
- when a seam should be labeled `promote`, `pilot`, `watch`, or `defer`,
- and when a pilot has proved enough to become reusable ecosystem substrate.

Without that layer, Interop Commons risks two opposite failures:
1. **pseudo-standardization** — early pilots silently become blessed answers before seam scope, adapter lossiness, and stewardship are explicit;
2. **schema theater** — beautiful neutral-seam schemas exist, but nobody can tell which seams deserve common ground now and which are still waiting on language or ecosystem maturation.

## Design principles
1. **Start where repeated adapter churn already exists.** The opening pilots should target seams with visible cross-stack reuse pressure, not merely elegant abstractions.
2. **Keep the neutral core aggressively small.** Pilot success comes from proving a tiny common vocabulary, not from wrapping full frameworks.
3. **Adapters are first-class evidence.** A seam without honest adapter profiles is not yet a useful commons proposal.
4. **Conformance budgets must be explicit.** Pilots need positive vectors, negative vectors, and environment assumptions.
5. **“Not ready yet” is a valid outcome.** Commons must support watch/wait verdicts for seams that still depend on language/compiler progress.
6. **Stewardship must be visible before promotion.** A promoted seam is infrastructure and needs ownership, versioning, and migration posture.
7. **Atlas consumes successful seams.** Recommendation pilots should point at commons artifacts only after seam readiness has been made explicit.

## Artifact family
### 1. `commons-pilot-brief/v0`
Explains why a seam is worth piloting now:
- seam id and summary
- why adapter churn is high enough to matter
- why the seam is tractable enough to pilot now
- expected adopter families
- likely semantic fault lines

### 2. `pilot-neutral-core-scope/v0`
Defines the neutral layer being attempted:
- types / traits / metadata in scope
- explicit exclusions
- extension points
- semantics that must remain framework-specific
- reasons the core is small enough to stay neutral

### 3. `pilot-adapter-matrix/v0`
Declares the minimum adapter coverage for credibility:
- adopter crates / versions
- required adapter modes
- lossy edges that must be documented
- runtime / allocation / buffering / pin assumptions
- unsupported combinations

### 4. `pilot-conformance-budget/v0`
Defines what must be tested:
- required golden vectors
- required negative cases
- environment assumptions
- optional extended vectors
- known untestable or deferred areas

### 5. `pilot-readiness-scorecard/v0`
Decides whether a seam is working:
- does the neutral core stay small?
- do adapters preserve honest lossiness?
- do vectors catch real regressions?
- are adopters materially independent?
- are blockers ecosystem-local or language/compiler-level?
- should the seam be `promote`, `pilot`, `watch`, or `defer`?

### 6. `pilot-stewardship-profile/v0`
Makes governance visible:
- maintainer / steward identities
- versioning and MSRV posture
- new-adopter policy
- change-approval path
- deprecation / succession rules

### 7. `commons-pilot-pack/v0`
Bundle for review and reuse:
- canonical pilot artifacts
- current readiness verdict
- adapter findings
- conformance results
- migration notes
- Atlas-facing summary when applicable

## Ranked first pilots

### 1) HTTP request / response / body seams
**Why first**
- Rust already has a proven neutral vocabulary in `http` and adjacent body traits.
- Multiple serious adopters exist across client, server, and middleware ecosystems.
- This is the cleanest place to prove that a commons pilot can stay small while still being useful.

**What must be explicit**
- request/response/header/body scope boundaries
- what belongs in `http`-style common types versus framework-specific ergonomics
- body-stream and buffering assumptions
- known adapter lossiness
- environment/runtime assumptions for tested combinations

**Why this is a good pilot**
It is the strongest “promotion” candidate because the ecosystem already has real common ground; the pilot mainly needs to make scope, adapters, vectors, and stewardship more reviewable.

### 2) Service / layer / middleware seams
**Why second**
- Tower-style integration points already unlock reuse across Axum-, Hyper-, and Tonic-adjacent stacks.
- Middleware and service composition are exactly the sort of area where vague “these crates compose” folklore is not enough.
- This pilot can prove that a commons layer can describe adapter truth without flattening higher-level framework semantics.

**What must be explicit**
- service and layer semantics that truly compose
- backpressure / readiness / async assumptions
- middleware ordering and lossiness caveats
- which behavior stays outside the neutral seam

**Why this is a good pilot**
It tests whether Interop Commons can describe a widely reused seam with sharper semantic boundaries than a mere type vocabulary.

### 3) One explicit watch/wait seam: async borrowing / sequence interop
**Why third**
- The ecosystem clearly wants better async-sequence and borrow-friendly interoperability.
- Official goals still say important pieces depend on language/compiler progress (reborrow traits, Polonius, lending iterators, async parity).
- A commons system that cannot publish an honest `watch` verdict will eventually overstandardize too early.

**What must be explicit**
- which parts are sync today versus async bridge versus future language-enabled lanes
- what adapter costs are clones / boxing / buffering / pinning / runtime coupling
- which blockers are ecosystem fragmentation versus genuine language/compiler blockers
- why promotion would be premature today, if that remains the verdict

**Why this is a good pilot**
It proves the archive can say “this seam matters, but the correct contribution right now is evidence and readiness reporting rather than a final common crate.”

## Pilots to defer
These may matter later, but are weaker opening bets:
- **general database abstractions** — semantics differ too widely for a clean neutral opening pilot
- **GUI/widget commons** — likely to collapse into framework politics too early
- **full plugin-runtime seams** — important, but better after HTTP/Tower-style pilots prove the mechanics
- **cross-domain ‘error story’ commons** — tempting, but too easy to over-unify without real gain

## Suggested CLI shape
- `cargo commons pilot init`
- `cargo commons pilot check`
- `cargo commons pilot diff`
- `cargo commons pilot score`
- `cargo commons pilot promote`
- `cargo commons pilot watch`
- `cargo commons pilot retire`

## Phased execution
### Phase 0: pilot scaffolding
- lock down pilot artifacts
- write one worked example and one explicit watch/wait case
- define readiness scorecards before expanding scope

### Phase 1: proven-seam pilots
- ship HTTP request/response/body and service/layer pilots
- require adapter matrices and conformance budgets up front
- keep neutral cores aggressively minimal

### Phase 2: watch/wait seam
- ship one async borrowing / sequence readiness pilot
- make language/compiler blockers first-class rather than hiding them in “future work” prose

### Phase 3: Atlas consumption
- let atlas pilots reference commons outputs where seams are actually ready
- keep Atlas and Commons governance distinct so recommendation pressure does not silently standardize a seam

### Phase 4: expansion or refusal
- expand only if the existing pilots show real reuse, honest adapters, and sustainable stewardship
- explicitly refuse or defer seams that keep collapsing into semantic mismatch or framework-specific behavior
