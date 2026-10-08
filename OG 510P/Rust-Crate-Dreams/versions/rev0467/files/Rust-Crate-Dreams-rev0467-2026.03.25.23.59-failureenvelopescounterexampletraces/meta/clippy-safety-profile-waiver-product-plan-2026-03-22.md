# Clippy Safety Profile & Waiver product plan — 2026-03-22

This note turns **P-0459 Clippy Safety Profile & Waiver Kit** into a more concrete build plan.

## Product thesis

The worthy crate is not a new lint engine.
It is a **reviewable lint-policy workflow** that helps maintainers, auditors, and adopters answer five questions:

1. what policy was intended,
2. where the effective policy actually came from,
3. what scope was really checked,
4. which findings came from which diagnostic channel,
5. and what changed across revisions.

## Core artifacts

### 1. `policy-authority.receipt.json`
Records where each effective lint decision came from.
Key fields should include:
- crate / package / workspace identity
- tool (`rust`, `clippy`, `cargo`)
- lint or lint group name
- effective level and priority
- authority source (`workspace_lints`, `package_lints`, `clippy_toml`, `inline_attribute`, `imported_policy`, `nightly_cargo_lints`, `unknown`)
- override chain
- review notes / unresolved gaps

### 2. `checked-scope.matrix.json`
States what was actually checked.
Key fields should include:
- workspace/package selection
- target(s)
- feature selection mode
- tests / benches / examples participation
- private-item posture
- doc/test build participation
- toolchain id and channel
- unexecuted expected cells

### 3. `diagnostic-channel.receipt.json`
Keeps finding provenance honest.
Key fields should include:
- finding producer (`rustc`, `clippy`, `cargo`)
- stability (`stable`, `nightly`, `experimental_adapter`)
- command and flags
- advisory/blocking class
- source bundle ids
- import caveats

### 4. `waiver-decision.record.json`
Records explicit exceptions.
Key fields should include:
- lint identity
- scope
- rationale
- owner
- expiry / review date
- source reference (`inline_attribute`, `waiver_file`, `ci_override`, `manual_review`)
- risk posture

### 5. `lint-policy-drift.diff.json`
Compares two revisions and classifies drift.
Key fields should include:
- old/new revision ids
- drift categories
- severity / review recommendation
- linked authority/scope/channel/waiver ids

### 6. `lint-support-bundle.manifest.json`
Portable manifest for receipts, raw findings, source snippets, and notes.

## CLI sketch

- `cargo clippy-profile init` — generate starter policy and waiver vocabulary
- `cargo clippy-profile capture` — execute declared policy and emit receipts
- `cargo clippy-profile explain <lint>` — explain effective authority and scope
- `cargo clippy-profile diff old/ new/` — compare lint posture between revisions
- `cargo clippy-profile bundle` — create portable review bundle

## Planned package structure

- library crate for artifact types, capture, and diff logic
- cargo subcommand for workspace execution
- optional render adapters for Markdown / SARIF / HTML

## Adoption sequence

### MVP
- manual policy file
- policy-authority receipt
- checked-scope matrix
- waiver record
- bundle writer

### v0.2
- diagnostic-channel receipt
- drift mode for release comparison
- CI helpers
- Markdown rendering

### v1
- importers for Cargo workspace rollout data
- richer fixture corpus
- interop with unsafe-contract, docs-support, and evidence-bundle lanes

## What this crate should explicitly refuse to do

- define official Rust lint policy,
- collapse stable and nightly findings into one verdict,
- infer full scope from one command line,
- or promise certification from green output.
