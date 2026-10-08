# Unsafe Contract Auditor product plan — 2026-03-22

This note turns **P-0120 Unsafe Contract Auditor Kit** into a more concrete build plan.

## Product thesis

The worthy crate is not a verifier that promises soundness.
It is a **reviewable unsafe obligation workflow** that helps maintainers, auditors, and adopters answer four questions:

1. what obligations exist,
2. where they came from,
3. what evidence touched them,
4. and where that evidence stopped.

## Core artifacts

### 1. `contract-authority.receipt.json`
Records the authority source for each unsafe obligation.
Key fields should include:
- authority source class (`docs`, `contract_attribute`, `imported_upstream`, `manual_manifest`, `std_contract_import`, `unknown`)
- location references
- freshness / tool version
- manual-review requirement

### 2. `obligation-map.report.json`
Inventory of unsafe surfaces and obligation classes.
Key fields should include:
- crate / module / item identity
- unsafe site or API surface
- obligation classes (`aliasing`, `initialization`, `lifetime`, `threading`, `ffi`, `symbol`, `abi`, `callback`, `other`)
- linked evidence ids
- unresolved-gaps list
- owner / review lane

### 3. `interpreter-boundary.receipt.json`
Records what the dynamic witness could not see.
Key fields should include:
- witness kind (`miri`, `loom`, `other`)
- target triple / host triple
- FFI posture
- platform / process / network limits
- callback / symbol / ABI observability
- overall boundary class (`local_only`, `partial_system`, `unknown`)

### 4. `witness-fidelity.report.json`
States what the witness result actually means.
Key fields should include:
- witness id and version
- verdict (`passed`, `failed`, `partial`, `not_run`)
- evidence strength (`strong_for_claimed_scope`, `advisory`, `weak`, `manual_review_required`)
- non-claims list
- comparison eligibility / drift notes

### 5. `unsafe-audit-bundle.manifest.json`
Portable manifest for receipts, logs, repro commands, and notes.

### 6. `authority-import.receipt.json`
Records imported authority and how it was normalized.
Key fields should include:
- source kind (`docs_section`, `contract_attribute`, `std_contract_import`, `upstream_manifest`, `manual_manifest`, `unknown`)
- imported location
- exactness class (`exact`, `translated`, `partial`, `inferred`, `unknown`)
- obligations covered
- freshness/tool-version notes
- conflicts with local declarations
- manual-review requirement

### 7. `obligation-drift.diff.json`
Compares unsafe posture between revisions without flattening site movement into semantic change.
Key fields should include:
- comparison basis
- added obligations
- removed obligations
- changed obligations
- change class (`authority_changed`, `site_moved`, `site_count_changed`, `obligation_class_changed`, `witness_linkage_changed`, `unresolved_gap_changed`, `owner_changed`)
- semantic-equivalence class
- manual-review requirement

### 8. `witness-comparison.report.json`
States whether two witness results are honestly comparable.
Key fields should include:
- compared witnesses/tool versions
- target/host lane
- comparability class (`comparable_same_claim_scope`, `scope_shifted`, `tool_semantics_shifted`, `not_comparable`)
- change summary
- recommended action
- manual-review requirement

## CLI sketch

- `cargo unsafe-audit init` — generate starter manifest and baseline authority file
- `cargo unsafe-audit run` — collect unsafe sites, run chosen witnesses, emit receipts
- `cargo unsafe-audit import-authority` — normalize docs / std-contract / upstream authority into receipts
- `cargo unsafe-audit diff old/ new/` — compare obligation maps and witness fidelity between revisions
- `cargo unsafe-audit compare-witness old/ new/` — compute witness-comparison reports when the comparison is honest
- `cargo unsafe-audit bundle` — create portable review bundle

## Planned package structure

- library crate for artifact types and diff logic
- cargo subcommand for workspace execution
- optional doc-rendering adapter for HTML / Markdown summaries

## Adoption sequence

### MVP
- manual manifest
- unsafe-site inventory
- Miri integration
- four core artifact types
- bundle writer

### v0.2
- Loom support
- CI helpers
- authority-import receipts
- obligation-drift diffs
- witness-comparison reports for release / toolchain changes

### v1
- importer adapters for future contract attributes / std-contract substrate
- richer review rendering
- interop with broader evidence-bundle / verification-campaign lanes

## What this crate should explicitly refuse to do

- promise soundness,
- hide boundary limitations,
- collapse all unsafe obligations into memory-model claims,
- or pretend every team must adopt formal methods before the crate is useful.
