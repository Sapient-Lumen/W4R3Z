# Safety-critical evidence stack — 2026-03-08

## Main judgment

The archive now has enough **evidence-producing** safety-critical proposals that another pass should stop inventing more isolated receipts unless it can explain where they sit in the stack.

The under-covered layer is now the **assurance-case assembly/export layer** above those receipts.

In other words:

- the lower layers increasingly know how to produce coverage, lint, contract, unsafe, and toolchain evidence,
- but the archive still needed a crate that could link those artifacts to explicit claims and emit a reviewable argument pack.

That is why this pass adds **P-0503 Assurance Case Workbench Kit**.

## The stack

### 1) Normative/reference substrate

These are not “assurance crates”, but they matter because high-assurance teams need stable references and toolchain/spec provenance.

- FLS cadence and specification maintenance
- normative unsafe documentation
- domain standards and project-specific requirement sets

### 2) Safety policy and semantic-substrate layer

These crates make safety-relevant expectations machine-readable.

- **P-0453 Safety Contract Consumer Kit**
- **P-0459 Clippy Safety Profile & Waiver Kit**
- **P-0460 Unsafe Field Invariant Ledger Kit**

### 3) Evidence-producing execution layer

These crates run checks and emit receipts.

- **P-0433 MC/DC Coverage Workbench Kit**
- **P-0465 BorrowSanitizer Workflow & Evidence Kit**
- unsafe-audit / invariant / lint / coverage / spec-reference outputs from sibling crates

### 4) Bundle/packaging substrate

This layer makes evidence portable and diffable.

- **P-0256 Evidence Bundle Core Kit**

### 5) Assurance-case assembly layer

This is the missing layer that was not yet represented clearly enough.

- **P-0503 Assurance Case Workbench Kit**

Its job is to:

- import evidence,
- connect evidence to claims and assumptions,
- preserve freshness/provenance/manual-review status,
- export conservative review packs,
- and produce change-impact diffs.

## What should not get collapsed together

### Not the same thing: evidence producer vs assurance case

A coverage receipt, contract snapshot, or lint waiver report is **not** an assurance case.
It is an input to one.

### Not the same thing: assurance workbench vs full certification platform

The missing crate is a **workbench and packager**, not a regulator-facing lifecycle suite.
It should not try to own hazard logs, full requirement databases, or organization-wide approval workflows.

### Not the same thing: assurance workbench vs raw GSN/SACM editor

GSN and SACM matter as interchange and visualization surfaces.
But the Rust-specific value begins at:

- importing Rust-native evidence bundles,
- linking them to claims,
- and diffing assurance posture over time.

A generic editor alone would be the wrong frontier.

## Immediate planning implication

For the next safety-critical passes, prefer one of these moves:

1. sharpen import contracts between **P-0503** and evidence-producing proposals,
2. add tiny fixture corpora proving stale/manual/assumed/satisfied transitions,
3. define one small claim-pattern library for common Rust safety arguments,
4. or tighten redaction and provenance semantics for exported packs.

Prefer **not** to:

- add another generic safety-case editor proposal,
- add another isolated receipt crate without stack placement,
- or blur claim assembly into “the tool certifies you”.

## Sources

- Rust safety-critical vision post: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust 2026 flagship goals: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- FLS update-capability goal: https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- Safety-Critical Rust Consortium: https://rustfoundation.org/safety-critical-rust-consortium/
- Rust Foundation 2025 review: https://rustfoundation.org/2025/
- SACM: https://www.omg.org/spec/SACM/2.3/About-SACM
- GSN Community Standard v1 (FAA mirror): https://www.faa.gov/about/office_org/headquarters_offices/ang/redac/redac-sas-201503-gsn-community-standard-v1.pdf
