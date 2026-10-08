# Epic Proposal: Change Impact Kit (`cargo impact`)

## One-sentence pitch
Give Rust one reviewable change-impact boundary over concrete change slices, semantic classifications, rebuild scope, and relink opportunities so future “relink don’t rebuild” progress becomes attachable instead of living inside hidden Cargo/rustc heuristics.

## Why this is worthy
This is an ecosystem-shaping contribution because it sits exactly where several major Rust efforts are converging:
- Cargo is beginning to persist rebuild reasons and expose them through `cargo report rebuilds`.
- The Rust project has an explicit flagship goal to avoid rebuilding reverse dependencies when a crate’s public interface has not changed.
- Cargo fingerprinting and build-script invalidation remain deliberately conservative and hard to explain after the fact.
- rustc’s incremental-query machinery already distinguishes “potentially affected” from “actually changed”, but that understanding does not yet travel as a portable artifact.

If the ecosystem does **not** establish a shared boundary here, future improvements will still happen — but users will keep seeing them as mysterious behavior changes rather than explainable, reviewable outcomes.

## Deliverables
This epic should now be read as part of the shared **Build-State Evidence Stack**; see [`design/build-state-evidence-stack.md`](../design/build-state-evidence-stack.md) and [`design/build-state-evidence-pilot-program.md`](../design/build-state-evidence-pilot-program.md). The stack order is cache/layout truth → change-impact truth → diagnosis truth.

### Schemas / artifact family
- `impact-subject/v0`
- `change-slice/v0`
- `impact-lane-profile/v0`
- `impact-classification-report/v0`
- `rebuild-scope-report/v0`
- `relink-opportunity-report/v0`
- `impact-diff-report/v0`
- `impact-pack/v0`

### Reference tooling
- `cargo impact slice`
- `cargo impact classify`
- `cargo impact scope`
- `cargo impact relink`
- `cargo impact diff`
- `cargo impact pack`

### Integrations
- Cargo build-analysis / `cargo report rebuilds`
- Cargo fingerprint-log import
- Public API / semver adapters
- Compile-Time Capabilities Kit adapters for build-script / proc-macro invalidation
- Build Cache Kit and Build Doctor Kit consumption paths

## Example theory-to-practice scenarios
### 1. “Why did this harmless edit rebuild half my graph?”
A team changes comments or formatting and sees broad rebuilds.
The kit should produce:
- one `change-slice` saying the change was doc/format-only,
- one `impact-classification-report` saying no semantic interface changed,
- one `rebuild-scope-report` distinguishing observed work from semantically required work,
- and, when possible, one `relink-opportunity-report` saying what could have been reused.

### 2. Reverse-dependency rebuild triage
A crate’s function body changes, but the public signature does not.
The kit should show:
- whether the change is local-only, codegen-sensitive, or interface-affecting,
- whether reverse dependencies recompiled because current behavior is conservative,
- and whether a relink-oriented lane could have done less work.

### 3. Build-script invalidation blowup
A broad `build.rs` rerun forces large downstream churn.
The kit should separate:
- the concrete file/environment change,
- the compile-time invalidation reason,
- the downstream rebuild scope,
- and whether the churn is semantic or policy-driven.

### 4. Toolchain / feature / target drift
A change in target, features, or toolchain causes rebuild scope to jump.
The kit should classify that as build-context change rather than pretending source edits alone explain everything.

## Distinctness from nearby ideas
This epic is **not**:
- another cache tool,
- another public-API diff tool,
- a replacement for Cargo rebuild diagnostics,
- a build-performance dashboard,
- or a speculative full-compiler oracle.

It is the missing **change-classification and rebuild-scope** substrate between them.

## Milestones
### M0 — vocabulary and fixtures
- stabilize minimal v0 schemas
- define classification and reason-code taxonomy
- collect representative fixtures:
  - doc-only
  - local body change
  - public signature change
  - build-script-triggered change
  - toolchain/feature drift

### M1 — import observed rebuild evidence
- adapter for `cargo report rebuilds`
- optional fingerprint-log import
- initial `rebuild-scope-report/v0`
- make current observed behavior attachable

### M2 — add semantic classification
- import bounded API/semantic-context evidence
- emit `impact-classification-report/v0`
- distinguish interface change from conservative rebuild

### M3 — relink opportunity lane
- emit `relink-opportunity-report/v0`
- compare current observed behavior against relink-oriented expectations
- attach confidence and blocking reasons honestly

### M4 — ecosystem consumption
- Build Doctor Kit imports impact packs for diagnosis
- Build Cache Kit references change-impact facts in reuse explanations
- CI / release tooling attaches packs to PRs and regression issues

## Non-goals
- Freezing Cargo/rustc internals prematurely
- Promising that v0 can perfectly classify all codegen-sensitive changes
- Pretending unchanged public API always implies unchanged downstream codegen
- Treating build-script or proc-macro churn as ordinary source edits
- Replacing compiler or Cargo optimization work with reporting alone

## Why now
- Rust Project Goals — Relink don’t Rebuild: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo Book — unstable build-analysis and `cargo report rebuilds`: https://doc.rust-lang.org/beta/cargo/reference/unstable.html
- Cargo FAQ — “Why is Cargo rebuilding my code?”: https://doc.rust-lang.org/cargo/faq.html
- Cargo fingerprint docs: https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/fingerprint/index.html
- rustc-dev-guide — incremental compilation and red-green: https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation-in-detail.html
- Cargo Book — build scripts and `rerun-if-*`: https://doc.rust-lang.org/cargo/reference/build-scripts.html

## Strategic outcome
If this succeeds, the ecosystem stops treating rebuild behavior as one opaque side effect of “incremental compilation”.
Instead, Rust gets a real review boundary for:
- the concrete edit,
- the semantic impact,
- the observed rebuild scope,
- and the relink/reuse opportunity.

That is the missing substrate needed for smarter builds to become legible, testable, and sharable.
