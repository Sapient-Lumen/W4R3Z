# Epic proposal: Sanitizer Battery Kit (`cargo sanitize` + `sanitize-pack/v0`)

## One-liner
Ship a standard dynamic-analysis and mitigation execution/evidence layer for Rust: `cargo sanitize`, versioned lane/runtime/capability/finding artifacts, and adapters that make Miri, `cargo-careful`, LLVM sanitizer lanes, mitigation lanes, and future BorrowSanitizer-style engines composable in CI and release review without flattening them into one battery verdict.

## Why this is worthy
Rust increasingly has the **engines** needed for serious runtime checking and adjacent hardening:
- 2026 flagship sanitizer work aimed at practical MSan/TSan workflows with precompiled and instrumented std,
- the 2025H2 sanitizer-support precursor goal,
- the exploit-mitigations surface documented in rustc,
- Miri as a deterministic UB/interpreter lane,
- `cargo-careful` as a practical extra-checking lane,
- `nextest` and related runner infrastructure as scalable execution imports with explicit tradeoffs,
- and retag/codegen work intended to support native aliasing instrumentation such as BorrowSanitizer.

What Rust still lacks is the **shared battery contract**.

Important questions still have to be answered by reading CI YAML and shell flags:
- Which lane actually ran?
- Was std or the sanitizer runtime instrumented?
- Did the lane import direct execution, `cargo test`, Miri, nextest, or some runner-native recording?
- Did the lane see FFI and mixed-language code, or not?
- Are “no findings” and “unsupported target” being conflated?
- Did a faster runner configuration silently change what classes of bug were observable?
- Are suppressions reviewable and expiring, or hidden in env vars and scripts?

That is a real ecosystem gap, and solving it would compound across safety, CI, release engineering, support policy, and incident response. The lane split captured in [`design/sanitizer-battery-lane-map.md`](../design/sanitizer-battery-lane-map.md) should remain normative for the proposal layer so interpreter, runner-import, native finding, mitigation, and aliasing-watch posture never collapse into one fake score.

## Users
- maintainers of unsafe-heavy crates
- mixed Rust/C/C++ teams
- application teams wanting a reproducible runtime-checking battery in CI
- safety and security reviewers
- tool authors adding new engines or wrappers
- release pipelines that want attachable runtime-evidence packs

## MVP (6–10 weeks)
- Schemas:
  - `sanitize-subject/v0`
  - `sanitize-lane-profile/v0`
  - `sanitize-runtime-profile/v0`
  - `sanitize-capability-profile/v0`
  - `sanitize-execution-import/v0`
  - `sanitize-observation-report/v0`
  - `sanitize-finding-report/v0`
  - `sanitize-waiver/v0`
  - `sanitize-pack/v0`
- Commands:
  - `cargo sanitize doctor`
  - `cargo sanitize run`
  - `cargo sanitize pack`
- Adapters for:
  - Miri
  - `cargo-careful`
  - one LLVM sanitizer wrapper family
- one CI recipe using imported execution evidence and uploaded packs
- one minimal diff mode for finding drift and non-comparability reporting
- one explicit lane map in [`design/sanitizer-battery-lane-map.md`](../design/sanitizer-battery-lane-map.md)
- one ranked execution plan in [`design/sanitizer-battery-pilot-program.md`](../design/sanitizer-battery-pilot-program.md)

## Good v1 extensions
- `sanitize-diff-report/v0`
- policy gates by finding class / target / lane / maturity level
- replay/fuzz/safety-case attachment conventions
- explicit runtime/sysroot import from Sysroot Pack Kit
- explicit execution import from Test Execution Evidence / runner-native recordings
- richer mixed-language instrumentation descriptors
- mitigation-activation reports and deployment-facing handoffs
- first-class aliasing lane support once BorrowSanitizer output stabilizes further

## Non-goals
- replace the underlying engines
- define UB or aliasing semantics for Rust
- guarantee cross-target comparability
- mandate one runner or one CI service
- reduce all findings to one fake security score

## Risks and mitigations
- **Upstream churn**
  - keep the contract artifact-first and capability-heavy
- **Overclaiming confidence**
  - treat `unsupported`, `partial`, and `inconclusive` as normal first-class outcomes
- **Scope bloat**
  - start with execution + evidence, not a universal triage dashboard
- **Engine mismatch**
  - require explicit capability and provenance descriptors for every lane
- **Overlap confusion**
  - let Safety Evidence, Sysroot Pack, Replay, and FFI Boundary consume sanitizer artifacts rather than absorb them

## Why now
This seam has crossed from “nightly tinkering” to “strategic substrate”. The roadmap now points toward practical sanitizer provisioning, richer mitigations, runner-import complexity, and new native instrumentation lanes. That means the most leveraged contribution is no longer one more checker. It is the **reviewable battery layer** — plus the ranked pilot path that proves it — making all the existing and emerging checkers usable together without flattening their differences.