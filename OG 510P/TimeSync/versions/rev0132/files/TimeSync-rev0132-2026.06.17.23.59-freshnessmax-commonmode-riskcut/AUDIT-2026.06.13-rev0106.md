# AUDIT-2026.06.13-rev0106 — evidence-summary obligation refactor

## Focus

rev0106 continues the FT-0090 execution-first cleanup. I reviewed the dense evidence-summary branch in `tools/validate_archive.py` because it still mixed class-catalog consistency, redacted external-reference guardrails, profile-reference binding, non-provenance guard checks, and obligation-result semantics in one validator block.

## Risk found

The existing validator already rejected forbidden evidence classes, transport-only promotion, and several redacted-reference mistakes. The remaining usability gap was narrower but important: an obligation could say `result: met` while citing an evidence item that was not actually usable for a met result.

The riskiest cases were:

```text
presence: absent / unknown / not_applicable
value_state: ignored / conflicting / withdrawn
used_for: not_used
value_state: redacted without a salted commitment
```

Those states should be allowed to appear in a summary, but they should not be able to satisfy a met obligation.

## Change made

Added `tools/evidence_summary_semantics.py` and moved evidence-summary semantics into it. The monolithic validator now delegates evidence-class catalog and evidence-summary checks to that helper, while keeping a small callback wrapper for JSON Schema validation of embedded redacted external evidence references.

## New executable checks

rev0106 rejects:

```text
met obligation -> non-present evidence item
met obligation -> ignored/conflicting/withdrawn evidence item
met obligation -> item marked used_for: not_used
met obligation -> redacted evidence item without salted commitment
```

## Fixtures

Added three derivation-checked negative fixtures:

```text
examples/negative/evidence-summary-met-obligation-absent-item-invalid.json
examples/negative/evidence-summary-met-obligation-ignored-item-invalid.json
examples/negative/evidence-summary-redacted-obligation-without-commitment-invalid.json
```

These are derived from `examples/evaluator/evidence-input-summary-p3-satisfied.json` with explicit small patch operations in `tests/fixture-derivations.yaml`.

## Boundary kept

No new evidence registry was added. No hidden evidence is exported. Redacted evidence remains usable only when a salted commitment binds the redacted value. External provenance remains explicitly non-interpreted by TimeSync.
