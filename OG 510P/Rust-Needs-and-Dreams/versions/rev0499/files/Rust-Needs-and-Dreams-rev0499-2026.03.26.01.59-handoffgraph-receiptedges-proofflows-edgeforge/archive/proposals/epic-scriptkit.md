# Epic Proposal: ScriptKit (portable truth for Cargo single-file packages)

## One-sentence pitch
Turn Cargo single-file packages into a credible ecosystem execution lane by standardizing **subject identity, frontmatter/default truth, lock/cache posture, consumer-import reports, and portable script packs**.

## What makes this worthy now
This no longer reads like a speculative “maybe Rust should have scripting” proposal.
Cargo is already making single-file packages real.
The worthy contribution is now the layer that keeps them from turning into folklore.

Recent official signals are unusually aligned:
- cargo-script is a 2026 flagship,
- Cargo’s unstable docs define concrete single-file package semantics,
- the Rust project is actively advertising scripts for quick prototypes and minimal reproducers,
- workspace discovery questions are being discussed explicitly,
- and editor / rustdoc / output UX still has open edges that need honest consumer contracts.

## Deliverables
- `cargo-scriptkit` reference implementation (external subcommand first)
- schemas:
  - `script-subject/v0`
  - `script-frontmatter-report/v0`
  - `script-lane-profile/v0`
  - `script-run-report/v0`
  - `script-consumer-import-report/v0`
  - `script-pack/v0`
- reference scorecards / example packs for bug repros, shebang utilities, and repo scripts
- CI/editor guidance for importing the same subject id instead of inventing temp-project folklore
- policy hooks for important repo scripts

## Why now
- Rust’s 2026 flagships explicitly plan to stabilize cargo-script.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s unstable docs already define many of the low-level rules we need to preserve rather than guess.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The January 2026 program-management update explicitly frames cargo-script as valuable for one-file bug repros and quick prototypes.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The December 2025 goals update and current issues show that frontmatter/rustdoc/editor/output details still need execution discipline.
  https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/ ; https://github.com/rust-lang/rust-analyzer/issues/15318 ; https://github.com/rust-lang/cargo/issues/16388

## Non-goals
- Replacing Cargo’s implementation
- Building a giant script registry or publication portal
- Treating scripts as a backdoor that escapes compile-time / policy / repo-governance review
- Assuming all scripts should live in workspaces
- Pretending editor/CI parity already exists

## Milestones
1. **v0 minimal bug-repro lane**
   - stable subject/frontmatter/lane reports
   - pack + verify flow
   - explicit toolchain / lock posture
2. **v0.2 shebang utility lane**
   - invocation-mode truth
   - rerun/output-mode reporting
   - partial-support import reports
3. **v0.3 in-repo automation lane**
   - standalone vs repo-governed distinction
   - config/workspace posture
   - optional policy attachments
4. **v0.4 editor + CI import lane**
   - subject-id matching
   - diagnostics path fidelity notes
   - explicit lossiness markers
5. **v1 workspace opt-in + policy lane**
   - future-proof opt-in semantics
   - stronger governance / release / supply-chain consumers

## Relationship to the Compile-Time Surface stack
This proposal remains adjacent rather than central to the compile-time stack described in [`design/compile-time-surface-pilot-program.md`](../design/compile-time-surface-pilot-program.md).
Its strategic role is to make small, shareable Rust programs and repros carry enough identity, lock, toolchain, discovery, and provenance truth that they can plug into the same review culture instead of living outside it.

## Relationship to Repo Composition
The archive should also treat ScriptKit as a bridge into the Repo Composition Stack.
A committed `scripts/*.rs` lane is only healthy if standalone-vs-workspace posture, config inheritance, and lock persistence remain explicit instead of being accidental side effects of directory layout.
