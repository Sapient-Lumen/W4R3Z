
# Sanitizer and unsafe-evidence stack — 2026-03-16

This note exists to stop the archive from collapsing several adjacent safety/debugging ideas into one vague “sanitizer crate”.

Recent Rust signals make the boundary sharper:

- Rust’s 2026 goals include stabilizing **MemorySanitizer** and **ThreadSanitizer** support.
- BorrowSanitizer-related compiler work is explicitly aimed at practical runtime detection of aliasing violations, especially across language boundaries.
- The 2025 State of Rust survey still reports debugging as a meaningful productivity problem, and the 2026 debugging survey is explicitly asking about debugger quality, visualizers, async debugging, and expression evaluation.

That means the ecosystem now has multiple real lanes, and the archive must keep them separate.

## The stack to preserve

### 1. General sanitizer workflow substrate
This is **P-0434 Sanitizer Profile & Evidence Kit** territory:

- ASan / LSan / MSan / TSan profile selection
- instrumented std expectations
- symbolization and suppressions
- target/toolchain/profile caveats
- CI handoff bundles

The receiver-facing question is:

> what sanitizer profile ran, under which caveats, and what report bundle should another person inspect?

### 2. BorrowSanitizer-specific aliasing evidence
This is **P-0465 BorrowSanitizer Workflow & Evidence Kit** territory:

- aliasing-model-sensitive findings
- FFI boundary mapping
- provenance-violation classification
- optional comparison against Miri
- minimization/reduction receipts

The receiver-facing question is:

> which aliasing/provenance finding happened, across which FFI boundary or unsafe surface, and how does it compare to earlier runs or Miri expectations?

### 3. Broad debuggability support posture
This is **P-0486 Debuggability Support Contract Kit** territory:

- symbols and sidecars
- support posture (`interactive_debugger`, `backtrace_only`, etc.)
- visualizer presence
- release drift

This is not a sanitizer result at all.
It is the artifact that says whether another human can debug the build effectively.

### 4. Cross-tool verification and assurance imports
These are **P-0485 Verification Campaign Workbench Kit** and **P-0503 Assurance Case Workbench Kit** territory:

- import sanitizer or BorrowSanitizer evidence conservatively
- keep lane-specific trust and coverage limits explicit
- do not treat one passing run as a complete safety argument

## Working rule

When touching sanitizer or unsafe-evidence work, future revisions must state explicitly:

1. whether the crate owns a **general sanitizer workflow** or a **BorrowSanitizer-specific aliasing lane**,
2. whether the main artifact is a **profile/report bundle**, a **finding/minimization bundle**, or a **debug-support receipt**,
3. what role **Miri comparison** plays (informational, corroborating, or absent),
4. and whether higher-level verification or assurance crates are merely **importing** the evidence.

Do not let the archive silently collapse:

- general sanitizer profiles,
- aliasing/provenance findings,
- debugger support posture,
- and assurance imports

into one fake “sanitizer result”.

The worthy crates here are the **lane-honest artifacts** above increasingly real substrate.
