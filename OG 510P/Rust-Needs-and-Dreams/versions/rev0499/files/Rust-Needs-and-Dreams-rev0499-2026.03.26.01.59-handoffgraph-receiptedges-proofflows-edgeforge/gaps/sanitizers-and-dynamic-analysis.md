# Gap: Dynamic analysis in Rust still lacks a first-class execution and evidence layer

## Summary
Rust now has enough serious dynamic-analysis engines that the missing contribution is no longer “invent another checker”. The missing seam is a **Cargo-native execution and evidence layer** that can describe, run, compare, and review:
- LLVM sanitizers (`asan`, `msan`, `tsan`, `cfi`, `kcfi`, `safestack`, `shadow-call-stack`, and related lanes),
- Rust-specific runtime checking (`cargo-careful`),
- MIR interpretation (`Miri`),
- test-runner and CI execution lanes (including `nextest`),
- and emerging aliasing/provenance instrumentation such as BorrowSanitizer.

Today, teams still compose this with ad hoc `RUSTFLAGS`, nightly switches, `-Zbuild-std`, target caveats, host/runner quirks, and hand-written CI glue. The engines exist. The missing layer is the shared boundary that records **which lane ran, what was instrumented, whether the lane was bug-finding or mitigation-oriented, what that lane could actually observe, what it found or enforced, and how much confidence to assign to the result**.

## Why now
- Rust’s 2026 flagship roadmap explicitly includes **Stabilize MemorySanitizer and ThreadSanitizer Support**, including the infrastructure changes needed to provide **precompiled and instrumented standard libraries**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 sanitizer-support goal is the immediate precursor and makes the operational requirement explicit: practical sanitizer use should not depend on rebuilding std by hand forever.
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- The current unstable-book sanitizer docs still expose how fragmented the workflow is: support is engine- and target-specific, several lanes still require `--target` and `-Zbuild-std`, cross-language CFI needs extra clang-side normalization flags, and some mitigations are documented separately from ordinary sanitizer flows.
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- The rustc exploit-mitigations chapter now documents a broader mitigation surface — including safe stack and shadow call stack — which means the dynamic-analysis / hardening story is no longer just ASan-vs-Miri.
  https://doc.rust-lang.org/rustc/exploit-mitigations.html
- Miri remains uniquely valuable, but its README says it defaults to deterministic execution and host isolation, approximates Rust UB under the current compiler, and has limited support for platform APIs and native FFI. That makes it a distinct execution lane, not the whole story.
  https://github.com/rust-lang/miri
- `nextest`’s Miri integration demonstrates why execution semantics must be first-class metadata: per-test processes can make Miri runs 3–4× faster, but that configuration also loses visibility into races between tests sharing resources. That means runner-native execution imports are part of the missing boundary, not an implementation footnote.
  https://nexte.st/docs/integrations/miri/
- `cargo-careful` has matured into a practical middle lane that rebuilds std with debug assertions, enables extra UB checks, and can optionally combine with sanitizers while still permitting arbitrary system and C FFI calls.
  https://github.com/RalfJung/cargo-careful
- The retag/codegen goal exists specifically to support native aliasing instrumentation such as BorrowSanitizer, and BorrowSanitizer’s February 2026 update shows improving diagnostics, LLVM integration, and a push toward broader usability.
  https://rust-lang.github.io/rust-project-goals/2025h2/codegen_retags.html
  https://borrowsanitizer.com/status/february_2026.html

## Concrete missing pieces
1. **Lane profiles, not just engine names**
   - engine family (`miri`, `careful`, `llvm-sanitizer`, future `borrow`)
   - host toolchain, target triple, runner, profile, and test harness
   - whether runs are in-process, process-per-test, isolated, or host-visible
2. **Instrumentation provenance**
   - whether std was rebuilt, downloaded, or taken from a prebuilt instrumented sysroot
   - which runtime libraries and target modifiers were active
   - whether mixed-language / FFI instrumentation was complete, partial, or absent
3. **Capability descriptors**
   - which bug classes the lane can realistically observe
   - whether results are deterministic, schedule-sensitive, or target-limited
   - whether inter-test races, foreign code, or platform APIs were visible
4. **Portable findings and outcome states**
   - findings must be reason-coded and attachable
   - `no findings`, `unsupported`, `misconfigured`, `partial visibility`, and `inconclusive` must remain distinct outcomes
5. **Reviewable waivers and drift reports**
   - suppressions, target exceptions, flaky-lane quarantines, and expiry dates should be first-class artifacts
   - diffs across PRs, toolchain upgrades, and target changes should be comparable without reverse-engineering shell scripts

6. **Lane-family map**
   - interpreter lane vs runner-import variant vs native debug-assertion lane vs native finding lane vs mitigation/hardening lane vs aliasing/watch-import lane
   - finding-oriented lanes must stay distinct from mitigation-only lanes
   - mixed-language completeness and maturity/watch posture must remain explicit

## Desired properties
- Converge existing engines instead of replacing them.
- Make instrumented-runtime provenance and execution semantics explicit.
- Preserve target-, engine-, and runner-specific truth instead of collapsing it into one fake “sanitizer pass”.
- Produce attachable artifacts for CI, reviews, incident response, and higher-level safety cases.
- Leave room for future native aliasing tools and mitigation-heavy lanes without forcing them into an ASan-shaped box.

## Distinction from nearby archive entries
- **Safety Evidence Kit** remains the higher-level assurance layer; Sanitizer Battery supplies one family of runtime evidence.
- **Replay Kit** is about capturing and replaying failures; Sanitizer Battery is about describing and executing runtime-checking lanes.
- **FFI Boundary Kit** governs interface contracts; Sanitizer Battery records how much of those boundaries were actually instrumented and visible at runtime.
- **Sysroot Pack Kit** owns reusable std/sysroot builds; Sanitizer Battery records which instrumented runtime/sysroot lane was selected and what that implied for findings.
- **Compile-Time Capabilities Kit** covers authority during compilation; Sanitizer Battery covers authority and visibility during execution.

See also [`design/sanitizer-battery-lane-map.md`](../design/sanitizer-battery-lane-map.md) and [`design/sanitizer-battery-pilot-program.md`](../design/sanitizer-battery-pilot-program.md). The next credible move is a ranked pilot path rather than a giant battery command: Miri isolated baseline first, Miri + runner-import second, `cargo-careful` native lane third, LLVM sanitizer + instrumented-stdlib finding lane fourth, mitigation/hardening lane fifth, BorrowSanitizer import sixth, and safety-critical imports last.
