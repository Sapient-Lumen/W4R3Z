## Execution addendum (rev0456)
This proposal should now be read through `design/compatibility-claims-execution-blueprint-2026Q1.md`.

Interpretation rule:
- the epic remains the broader program/band story;
- the execution blueprint is now the concrete answer for artifact shape, proving lanes, and refusal boundaries;
- and future edits should preserve imported-owner boundaries instead of letting the epic silently redefine support, acceptance, MSRV, or public-boundary truth.

# Epic Proposal: Compatibility Claims Stack (`cargo compat` + `compat-pack/v0`)

## Why this is worthy
Rust projects increasingly need to publish **compatibility claims that can be reviewed like contracts instead of inferred from folklore**.

The official signals are unusually aligned:
- Target tiers already distinguish stronger and weaker guarantees, including separate host-tool posture.
  https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
- Official support posture is actively changing: `x86_64-apple-darwin` was demoted to Tier 2 with host tools in Rust 1.90, while Rust 1.91 promoted `aarch64-pc-windows-msvc` to Tier 1.
  https://blog.rust-lang.org/2025/08/19/demoting-x86-64-apple-darwin-to-tier-2-with-host-tools/
  https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
- docs.rs changed its default target list in October 2025, proving that docs-target posture is part of the public compatibility story.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The 2026 debugging survey says users want multi-debugger, multi-OS support, visualizers, async debugging, and Rust expression evaluation. The compiler dev guide also documents real debugger asymmetries across GDB, LLDB, and CDB.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
  https://rustc-dev-guide.rust-lang.org/debuginfo/intro.html
- The Rust Reference exposes `debugger_visualizer`, which means debugger-facing presentation artifacts are a public ergonomics surface.
  https://doc.rust-lang.org/reference/attributes/debugger.html
- The 2025 State of Rust survey says online docs remain canonical while machine consumers rise, which increases the need for attachable compatibility truth rather than prose-only caveats.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The safety-critical adoption writeup explicitly recommends target-focused readiness checklists and ecosystem-wide MSRV conventions, which is a strong signal that long-lived support posture needs more reviewable artifacts than README prose.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The 2026 flagships keep next-solver stabilization live, which means advanced-pattern acceptance will keep moving in ways projects may need to explain.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s `supported-targets` RFC shows demand for first-class support declarations, but that alone would still not answer debugger-tuple or acceptance-surface questions.
  https://github.com/rust-lang/rfcs/pull/3759
- Cargo continues to emphasize plugins and companion tools because Cargo cannot be everything to everyone.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/

But the ecosystem still has no single honest handoff for **compatibility-claim truth**.
That means maintainers, release reviewers, docs authors, support engineers, CI systems, and safety-oriented adopters still have to reconstruct the answer from:
- target-tier docs and target notes,
- per-target runtime baseline prose,
- CI matrices,
- docs.rs metadata and defaults,
- debugger setup pages and visualizer scripts,
- `trybuild` fixtures and nightly notes,
- and scattered release caveats.

The missing contribution is a thin composition layer above those pieces, not another platform badge or hosted matrix service.

## Proposal
Define a **Compatibility Claims Stack** with:
- a reference companion CLI, `cargo compat`;
- a thin linked bundle, `compat-pack/v0`;
- imported evidence from:
  - Support Envelope artifacts,
  - Debuggability / debugger-tuple artifacts,
  - Acceptance Surface artifacts,
  - and optional release/docs/policy attachments;
- stable compatibility-facing artifacts:
  - `compat-subject/v0`
  - `compat-lane-catalog/v0`
  - `compat-claim-register/v0`
  - `compat-change-report/v0`
  - `compat-consumer-summary/v0`
  - `compat-pack/v0`

## Reference CLI shape
- `cargo compat export`
  - emit `compat-subject/v0` and `compat-lane-catalog/v0` for one release / crate / workspace subject
- `cargo compat check`
  - import support/debugger/acceptance attachments and emit `compat-claim-register/v0`
- `cargo compat diff --against <prior-pack|ref|path>`
  - emit `compat-change-report/v0` comparing support, debugger, acceptance, and docs-target posture
- `cargo compat render --for <docs|release|support|ci|policy|audit|assistant>`
  - emit `compat-consumer-summary/v0`
- `cargo compat pack`
  - produce `compat-pack/v0`
- `cargo compat verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace Support Envelope Kit, Acceptance Surface Kit, Debuggability Stack, docs.rs metadata, or future Cargo-native support declarations.

## What `compat-pack/v0` should contain
- `manifest.json`
- `compat-subject.json`
- `compat-lane-catalog.json`
- `compat-claim-register.json`
- optional `compat-change-report.json`
- one or more `compat-consumer-summary.json` attachments
- imported support/debugger/acceptance attachments or pointers
- checksums, provenance, and generator identity
- optional release/docs/policy/audit pointers

## Design principles
- **Lane identity before marketing.** Every claim starts by naming the lane.
- **Imported truths stay imported.** Support, debugger, and acceptance owners remain separate.
- **Declared and observed claims stay distinct.** A green declaration is not the same as an observed lane.
- **Debugger support is not implied by platform support.** Tuple truth must stay explicit.
- **Acceptance is not implied by stable compilation.** Pattern-family and compiler-lane scope must stay explicit.
- **Consumers import bounded conclusions.** Docs, release notes, support pages, CI, policy, audit, and assistant views each need their own summary.
- **Cargo-merger fantasies stay out of scope.** A useful companion layer is already a success.

## Early implementation order
1. released-binary support lane
2. debugger tuple lane
3. advanced-pattern acceptance lane
4. mixed-workspace compatibility bundle
5. long-lived / safety-oriented support lane

That order follows the real ecosystem pressure: first prove public support posture, then public debugger tuple truth, then acceptance drift on advanced patterns, then prove a realistic multi-lane workspace, and only after that widen into harder lifecycle and assurance consumers.

## Non-goals
- a universal compatibility badge;
- a giant hosted matrix UI;
- a replacement for target-tier policy or platform-support docs;
- a replacement for debugger work or compiler-lane harnesses;
- flattening platform support, debugger support, and acceptance into one status light.

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- which compatibility lanes exist for a subject;
- what kind of claim each lane makes;
- what evidence is declared versus observed;
- what debugger tuple support really exists;
- what advanced-pattern acceptance really exists on which compiler lanes;
- what changed since the previous release or toolchain;
- and what a given consumer may safely say,

without scraping README prose, reconstructing CI intent, or inferring scope from issue threads and release notes.

## Read this with
- `gaps/compatibility-claims-platform-debugger-and-acceptance-contracts.md`
- `design/compatibility-claims-stack.md`
- `design/compatibility-claims-pilot-program.md`
- `design/support-envelope-kit.md`
- `design/support-envelope-pilot-program.md`
- `design/acceptance-surface-kit.md`
- `design/debuggability-stack.md`
- `design/debugger-pilot-program.md`
