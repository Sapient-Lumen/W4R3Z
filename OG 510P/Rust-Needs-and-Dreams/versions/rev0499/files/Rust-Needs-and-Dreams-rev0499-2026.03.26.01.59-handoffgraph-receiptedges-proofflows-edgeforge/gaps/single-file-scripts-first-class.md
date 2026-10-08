# Gap: Single-File Rust Scripts that Feel First-Class (ScriptKit)

## Summary
Rust is getting much closer to first-class one-file programs, but the ecosystem still lacks the **truth layer** that would make them genuinely dependable.

Cargo is now actively defining single-file packages:
- a `.rs` file can act as the package subject,
- frontmatter can embed a subset of `Cargo.toml`,
- defaulted manifest fields are documented,
- target-dir and lockfile behavior are documented,
- and `cargo <file.rs>` exists as an intended manifest-command path.

That is major progress.
But it still leaves an ecosystem gap:
- scripts are easy to run and hard to **review**,
- editor / CI / shell consumers may not identify the same subject,
- standalone-vs-repo-governed behavior is not yet a stable social contract,
- and policy / supply-chain / compile-time tooling still lacks a clean way to import one-file package truth.

## Ecosystem signals
- Rust’s 2026 flagships explicitly include **stabilize cargo-script**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s unstable-features docs define **single-file packages** with embedded frontmatter, explicit defaulted fields, disallowed fields, a hashed default `CARGO_TARGET_DIR`, and a lockfile located in `CARGO_TARGET_DIR`.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The January 2026 program-management update calls cargo-script one of the most anticipated features and explicitly highlights minimal reproducers and quick prototypes as high-value use cases.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The December 2025 goals update says frontmatter-format work moved forward, but rustdoc’s handling of frontmatter in doctests remained a blocker.
  https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- Cargo 1.94 says workspace/config discovery is still an active design problem and notes that cargo-script starts with **workspace auto-discovery disabled**.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer still has an open issue for shebang / single-file package support.
  https://github.com/rust-lang/rust-analyzer/issues/15318
- Cargo still has active UX issues such as suppressing Cargo noise on no-change script runs.
  https://github.com/rust-lang/cargo/issues/16388

## What is still missing
### 1. Reviewable script identity
A single file should not become a vague temp package once it leaves the author’s machine.
We need a stable subject id and explicit invocation posture.

### 2. Frontmatter/default truth
Because Cargo can infer values like package name and edition, tools and reviewers need to know what was explicit and what was defaulted.

### 3. Lock/cache/discovery truth
The script lane needs explicit answers to:
- where the lockfile lives,
- where build artifacts live,
- whether online resolution was expected,
- whether workspace/config discovery was intentionally disabled or intentionally opted in.

### 4. Consumer import truth
Editors, CI, docs, and issue trackers should be able to admit partial support rather than pretending every tool sees the same package.

### 5. Policyable one-file packages
Important scripts inside a repo should be able to carry packs, locks, toolchain hints, and optional supply-chain/safety attachments instead of bypassing normal review.

## What “good” looks like
- a one-file repro that another person can rerun with the same subject id, lock posture, and toolchain posture;
- a repo script that states whether it is standalone or repo-governed;
- an editor/CI import report that exposes lossiness rather than hiding it;
- and a portable `script-pack/v0` that can be attached to issues, CI runs, or policy gates without pretending a script is a full workspace.
