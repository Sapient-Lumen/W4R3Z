# Lint idempotence and release provenance witnesses

This surface resolves `OQ-0224` by treating validation-side mutation as a release-hardening defect rather than as harmless lint noise.

## Practice / observation

A clean `rev0329` extraction could run `make lint`, pass the full suite, and still rewrite `RELEASE-PROVENANCE.json` from package-release provenance to helper-generator provenance. The same invocation could also leave `tools/__pycache__` artifacts. Both effects are operational side effects hidden by a green lint count.

## Working synthesis

The current witness family is `lint_idempotence_state` / `WVF-0129`. It distinguishes these allowed exact tokens:

- `lint-nonmutating`
- `release-provenance-stable`
- `bytecode-side-effects-blocked`
- `integrity-regeneration-stable`
- `clean-extraction-idempotent`
- `generated-surface-non-authoritative`
- `mixed-lint-idempotence`

`tools/gen_release_integrity.py` now regenerates canonical package provenance derived from `RELEASE-MANIFEST.json` instead of claiming that the helper script is the packaged-release generator. `Makefile` sets `PYTHONDONTWRITEBYTECODE=1`, and `tools/run_lint_suite.py` sets `sys.dont_write_bytecode = True` before importing helper modules.

## Audit surfaces

- `LINT-IDEMPOTENCE-AUDIT.json`
- `docs/00-meta/lint-idempotence-audit.md`
- `tools/lint_idempotence_audit_lib.py`
- `tools/gen_lint_idempotence_audit.py`
- `tools/check_lint_idempotence_audit_contract.py`
- `tools/check_lint_idempotence_witness_contract.py`
- `tools/check_current_witness_receipt_slot.py`
- `tools/check_release_integrity_contract.py`
- `tools/check_json_schema_surface_contract.py`

## Forbidden machinery

The following names remain quarantined, not admitted as authority: `lint-idempotence-court`, `provenance-sovereign`, `generator-authority-board`, `bytecode-tribunal`, `clean-extraction-notary`, `release-provenance-court`, `mutation-waiver-senate`, and `idempotence-certification-authority`.

## Non-authority boundary

`LINT-IDEMPOTENCE-AUDIT.json` blocks validation-side mutation and provenance drift. It does not certify semantic truth, legal status, minimality, canon sufficiency, or continuation authority. A clean, non-mutating lint run is an operational hygiene witness, not a court.

## Reopen trigger

Reopen through `OQ-0225` if idempotence evidence begins to certify release legitimacy, if generated audits become self-authorizing, or if clean-extraction tests are used to waive direct receipt/canon review.
