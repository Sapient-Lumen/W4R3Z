# Design: Sanitizer Battery Pilot Program (`cargo sanitize pilot`, `sanitize-pilot-pack/v0`)

## Goal
Make **Sanitizer Battery Kit** executable as a ranked, reviewable rollout instead of leaving `sanitize-pack/v0` as a strong schema idea with no agreed proving path.

The missing contribution is not another checker, wrapper, dashboard, or one-flag “run all sanitizers” story.
It is a disciplined pilot path that proves Rust projects can publish **portable dynamic-analysis intent, runtime/instrumentation provenance, execution-import truth, capability limits, findings or mitigation posture, and waiver-aware diffs** across materially different lanes without pretending those lanes already mean the same thing.

## Why this now
- Rust’s 2026 flagship roadmap explicitly includes **Stabilize MemorySanitizer and ThreadSanitizer Support**, including the infrastructure changes needed to provide **precompiled and instrumented standard libraries**. That moves sanitizer work from niche nightly lore into roadmap-visible ecosystem infrastructure.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 sanitizer-support goal already made the practical substrate clear: MemorySanitizer and ThreadSanitizer need a way to be used **without rebuilding the standard library by hand forever**, which implies provisioning and review boundaries above raw shell flags.
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- The current unstable-book sanitizer docs still show why lane identity cannot be reduced to a single engine name: target support, `-Z build-std`, runtime-linkage posture, and cross-language flags materially change what a run means.
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- The rustc exploit-mitigations chapter makes a second distinction explicit: CFI, KCFI, safestack, and shadow-call-stack live near sanitizer work, but they are hardening lanes, not identical “finding lanes”.
  https://doc.rust-lang.org/rustc/exploit-mitigations.html
- `cargo-careful` is now a real middle lane rather than a toy: rebuilt std with debug assertions, extra UB checks, optional sanitizer add-ons, and support for arbitrary system and C FFI make it operationally different from both Miri and classic LLVM sanitizer runs.
  https://github.com/RalfJung/cargo-careful
- Miri remains uniquely valuable but semantically distinct. Its default isolation and interpreter semantics differ sharply from native execution, and nextest’s Miri integration makes the runner story explicit by trading shared-process race visibility for per-test process speed and isolation benefits.
  https://github.com/rust-lang/miri
  https://nexte.st/docs/integrations/miri/
- The retag/codegen work and BorrowSanitizer updates show the horizon is widening again: Rust is not converging on one dynamic-analysis lane, it is gaining new native instrumentation families.
  https://rust-lang.github.io/rust-project-goals/2025h2/codegen_retags.html
  https://borrowsanitizer.com/status/february_2026.html
- Rust-for-Linux is still a forcing function for stable foundations around compiler flags, sanitizer integration, and custom std builds, which keeps this problem ecosystem-level rather than “CI polish for app teams”.
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html

The proposal-layer candidate that should absorb successful pilots remains [`proposals/epic-sanitizer-battery-kit.md`](../proposals/epic-sanitizer-battery-kit.md). Keep the lane split in [`design/sanitizer-battery-lane-map.md`](./sanitizer-battery-lane-map.md) open next to this pilot design while evaluating widening moves.

## Why this needs its own design layer
The archive already had a strong Sanitizer Battery Kit, but without a pilot design the seam keeps drifting toward four failure modes:
1. **engine flattening** — equating Miri, `cargo-careful`, native sanitizers, mitigation-heavy lanes, and future aliasing tools because they all found “runtime bugs”;
2. **build-flag overclaim** — inferring runtime visibility from `RUSTFLAGS`, target triples, or passing CI jobs instead of explicit runtime/instrumentation receipts;
3. **runner amnesia** — forgetting that execution mode can change observability, as shown by Miri-in-nextest versus `cargo miri test`;
4. **assurance inflation** — importing dynamic-analysis results into safety/release/support claims before the dynamic-analysis lane itself has a disciplined artifact path;
5. **finding/mitigation blur** — narrating CFI/safestack/shadow-call-stack as though they were just another “found bugs / found none” sanitizer lane.

A worthy contribution should prove the smaller and stronger claim:
> Rust dynamic-analysis lanes can emit enough shared structure that humans and downstream systems can compare what ran, what it could see, what it actually found, and where the results are not comparable.

## Design principles
1. **Pair unlike lanes early.** The pilot should cross at least two materially different engine families before claiming ecosystem value.
2. **Execution imports are first-class artifacts.** Runner-native stores and portable run packs should be imported explicitly rather than reverse-engineered from logs.
3. **Provisioning and enactment stay distinct.** “Instrumented std was available” and “this run actually used it” must remain separate facts.
4. **Visibility limits are part of the result.** Unsupported target, partial FFI visibility, host isolation, and lost inter-test race visibility are meaningful outcomes.
5. **Diffability matters as much as one-off success.** Adoption depends on comparing revisions, toolchain changes, runner swaps, and lane substitutions honestly.
6. **Safety-critical imports come later.** Dynamic-analysis pilots should harden themselves before being widened into broader assurance packages.

## Artifact family

### 1) `sanitize-pilot-brief/v0`
Why a dynamic-analysis slice is being piloted.

Should record:
- pilot id and summary
- subject family (`miri-isolated`, `miri-runner-import`, `careful-native`, `llvm-sanitizer`, `borrow-lane`, `toolchain-import`, `safety-import`)
- why this slice matters now
- intended consumers
- why the slice is tractable now

### 2) `sanitize-subject-profile/v0`
The scoped thing being analyzed.

Should record:
- workspace/package/binary/test identity
- target/profile/features/toolchain identifiers
- unsafe-heavy or FFI-heavy posture when relevant
- included and excluded workloads
- whether the slice is illustrative, gating, release-facing, or watch-only

### 3) `sanitize-execution-import/v0`
How execution evidence is imported.

Should record:
- execution source (`direct`, `cargo-test`, `cargo-miri`, `nextest`, `runner-recording-import`, `other`)
- imported artifact pointers (`test-exec-pack/v0`, runner-native recording, raw log set)
- selected subset / filterset / shard notes
- known lossiness in the import
- observability-impact notes (for example inter-test race visibility, process model, host access)
- whether the import is authoritative, advisory, or watch-only

### 4) `sanitize-runtime-budget/v0`
The explicit runtime/instrumentation limitation model.

Should record:
- std/sysroot provenance
- runtime library linkage posture
- target modifiers and ABI-affecting flags
- mixed-language instrumentation completeness
- unsupported platform APIs, FFI zones, or external runtimes
- known false-positive / false-negative regions

### 5) `sanitize-consumer-handoff/v0`
How a pilot result may be consumed.

Should record:
- consumer class (`maintainer-review`, `ci-gate`, `release-review`, `safety-review`, `incident-triage`, `research-compare`)
- what the consumer may conclude
- what the consumer must not conclude
- required sibling artifacts (`test-exec-pack`, `sysroot-pack`, `replay-pack`, `safety-pack`, etc.)
- required human checks

### 6) `sanitize-pilot-scorecard/v0`
Decides whether a lane is worth widening.

Should ask:
- did the pilot preserve lane identity honestly?
- did it preserve runner/execution-import truth honestly?
- did runtime provenance stay explicit?
- were unsupported/partial/inconclusive outcomes preserved?
- did at least one real downstream consumer import it?
- does widening the pilot still look justified?

### 7) `sanitize-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- subject profile
- execution import
- runtime budget
- linked `sanitize-pack/v0`
- optional engine-native attachments
- consumer handoff
- scorecard

## Ranked first pilots

### 1) Miri isolated baseline lane
**Why first**
- Miri is semantically strong and narrow enough to force capability honesty early.
- It gives the archive a clean baseline for host isolation, deterministic execution, and UB-finding posture before runner imports complicate the story.

**Core artifacts**
- `sanitize-lane-profile/v0`
- `sanitize-runtime-profile/v0`
- `sanitize-capability-profile/v0`
- `sanitize-observation-report/v0`
- `sanitize-finding-report/v0`
- `sanitize-pilot-scorecard/v0`

**Primary consumers**
- unsafe-library maintainers
- CI experiments
- incident reviewers wanting a disciplined interpreter lane

### 2) Miri + runner-import lane
**Why second**
- nextest shows exactly why execution import must be first-class: per-test processes can be much faster and easier to inspect, but they also lose some shared-process race visibility.
- This is the smallest pilot that proves the archive can record an execution-mode change without pretending the underlying engine changed.

**Core artifacts**
- `sanitize-execution-import/v0`
- imported `test-exec-pack/v0` or runner-native recording refs
- explicit observability delta against the baseline Miri lane
- `sanitize-diff-report/v0`

**Primary consumers**
- teams integrating dynamic-analysis into existing runner infrastructure
- testing-stack consumers
- maintainers comparing fidelity versus throughput

### 3) `cargo-careful` native/FFI lane
**Why third**
- `cargo-careful` is the clearest practical middle lane between interpreter-only and classic sanitizer runs.
- It forces the archive to record rebuilt-std provenance, extra-UB-check posture, native execution, and arbitrary FFI visibility honestly.

**Core artifacts**
- `sanitize-runtime-profile/v0`
- `sanitize-capability-profile/v0`
- optional sanitizer add-on notes
- runtime-budget and handoff artifacts

**Primary consumers**
- mixed Rust/C teams
- app and library maintainers wanting a cheaper always-on runtime battery
- release reviewers importing native-execution dynamic evidence

### 4) LLVM sanitizer + instrumented-stdlib finding lane
**Why fourth**
- This is where the 2026 flagship and 2025H2 support goal apply directly.
- It pressures the battery to preserve target support, runtime linkage, `build-std` or prebuilt instrumented std posture, and mixed-language instrumentation assumptions.

**Core artifacts**
- `sanitize-runtime-profile/v0`
- `sanitize-runtime-budget/v0`
- `sanitize-waiver/v0`
- explicit toolchain/sysroot imports when available
- comparability notes across ASan / MSan / TSan finding lanes

**Primary consumers**
- platform and toolchain maintainers
- release/security review
- Rust-for-Linux and other toolchain-heavy adopters

### 5) Mitigation / hardening lane
**Why fifth**
- The rustc exploit-mitigations surface proves adjacent hardening lanes already exist.
- This pilot forces the battery to preserve “mitigation active / inactive / partial” truth without laundering it into a fake findings report.

**Core artifacts**
- explicit mitigation-family identity
- activation/enforcement posture
- compatibility notes and unsupported-target notes
- comparability limits against bug-finding lanes

**Primary consumers**
- platform/security/release reviewers
- toolchain/productization work
- downstream teams deciding whether a lane is debugging-only or deployable

### 6) Borrow / native aliasing instrumentation lane
**Why sixth**
- Retag/codegen work and BorrowSanitizer maturity should widen the battery, not restart it.
- This pilot proves the pack can absorb a new family with different maturity, semantics, and mixed-language value.

**Core artifacts**
- explicit maturity profile
- engine-native attachment import
- aliasing-specific capability notes
- comparability limits against Miri/careful/native sanitizer and mitigation lanes

**Primary consumers**
- unsafe and FFI-heavy maintainers
- research-to-production transitions
- safety/security reviewers watching new aliasing evidence families

### 7) Safety-critical import lane
**Why last**
- Dynamic-analysis should first prove it can stand alone.
- Only then should the archive widen to a lane where `sanitize-pack/v0` is imported by a broader `safety-pack/v0` story.

**Core artifacts**
- `sanitize-consumer-handoff/v0`
- linked `safety-pack/v0` or safety-review attachments
- explicit “may conclude” / “must not conclude” boundaries

## Pack shape to exercise during pilots
Every pilot should aim to emit or simulate:
- one `sanitize-pilot-brief/v0`;
- one `sanitize-subject-profile/v0`;
- one `sanitize-execution-import/v0`;
- one linked `sanitize-pack/v0`;
- optional imported `test-exec-pack/v0`, `sysroot-pack/v0`, or runner-native recordings;
- one `sanitize-consumer-handoff/v0`;
- one `sanitize-pilot-scorecard/v0`.

## Success criteria
The pilot succeeds when:
- unlike lanes can be compared without flattening them;
- finding-oriented and mitigation-oriented lanes remain visibly different;
- execution-mode and runner-import changes remain visible;
- instrumented-stdlib and mixed-language posture stay reviewable;
- unsupported/partial/inconclusive results remain first-class;
- at least one downstream consumer imports the result without overclaiming;
- and the archive can honestly say “wait” when a lane is not yet ready.

## Expected downstream consumers
- maintainers of unsafe-heavy crates
- mixed Rust/C/C++ teams
- CI and release-review workflows
- toolchain/productization work importing sysroot/runtime provenance
- safety-critical evidence consumers
- incident and replay workflows

## Rollout guidance
Start with semantically sharp lanes and runner deltas, not with a universal “battery” command that tries to run everything at once.
Do **not** start with a hosted results portal, a universal severity score, or a requirement that every engine emit the same native log shape.

## Strategic outcome
If this pilot works, the ecosystem gets a practical answer to a hard now-problem:

**How do we make Rust dynamic-analysis lanes portable and reviewable across interpreters, native runtime checks, instrumented stdlib workflows, runner imports, and future aliasing instrumentation without lying about what each lane could see?**
