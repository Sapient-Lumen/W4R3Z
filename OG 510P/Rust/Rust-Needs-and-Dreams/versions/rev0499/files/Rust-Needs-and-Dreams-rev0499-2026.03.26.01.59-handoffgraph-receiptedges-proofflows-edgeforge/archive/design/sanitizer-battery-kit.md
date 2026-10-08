# Design: Sanitizer Battery Kit (`cargo sanitize`, `sanitize-pack/v0`)

## Goal
Create a Cargo-native dynamic-analysis and mitigation substrate that lets projects **declare**, **run**, **diff**, and **review** execution lanes with honest metadata about:
- which engine ran,
- what runtime/sysroot/instrumentation was actually active,
- what the lane could and could not observe,
- what it found,
- and what was waived or left inconclusive.

This should converge existing engines rather than replace them. LLVM sanitizers, exploit-mitigation lanes, `cargo-careful`, Miri, `nextest`-based execution, and future BorrowSanitizer-style engines should all be able to publish into one review surface without pretending they are interchangeable.

Read this together with [`design/sanitizer-battery-lane-map.md`](./sanitizer-battery-lane-map.md), which keeps interpreter lanes, runner-import variants, native checking, native finding, mitigation, and aliasing-watch lanes separate.

## References (signals)
- Rust’s 2026 flagship roadmap explicitly includes **Stabilize MemorySanitizer and ThreadSanitizer Support**, including the infrastructure changes needed to provide **precompiled and instrumented standard libraries**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 sanitizer-support goal is the immediate precursor: practical MSan/TSan workflows should not require users to rebuild std by hand forever.
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- The unstable-book sanitizer docs still show why lane provenance matters: target support, `-Zbuild-std`, cross-language flags, CFI/LTO requirements, and runtime-linking details vary materially by engine.
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- The rustc exploit-mitigations guide broadens the practical lane surface beyond classic ASan/MSan/TSan into safe stack and shadow call stack style hardening.
  https://doc.rust-lang.org/rustc/exploit-mitigations.html
- Miri documents deterministic execution, host isolation by default, and explicit limits around platform APIs and native code.
  https://github.com/rust-lang/miri
- `nextest` documents that Miri-in-nextest can be much faster while losing some race-detection visibility, which makes runner/import semantics part of the battery contract instead of a local implementation detail.
  https://nexte.st/docs/integrations/miri/
- The dedicated lane split reference is now [`design/sanitizer-battery-lane-map.md`](./sanitizer-battery-lane-map.md), which treats interpreter/native/mitigation/watch differences as first-class review truth.
- The dedicated rollout reference is now [`design/sanitizer-battery-pilot-program.md`](./sanitizer-battery-pilot-program.md), which treats lane comparison and execution-import honesty as first-class success criteria.
- `cargo-careful` provides a practical extra-checking lane with debug-assertion std and optional sanitizer integration.
  https://github.com/RalfJung/cargo-careful
- The retag/codegen goal and BorrowSanitizer updates show a distinct future lane for native aliasing instrumentation.
  https://rust-lang.github.io/rust-project-goals/2025h2/codegen_retags.html
  https://borrowsanitizer.com/status/february_2026.html

## Core design principles
1. **Execution lane is first-class.** “We ran Miri” is not enough. The artifact must preserve whether the lane was isolated, process-per-test, host-visible, cross-interpreted, instrumented-stdlib-backed, or mixed-language aware.
2. **Instrumentation provenance is first-class.** A finding means different things depending on whether std/runtime libraries were rebuilt, downloaded from rustup, or absent.
3. **Capabilities and outcomes are separate.** A lane may be configured correctly and still be unable to observe certain bug classes or code paths.
4. **Execution imports are first-class.** Direct runs, `cargo test`, `cargo miri`, nextest-backed runs, and imported runner-native recordings must remain explicit because execution mode can materially change observability.
5. **Findings are not the only result.** Unsupported targets, partial FFI visibility, skipped tests, runner failures, and stale suppressions are all meaningful review outcomes.
6. **Do not flatten Miri, careful, and native sanitizers into one fake score.** They are complementary lanes with different semantic and operational affordances.
7. **Do not flatten finding lanes and mitigation lanes into one fake score.** A hardening lane such as CFI or shadow-call-stack is adjacent to sanitizer work, but not the same review outcome as “a bug-finding sanitizer run”.

## Proposed artifact family

### 1) `sanitize-subject/v0`
Declares what is being analyzed.

Fields:
- workspace / package / binary / test subject
- crate graph identity / lockfile / revision
- host toolchain id
- target triple(s)
- profile(s) and runner family

### 2) `sanitize-lane-profile/v0`
Declares the intended execution lane.

Fields:
- engine family (`miri`, `careful`, `llvm-sanitizer`, `borrow-sanitizer`, `other`)
- lane posture (`interpreter`, `runner-import`, `native-checking`, `native-finding`, `mitigation`, `watch-import`)
- engine version / toolchain channel
- in-process vs process-per-test vs custom runner
- host isolation posture
- target and cross-execution posture
- requested finding classes
- required environment / external tools

### 3) `sanitize-runtime-profile/v0`
Records runtime and instrumentation provenance.

Fields:
- std/sysroot provenance (`host-std`, `rebuilt`, `prebuilt-instrumented`, `custom-pack`)
- sanitizer runtime libraries / runtime linkage posture
- relevant target modifiers and flags
- LTO / linker requirements if applicable
- mixed-language instrumentation posture (`complete`, `partial`, `none`, `unknown`)
- symbolizer / debug-info posture

Design rule: keep runtime provenance separate from lane identity. Two runs can both be “ASan” while differing materially in sysroot, runtime linkage, or FFI coverage.

### 4) `sanitize-capability-profile/v0`
Declares what the lane can observe and its blind spots.

Fields:
- supported finding classes
- deterministic vs schedule-sensitive posture
- inter-test race visibility
- native/FFI visibility
- platform API / networking / filesystem visibility
- unsupported targets / known false-positive or false-negative regions

### 5) `sanitize-execution-import/v0`
Records how execution evidence from the runner or harness entered the sanitize lane.

Fields:
- execution source (`direct`, `cargo-test`, `cargo-miri`, `nextest`, `runner-recording-import`, `other`)
- imported artifact pointers (`test-exec-pack/v0`, runner-native recording refs, raw log sets)
- selected subset / shard / filterset notes
- known lossiness in the import
- observability-impact notes (for example inter-test race visibility changes)
- whether the import is authoritative, advisory, or watch-only

### 6) `sanitize-observation-report/v0`
Records what actually happened in one execution.

Fields:
- environment summary
- selected runner/harness
- imported execution evidence refs
- tests or workloads attempted
- skipped / unsupported / failed-to-launch cases
- partial-visibility reasons
- raw logs / attachments / crash artifacts

### 7) `sanitize-finding-report/v0`
Normalized report for findings and no-finding outcomes.

Fields:
- outcome class (`findings`, `no-findings`, `mitigation-only`, `unsupported`, `misconfigured`, `partial`, `inconclusive`)
- finding class and engine-native code
- symbolized stack / location / attachment pointers
- target and runner context
- confidence / comparability notes

### 8) `sanitize-waiver/v0`
Reviewable suppressions and exceptions.

Fields:
- matching scope (finding class, target, package, test, engine, lane)
- rationale
- expiry / review date
- replacement or remediation condition
- issuer / approval metadata

### 9) `sanitize-diff-report/v0`
Compare runs across revisions or lane changes.

Fields:
- subject pair
- comparable / non-comparable reason codes
- new / resolved / reclassified findings
- runtime-provenance deltas
- lane-visibility deltas
- waiver drift

### 10) `sanitize-pack/v0`
Attachable bundle for CI, releases, incident work, or safety review.

Contains:
- one `sanitize-subject`
- one or more lane/runtime/capability profiles
- optional execution-import artifacts
- observation and finding reports
- optional waivers
- optional raw attachments (logs, symbolized traces, reproducer metadata)

## CLI shape
- `cargo sanitize doctor`
  - inspect host tools, target support, runtime availability, symbolizer presence, and sysroot requirements
- `cargo sanitize run`
  - execute one or more declared lanes
- `cargo sanitize pack`
  - emit `sanitize-pack/v0`
- `cargo sanitize diff`
  - compare two packs or two reports

Read together with:
- [`design/sanitizer-battery-lane-map.md`](./sanitizer-battery-lane-map.md)
- [`design/sanitizer-battery-pilot-program.md`](./sanitizer-battery-pilot-program.md)
- [`design/test-execution-evidence-stack.md`](./test-execution-evidence-stack.md)
- [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md)
- [`design/toolchain-productization-stack.md`](./toolchain-productization-stack.md)
- [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md)

## Example supported lanes
1. **Miri isolated lane**
   - deterministic, host-isolated, partial platform visibility
2. **Miri + nextest lane**
   - process-per-test, faster, weaker inter-test race visibility
3. **Careful lane**
   - debug-assertion std, extra UB checks, optional sanitizer add-ons, native/FFI allowed
4. **LLVM finding lane**
   - ASan/MSan/TSan/LSan-style native execution with explicit runtime/sysroot provenance
5. **Mitigation / hardening lane**
   - CFI / KCFI / safestack / shadow-call-stack style activation with explicit enforcement and compatibility posture
6. **Borrow lane**
   - future aliasing instrumentation with its own capability and maturity profile

## Why this is a worthy ecosystem contribution
Rust already has meaningful runtime-checking engines. What it lacks is the **portable handoff layer** between those engines and the people or systems that need to trust their outputs: CI, reviewers, release pipelines, incident response, testing infrastructure, and safety evidence. The latest roadmap signal only sharpens that case: Rust is actively trying to make instrumented-stdlib sanitizer lanes practical, while the ecosystem is simultaneously widening into runner imports and new aliasing instrumentation rather than collapsing onto one engine. That is exactly the kind of substrate that turns scattered progress into ecosystem leverage.

## Non-goals
- Replace Miri, `cargo-careful`, LLVM sanitizers, or future aliasing tools.
- Pretend all lanes are directly comparable.
- Collapse every issue into one severity number.
- Define the Rust aliasing model.
- Become a universal debugger or crash-reporting platform.

## Risks
- **Upstream churn:** mitigate with artifact-first design and explicit capability fields.
- **False confidence:** preserve `unsupported`, `partial`, and `inconclusive` outcomes.
- **Overlap with safety/caching/sysroots:** keep runtime evidence, policy, and provisioning artifacts distinct.
- **CI complexity:** start with a few clear adapters and diffable packs, not a universal orchestration empire.
## Safety-critical stack note
Treat this kit as the **dynamic-analysis lane** inside the shared **Safety-Critical Evidence Stack** in [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md).
Its job is to keep runtime-checking provenance, visibility limits, and findings honest, then hand those artifacts to Safety Evidence rather than pretending a sanitizer pass is the whole safety case.
Use [`design/safety-critical-pilot-program.md`](./safety-critical-pilot-program.md) to keep runtime-checking pilots narrow before widening toward certification-facing release candidates.
