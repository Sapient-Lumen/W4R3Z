# Design: Sanitizer Battery lane map (Miri interpreter, runner-import variants, careful/native checking, LLVM finding lanes, mitigation lanes, and aliasing-watch imports)

## Goal
Sharpen **Sanitizer Battery Kit** so the archive stops treating “runtime checking” as one bucket.
Rust already has materially different sanitizer and dynamic-analysis lanes, and they differ in **execution semantics**, **instrumented-runtime provenance**, **mixed-language visibility**, **whether they are trying to find bugs or harden production code**, and **what downstream reviewers may conclude**.

The archive should therefore keep sanitizer review grounded in a lane map instead of one flattened “battery passed” story.

## Signals from the current ecosystem
- Rust’s 2026 flagship roadmap explicitly includes **Stabilize MemorySanitizer and ThreadSanitizer Support**, including the infrastructure changes needed to provide **precompiled and instrumented standard libraries**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 sanitizer-support goal sharpens the same point: practical MSan/TSan use should not require rebuilding std by hand forever.
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- The unstable-book sanitizer docs keep lane differences explicit: some sanitizers tolerate partial instrumentation, MemorySanitizer effectively requires full instrumentation, instrumented std is strongly recommended, and mixed Rust/C++ use can require `-Zexternal-clangrt` plus careful `--target` handling.
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- The rustc exploit-mitigations chapter documents `cfi`, `kcfi`, `safestack`, and `shadow-call-stack` as compiler-supported mitigation families. That is adjacent to sanitizer work, but not the same review lane as “bug-finding sanitizer run”.
  https://doc.rust-lang.org/rustc/exploit-mitigations.html
- Miri’s README says Miri is deterministic and host-isolated by default, with fake RNG/env/clock APIs and limited support for the full platform surface. That makes it a distinct execution lane, not the whole story.
  https://github.com/rust-lang/miri
- nextest’s Miri integration shows why runner/import posture must be first-class metadata: per-test processes can make Miri 3–4× faster, but they also stop detecting races between tests sharing resources.
  https://nexte.st/docs/integrations/miri/
- `cargo-careful` remains a real middle lane: rebuilt std with debug assertions, extra UB checks, optional sanitizer add-ons, arbitrary system and C FFI support, and a recent-nightly requirement.
  https://github.com/RalfJung/cargo-careful
- The retag/codegen goal and BorrowSanitizer’s February 2026 status update show a widening future lane for aliasing instrumentation in multilanguage/native settings rather than convergence onto today’s engines.
  https://rust-lang.github.io/rust-project-goals/2025h2/codegen_retags.html
  https://borrowsanitizer.com/status/february_2026.html

## The lanes

### 1) Miri isolated interpreter lane
This is the semantically sharp interpreter lane.

What defines it:
- MIR interpretation rather than native execution
- deterministic execution by default
- host isolation by default
- limited or fake implementations for some platform APIs
- no assumption that native FFI or system behavior is faithfully modeled

What this lane is good for:
- high-signal UB finding in pure-Rust or mostly-Rust code
- first pilot lane for capability honesty
- a clean baseline for comparing later runner-import and native lanes

What it must **not** silently become:
- a statement about native mixed-language execution
- a statement about real host/network/clock/entropy behavior
- a statement that a production binary is hardened or “safe”

### 2) Miri + runner-import lane
This is the interpreter lane after execution semantics have changed because a runner such as nextest is driving the workload.

What defines it:
- Miri remains the engine family
- execution is imported from a runner-shaped or process-per-test lane
- observability changes because test scheduling/process model changes
- speed and debuggability may improve

Why it deserves a separate lane:
- nextest itself documents that this path loses visibility into races between tests sharing resources
- “same engine” does **not** mean “same result meaning” when execution semantics changed
- imported runner evidence becomes part of the truth, not a footnote

Design rule:
- preserve runner/import posture separately from engine family, and preserve observability deltas explicitly

### 3) `cargo-careful` native checking lane
This is the middle lane between interpretation and sanitizer-heavy native instrumentation.

What defines it:
- native execution
- std rebuilt with debug assertions
- extra rustc UB-oriented checks
- arbitrary system and C FFI support
- optional sanitizer add-ons, but not defined by them

Why it deserves a separate lane:
- it is neither Miri nor a classic LLVM sanitizer run
- it carries distinct std provenance and visibility properties
- it is a practical “always-on-ish” native checking lane for some teams

Design rule:
- keep rebuilt-stdlib provenance and extra-check posture explicit instead of laundering this lane into generic “native sanitizer” claims

### 4) Native LLVM finding lane
This is the finding-oriented sanitizer family: ASan, LSan, MSan, TSan, and similar lanes where findings are the primary review outcome.

What defines it:
- native execution with instrumentation
- sanitizer runtime linkage
- target-specific support and caveats
- strong dependence on instrumented std/runtime posture for some engines
- mixed-language completeness may be `complete`, `partial`, `none`, or `unknown`

Why it deserves a separate lane:
- ASan/LSan and MSan/TSan do not have the same instrumentation requirements
- native Rust-only and Rust+C/C++ instrumented stories are materially different
- findings depend on runtime/sysroot/procedural-macro/build-script posture in ways reviewers need to see

Design rule:
- preserve finding-oriented native sanitizer lanes as their own family rather than folding them into interpreter, careful, or mitigation-only stories

### 5) Mitigation / hardening lane
This lane is adjacent to sanitizers, but it is not a bug-finding lane.

What defines it:
- hardening or exploit-mitigation features such as CFI, KCFI, safestack, or shadow-call-stack
- output may be “mitigation active / inactive / partially active” rather than “finding found / not found”
- deployment and compatibility questions matter alongside testing questions

Why it deserves a separate lane:
- mitigation lanes can change exploitability without directly reporting the same class of findings as ASan/MSan/TSan or Miri
- conflating “hardening enabled” with “sanitizer passed” destroys review clarity
- production-consumer meaning differs from debugging-consumer meaning

Design rule:
- preserve finding-oriented lanes and mitigation-oriented lanes separately, even when they share compiler flags or provisioning stories

### 6) Borrow / aliasing watch-and-import lane
This is the widening horizon lane for BorrowSanitizer-style or similar future aliasing instrumentation.

What defines it:
- native instrumentation shaped around Rust aliasing/ownership semantics
- multilanguage relevance
- evolving compiler/codegen support and maturity
- imported/watch posture until the lane is operationally mature

Why it deserves a separate lane:
- the compiler work needed for BorrowSanitizer is real and distinct
- aliasing instrumentation should not be forced into an ASan/MSan-shaped explanation
- maturity, semantics, and output conventions are still moving

Design rule:
- keep this lane explicit as watch/import/maturing until it can support stronger ecosystem claims

## Review rules that follow from the lane map
1. Keep **engine family** separate from **execution model**.
2. Keep **interpreter lanes** separate from **native execution lanes**.
3. Keep **runner-import posture** separate from **engine identity**.
4. Keep **instrumented-stdlib/runtime provenance** separate from **lane selection**.
5. Keep **finding-oriented lanes** separate from **mitigation/hardening lanes**.
6. Keep **mixed-language completeness** separate from **Rust-only success claims**.
7. Keep **watch/import aliasing lanes** separate from **production-ready lanes**.
8. Keep **dynamic-analysis packs** separate from **safety-case conclusions**.

## What a worthy contribution should look like
The worthy contribution here is **not**:
- another “run all the sanitizers” wrapper,
- another CI badge or one-number battery score,
- another engine-specific helper,
- or another dashboard that hides execution/import/runtime details.

It is a thin `cargo sanitize` / `sanitize-pack/v0` layer that can preserve:
- lane identity,
- execution-import truth,
- runtime/sysroot provenance,
- capability and blind-spot profiles,
- finding reports,
- mitigation activation posture,
- waiver drift,
- and bounded downstream handoffs.

That means downstream reviewers can answer:
- *which lane actually ran?*
- *was this interpreter, native checking, finding-oriented native instrumentation, or mitigation hardening?*
- *what changed when a runner/import path was used?*
- *was std/runtime instrumentation complete, partial, or unknown?*
- *what did the lane actually have the power to observe?*
- *what may a safety/release/support consumer conclude, and what must remain advisory or watch-only?*

## Immediate archive consequences
Read this together with:
- `design/sanitizer-battery-kit.md`
- `design/sanitizer-battery-pilot-program.md`
- `gaps/sanitizers-and-dynamic-analysis.md`
- `proposals/epic-sanitizer-battery-kit.md`
- `design/test-execution-evidence-stack.md`
- `design/sysroot-pack-kit.md`
- `design/toolchain-productization-stack.md`
- `design/safety-critical-evidence-stack.md`

The archive should now prefer **lane-aware sanitizer packs before one fake battery verdict**.
