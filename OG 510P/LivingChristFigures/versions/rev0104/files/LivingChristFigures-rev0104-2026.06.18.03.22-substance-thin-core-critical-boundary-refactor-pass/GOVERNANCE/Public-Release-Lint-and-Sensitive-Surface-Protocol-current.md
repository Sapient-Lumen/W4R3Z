
# Public Release Lint and Sensitive Surface Protocol — current rev0051

## Purpose

This protocol separates three questions that earlier revisions could blur:

1. Does a sensitive surface exist somewhere in the working cube?
2. Is that surface allowed to remain internally as evidence, caution, or boundary language?
3. Is that surface safe to expose in the public layer?

The answer to question 1 may be yes while the answer to question 3 remains no.

## Instruments

- `tools/sensitive_surface_inventory.py` inventories configured sensitive surfaces across the working package.
- `tools/public_release_lint.py` scans only `PUBLIC/` files and treats high findings as public-handoff blockers.
- `tools/candidate_governance_snapshot.py` joins eligibility, link-review, lifecycle, consent/governance, and refresh posture into a candidate-level release gate.

## Rule

A public file is not safe because it is short, generated, or previously scrubbed. It is safe only after the public renderer, public lint, release contract, redaction scan, rule-specific scan, schema validation, and QA all agree that no configured public-handoff blocker remains.

## Short-code and partial-contact rule

Short helpline or crisis-line digits are contact data even when they are fewer than the older redaction scanner's phone-number threshold. Public rendering must redact contact shortcodes when they appear near hotline, helpline, lifeline, phone, call, text, SMS, WhatsApp, emergency, or intake language.

## Inventory caution

The sensitive-surface inventory is an internal audit aid. It may be too detailed for a public reading edition and should not be treated as a public-safe file merely because it is generated.

## rev0052 extension

Public lint and sensitive-surface inventories now feed `META/Release-Gate-Attestation-current.*`; the lint report is not just an advisory artifact. Row-level validation and generated-artifact provenance must also pass before handoff.
