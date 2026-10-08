# Epic Proposal: Build Doctor Kit (`cargo builddoctor`)

## One-sentence pitch
Turn Rust build-performance troubleshooting into a portable, reviewable artifact by standardizing workflow-aware diagnoses, bottleneck classifications, and tradeoff-aware suggestions above Cargo’s emerging report surfaces.

## Deliverables
This epic should now be read as part of the shared **Build-State Evidence Stack**; see [`design/build-state-evidence-stack.md`](../design/build-state-evidence-stack.md) and [`design/build-state-evidence-pilot-program.md`](../design/build-state-evidence-pilot-program.md). The stack order is cache/layout truth → change-impact truth → diagnosis truth.

- `cargo builddoctor` reference tool
- Schemas:
  - `build-workflow-profile/v0`
  - `build-observation-pack/v0`
  - `build-bottleneck-profile/v0`
  - `build-suggestion-catalog/v0`
  - `build-diagnosis-report/v0`
  - `build-doctor-pack/v0`
- Adapters/importers for:
  - `cargo report timings`
  - `cargo report rebuild`
  - Cargo session metadata
  - optional richer attachments (self-profile, CI cache facts, editor/build contention hints)
- Docs:
  - workflow playbook (`cargo check`, incremental rebuild, IDE, CI, debugger-heavy dev)
  - trade-off catalog for common suggestions
  - issue/PR templates for attaching build-doctor packs

## Why now
- The compiler performance survey shows strong demand for better explanations of slow builds and for actionable suggestions grounded in the workflow the user actually cares about.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo is finally growing the raw telemetry needed for this (`cargo report rebuild`, `cargo report sessions`, better timings, build-analysis experiments), but that still leaves a missing interpretation layer.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The Cargo book now has an official build-performance guide, which proves the recommendations exist but are still largely prose and manual judgment rather than portable artifacts.
  https://doc.rust-lang.org/nightly/cargo/guide/build-performance.html

## Strategic value
This is a worthy contribution because it would let Rust projects answer questions like:
- “Why did this workspace suddenly get slower to rebuild?”
- “Is link time or proc-macro expansion the bottleneck here?”
- “Should we reduce debuginfo, switch linkers, or change workflow expectations?”
- “Why is rust-analyzer fighting Cargo on this repo?”
- “Which recommendation is justified for *this* workflow, and what will it cost us?”

That is ecosystem-shaping because it connects official guidance, Cargo telemetry, CI policy, IDE behavior, and project-local choices without requiring every team to become build-performance experts.

## Non-goals
- Replacing Cargo report work
- Replacing runtime/perf benchmarking tools
- Freezing every upstream internal data structure immediately
- Pretending all build slowness can be reduced to one score or one universal recommendation
- Building a hosted SaaS dashboard as a prerequisite

## Milestones
1. **v0 observation import + workflow profiles**
   - import Cargo timing/rebuild/session context
   - define initial workflow taxonomy
2. **v0.2 bottleneck taxonomy + report**
   - standardized bottleneck classes
   - ranked diagnosis report with evidence references
3. **v0.3 suggestion catalog + tradeoff model**
   - structured suggestions grounded in official guidance
   - explicit debugger/runtime/nightly/coverage trade-offs
4. **v1 ecosystem convergence**
   - optional editor/CI/self-profile adapters
   - issue/PR attachment norms
   - compatibility story with Cargo report stabilization

## Why it is distinct from neighboring ideas
Build Doctor Kit is the missing **interpretation layer** in the archive’s build-performance stack:
- **Cargo Report Kit** = raw reports
- **Build Cache Kit** = cache substrate
- **Build Interop Kit** = discovery/graph/plan/event substrate
- **Build Doctor Kit** = diagnosis + suggested next actions
- **Perf Labs** = runtime/perf evidence
