
# BorrowSanitizer Workflow & Evidence Kit fixtures

These fixtures exist to make **P-0465 BorrowSanitizer Workflow & Evidence Kit** look buildable instead of merely timely.

The receiver-facing question is:

> what files should another maintainer or unsafe-code reviewer receive in order to understand a BorrowSanitizer-era finding, its FFI context, and whether it compares meaningfully to prior runs or Miri expectations?

## Minimal pack for 0.1

- `bsan-profile.schema.json` — toolchain, instrumentation lane, workload, FFI policy, and redaction defaults.
- `ffi-boundary-map.schema.json` — the foreign boundary or unsafe seam that matters for interpretation.
- `bsan-run.receipt.schema.json` — normalized run identity, target, toolchain, outcome counts, and caveats.
- `provenance-violation.schema.json` — one normalized finding with severity, evidence, and classification.
- `miri-compare.schema.json` — optional comparison against Miri or an expectation corpus.
- `reduction.receipt.schema.json` — how a finding was minimized or why minimization is still pending.

## Design rules

- Keep **general sanitizer workflow** separate from **BorrowSanitizer-specific aliasing/provenance evidence**.
- Keep **FFI boundary truth** separate from the raw finding payload.
- Keep **Miri comparison** explicitly optional and informational.
- Preserve `manual_review_required`, `tool_mismatch`, and `not_comparable` as honest outputs.

## Intended first scenarios

1. `cxx_callback_alias_violation` — mixed Rust/C++ callback ownership where aliasing/provenance confusion crosses the FFI boundary.
2. `pin_projection_reborrow_regression` — a Rust-heavy unsafe abstraction where a projection/reborrow change triggers a provenance warning and needs minimization plus Miri comparison.
