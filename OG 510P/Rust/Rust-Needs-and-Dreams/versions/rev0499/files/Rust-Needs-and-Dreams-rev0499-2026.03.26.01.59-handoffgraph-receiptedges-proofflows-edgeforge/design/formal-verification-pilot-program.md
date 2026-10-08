# Design: Formal Verification Pilot Program (`cargo verify pilot`, `verify-pilot-pack/v0`)

## Goal
Make **Formal Verification Kit** executable as a ranked, reviewable rollout instead of leaving `verify-pack/v0` as an abstract schema wish.

The missing contribution is not another verifier, proof badge, or premature certification wrapper.
It is a disciplined pilot path that proves Rust projects can publish **portable proof intent, backend capability, assumption, outcome, and counterexample artifacts** across different verification families without pretending those families already mean the same thing.

## References (signals)
- Rust’s 2026 flagship roadmap explicitly treats **Safety-Critical Rust** as a top-level theme, with evidence-oriented milestones rather than generic safety marketing.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The safety-critical adoption writeup says verification and evidence demands rise with criticality, which makes attachable proof/report artifacts strategically important rather than academic extras.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The Rust standard-library contracts goal ports safety contracts from `verify-rust-std` into the standard library and treats contract attributes as formal-spec inputs for static analysis and verification.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- `a-mir-formality` explicitly aims to help validate and prove Rust’s type safety while aligning formal models with executable semantics through MiniRust.
  https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- The Verify Rust Std project now explicitly welcomes multiple approved tools in CI — ESBMC (via GOTO-Transcoder), Flux, Kani, and VeriFast — which is strong evidence that Rust verification is plural and still widening.
  https://model-checking.github.io/verify-rust-std/tools.html
- The Rust Foundation’s ESBMC announcement says ESBMC joined the standard-library verification initiative, that the workflow is live in CI, and that the team aims to integrate ESBMC as an alternative backend for Kani.
  https://rustfoundation.org/media/expanding-the-rust-formal-verification-ecosystem-welcoming-esbmc/
- The Rust Formal Methods Interest Group explicitly says it wants better tool inter-compatibility, especially for specifications, which makes shared proof/report artifacts more timely.
  https://rust-formal-methods.github.io/
- Kani is Cargo-native (`cargo kani`) and already exposes concrete-counterexample playback, harness selection, unwind bounds, and verification-specific cfg posture.
  https://model-checking.github.io/kani/usage.html
- Creusot’s current workflow splits `cargo creusot` from `cargo creusot prove`, exposes intermediate Coma files, and already supports proof replay / IDE reopening workflows.
  https://creusot-rs.github.io/creusot/guide/
- Prusti already spans IDE-assisted verification plus `cargo prusti`, and its “verification succeeded” claim is narrower than full functional proof unless stronger specifications are added.
  https://viperproject.github.io/prusti-dev/user-guide/basic.html
- Verus frames itself as static full-functional-correctness verification for low-level systems code and explicitly does not rely on runtime checks.
  https://verus-lang.github.io/verus/guide/

## Why this needs its own design layer
The archive already had a strong Formal Verification Kit, but it still lacked a **reference execution path**.
Without a pilot design, the seam keeps drifting toward one of four failure modes:
1. **backend theater** — equating “we ran a verifier” with a stable shared contract;
2. **proof flattening** — treating model checking, deductive verification, refinement typing, separation-logic workflows, and proof-oriented Rust subsets as if a single `PASS` already means the same thing;
3. **artifact drift** — leaving counterexamples, bounds, assumptions, and trusted-code disclosures buried in backend-native logs;
4. **premature safety-case claims** — importing proof results into broader safety-critical stories before the proof lane itself has a disciplined rollout.

A worthy contribution should prove the smaller and stronger claim:
> Rust verification tools can emit enough shared structure that humans and downstream systems can compare proof scope, backend posture, assumptions, outcomes, and replayability honestly.

## Design principles
1. **Pair unlike families early.** A pilot should cross at least two verification families before claiming ecosystem value.
2. **Scope is part of the result.** Which crate, module, property class, bounds, contracts, and exclusions were in scope must stay explicit.
3. **Assumptions are first-class artifacts.** Trusted code, axioms, unsupported features, and proof budgets must be reviewable instead of buried.
4. **Replay is not optional when the backend can provide it.** Counterexamples, failed obligations, and proof-replay posture should survive beyond raw logs.
5. **Diffability matters as much as one-off success.** Adoption depends on being able to compare releases, toolchain upgrades, and backend swaps.
6. **Safety-critical imports come later.** Formal-verification pilots should harden themselves before becoming a wider assurance bundle ingredient.

## Artifact family

### 1) `verify-pilot-brief/v0`
Why a verification lane is being piloted.

Should record:
- pilot id and summary
- subject family (`bmc+dvt-pair`, `counterexample-replay`, `std-contract-slice`, `backend-diff`, `safety-critical-import`)
- why this slice matters now
- intended consumers
- why the slice is tractable now

### 2) `verify-subject-profile/v0`
The scoped thing being verified.

Should record:
- workspace/package/module/function identity
- target/profile/features/toolchain identifiers
- property classes in scope
- contract/spec source class
- included and excluded code
- whether the slice is illustrative, gating, or release-facing

### 3) `verify-import-matrix/v0`
How backend-native facts are imported.

Should record:
- selected backend family and version
- imported native outputs (`logs`, `proof.json`, `coma`, `witness`, `ide-session`, `proof-script`, etc.)
- known lossiness in the import
- whether the import is authoritative, advisory, or watch-only
- which artifacts are replayable versus merely inspectable

### 4) `assumption-budget/v0`
The explicit proof-limitation model.

Should record:
- loop/unwind/solver/resource bounds
- trusted code or axioms
- unsupported features
- contract/spec stubs
- FFI or environment assumptions
- expiry/review rules for tolerated incompleteness

### 5) `verify-consumer-handoff/v0`
How a pilot result may be consumed.

Should record:
- consumer class (`maintainer-review`, `release-review`, `safety-review`, `incident-triage`, `research-compare`)
- what the consumer may conclude
- what the consumer must not conclude
- required human checks
- required sibling evidence packs, if any

### 6) `verify-pilot-scorecard/v0`
Decides whether a lane is worth widening.

Should ask:
- did the pilot preserve scope truth?
- did it preserve backend-family differences honestly?
- did assumptions stay explicit?
- were counterexamples or failed obligations portable enough to review?
- did at least one real downstream consumer import it?
- does widening the pilot still look justified?

### 7) `verify-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- verify subject profile
- verify import matrix
- assumption budget
- linked `verify-pack/v0`
- optional backend-native attachments
- consumer handoff
- scorecard

## Ranked first pilots

### 1) Cargo-native pair: bounded model checking + deductive verification
**Why first**
- Kani and Creusot already expose distinct Cargo-native workflows.
- This is the smallest lane that proves one shared pack can span materially different proof families.
- It forces the archive to keep concrete counterexamples, contracts, and proof-search artifacts separate.

**Core artifacts**
- `verify-intent/v0`
- two `verify-capabilities/v0` imports
- one `verification-report/v0` per backend
- optional `counterexample-pack/v0` from Kani
- `verify-pilot-scorecard/v0`

**Primary consumers**
- maintainers comparing backend families on one crate
- CI/release review experimenting with proof imports
- research/teaching comparisons that need more than screenshots

### 2) Counterexample and replay lane
**Why second**
- Kani already has concrete playback; Creusot has replay/IDE flow; Prusti has IDE and Cargo lanes.
- This lane proves that failing proof obligations and concrete witnesses can become durable debugging artifacts instead of terminal output archaeology.

**Core artifacts**
- `counterexample-pack/v0` when available
- failure/obligation attachments when concrete witnesses are unavailable
- exact rerun instructions
- consumer handoff for incident/debug review

**Primary consumers**
- maintainers triaging failed proofs
- incident/debuggability consumers
- assistants or dashboards that need durable replay facts without pretending all backends emit the same witness shape

### 3) Standard-library-contract slice lane
**Why third**
- The std-contracts goal and verify-rust-std initiative make contracts/specification sources first-class ecosystem inputs.
- The multi-tool std-verification effort now has approved tools in CI, which makes this the clearest public proof-comparison substrate.
- This lane pressures the pack to keep contract authority, backend choice, and partial coverage separate.

**Core artifacts**
- `verify-subject-profile/v0` for a library slice
- contract/source-authority attachments
- backend comparison report
- explicit exclusions and unsupported-feature notes

**Primary consumers**
- unsafe-library reviewers
- standard-library verification contributors
- safety-contract and spec traceability work

### 4) Multi-backend diff and regression lane
**Why fourth**
- Tool upgrades, compiler upgrades, and spec changes are where verification adopters lose trust fastest.
- This lane proves `verify-diff-report/v0` is not optional polish; it is part of operationalizing proofs.

**Core artifacts**
- paired `verify-pack/v0` bundles
- `verify-diff-report/v0`
- reason-coded drift classification (`source-changed`, `backend-changed`, `bound-changed`, `scope-changed`, `spec-changed`)

**Primary consumers**
- release reviewers
- regression-tracking maintainers
- teams evaluating whether a backend swap widened or shrank proof coverage

### 5) Safety-critical import lane
**Why fifth**
- Only after the proof lane itself is stable should it be imported into the larger Safety-Critical Evidence Stack.
- This proves proof artifacts can become one explicit ingredient in a safety story without becoming the whole story.

**Core artifacts**
- linked `verify-pack/v0`
- linked safety-case and coverage/dynamic-analysis imports where relevant
- consumer handoff for safety/release review
- explicit limits on what the assurance consumer may conclude

**Primary consumers**
- higher-assurance product teams
- audit/pre-certification preparation teams
- maintainers building scoped safety cases around proof-backed modules

## Graduation rules
A pilot should graduate only when:
1. at least two materially different backends or families have been imported successfully;
2. assumptions and unsupported states remain visible;
3. counterexample or failure-replay posture is honest and documented;
4. a real downstream consumer uses the artifacts;
5. widening the pilot still looks justified.

If these are not met, the correct outcome is to keep the lane narrow or split it further.

## Why this is a worthy contribution
Rust already has enough serious verification motion that **workflow interoperability is becoming more valuable than one extra backend-local wrapper**.
A good formal-verification pilot program would turn `verify-pack/v0` from a good idea into an executable archive direction: one that supports maintainers, researchers, and safety-critical adopters without flattening real tool differences.
