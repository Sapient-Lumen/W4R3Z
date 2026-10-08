---
id: P-0160
title: Codemod & API Migration Kit
status: idea
domains: [devtools, refactoring, tooling, ecosystem, maintenance]
last_reviewed: 2026-03-05
evidence:
  - https://doc.rust-lang.org/cargo/commands/cargo-fix.html
  - https://github.com/rust-lang/rustfix
  - https://docs.rs/rustfix
  - https://rust-analyzer.github.io/manual.html
---
# Problem

Rust has great building blocks for automated edits—`cargo fix` (compiler-suggested edits), `rustfix` (apply suggestions), and rust-analyzer assists (interactive refactorings).
But the ecosystem still lacks a *standard*, **packagable**, and **testable** way to ship “API migration codemods”:

- Library authors deprecate or break APIs and users face large manual migrations.
- One-off scripts are brittle and hard to validate across real-world code.
- There’s no stable artifact format for “this migration transformed your code like *this* for *these* reasons”.

# What it should provide

A codemod platform that makes migrations **repeatable, reviewable, and CI-friendly**.

## 1) A codemod crate format

- A codemod is a versioned package that contains:
  - matcher logic (AST/typed model where possible),
  - transformations (edits + optional generated shims),
  - a test corpus (before/after fixtures),
  - constraints (edition/MSRV/features).

## 2) A stable execution model

- `cargo codemod run <pkg>@<ver>` applies transformations and emits:
  - `codemod-report.json` (what changed, why, confidence),
  - unified diffs (human review),
  - optional “fallback instructions” for uncertain edits.

## 3) Safety rails and validation

- Mandatory preflight:
  - clean working tree (or explicit `--allow-dirty`),
  - build/test after (configurable),
  - “idempotence check” (re-running makes no diff).
- Corpus-based validation:
  - codemod package ships before/after fixtures; CI must pass.

## 4) Integration hooks

- Option A (pragmatic MVP): leverage compiler JSON diagnostics + token/AST rewriting where sufficient.
- Option B (power path): optional adapter to rust-analyzer’s analysis for richer transforms (feature-gated, not required).

# MVP plan (0.1)

- Define `codemod-report.json` + corpus layout.
- Provide a minimal engine that:
  - runs a codemod executable (Wasm or native) against a workspace,
  - applies edits safely,
  - produces report + diffs,
  - runs `cargo test` if requested.

# v1 plan

- Canonical library APIs for:
  - parsing + span mapping,
  - structured edits and conflict resolution,
  - workspace-wide renames and signature changes.
- A public registry “codemods” index (can start as GitHub list).
- Provenance: codemod run emits a signed “change capsule” for audit.

# Design constraints & sharp edges

- Avoid “format churn”: integrate with rustfmt post-apply, but keep diffs stable.
- Keep “typed refactoring” optional; start with what’s robust, not what’s maximal.
- Security: codemods are code—support sandboxing or at least clear trust prompts.

# Why this is epic

It creates a missing social contract for Rust evolution: breaking changes become *ship-with-codemod*, and maintainers can offer users a one-command migration with auditable evidence.
