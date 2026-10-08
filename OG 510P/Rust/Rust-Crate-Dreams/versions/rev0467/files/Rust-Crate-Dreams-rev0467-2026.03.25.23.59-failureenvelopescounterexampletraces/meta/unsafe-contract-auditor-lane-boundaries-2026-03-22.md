# Unsafe Contract Auditor lane boundaries — 2026-03-22

This note keeps **P-0120 Unsafe Contract Auditor Kit** from collapsing into neighboring lanes.

## What belongs in P-0120

P-0120 owns:
- unsafe obligation inventory,
- authority-source tracking,
- dynamic-witness boundary receipts,
- witness-fidelity statements,
- and portable unsafe-audit bundles.

## What does not belong here

### Not the same as P-0485 Verification Campaign Workbench Kit
P-0485 compares many evidence lanes and policy-evaluates whole campaigns.
P-0120 is narrower: it focuses on unsafe obligations and the honesty of specific unsafe witnesses.

### Not the same as P-0121 FFI Boundary & Bindings Conformance Kit
If the main hard problem is ownership, layout, error propagation, or callback behavior across languages, that belongs primarily in P-0121.
P-0120 may record that FFI is out of scope or partially witnessed, but it does not replace cross-language boundary contracts.

### Not the same as P-0434 Sanitizer Profile & Evidence Kit
Sanitizer evidence is operational debugging / bug-finding substrate.
P-0120 is about unsafe obligation authority and witness semantics.
A sanitizer report may join a larger audit bundle later, but it is not the same object.

### Not the same as a lint pack
Unsafe lints can flag syntax or patterns.
P-0120 exists to publish reviewable obligation/evidence artifacts, not only diagnostics.

## Guardrails

Do not let any of the following stand in for an honest unsafe contract:
- “Miri passed,”
- “the crate documents safety invariants,”
- “every unsafe block has comments,”
- “Loom found no schedule issue,”
- or “Rust 2024 forced `unsafe extern` already.”

A crate can have all of those truths and still leave authority source, FFI limits, symbol obligations, or manual-review debt unresolved.


### Not the same as std-contract substrate or unsafe-fields language work
The std-contracts goal and future contract attributes create machine-readable safety substrate.
Unsafe fields create a language surface for denoting field-carried invariants.
P-0120 sits above both: it imports whatever authority exists and publishes reviewable obligation/evidence artifacts for crate maintainers and adopters.
