# Basis provenance audit witnesses

This surface resolves `OQ-0227` by refusing to let schema-coverage routing or green generated packets outrun the receipt's session-underlier basis. A coverage audit can route root JSON validator evidence only if the basis witness says which immediate package was expected and observed, and if that basis is not a stale carryover from an older revision.

## Practice / observation

`rev0332` closed schema coverage, but a fresh audit found a deeper false-green seam: `REVISION-RECEIPT.json#basis_witness.expected_head` and `observed_head` still named `rev0330`, and `session_provenance` still described work from older packages. The generated `innovation-packet.json` faithfully copied those fields, so the derivative packet was internally consistent while the underlying basis was stale.

## Working synthesis

The current witness family is `basis_provenance_state` / `WVF-0132`. It distinguishes these allowed exact tokens:

- `expected-head-current`
- `observed-head-current`
- `session-provenance-aligned`
- `direct-underlier-anchored`
- `innovation-anchor-resynced`
- `stale-carryover-blocked`
- `mixed-basis-provenance`

`BASIS-PROVENANCE-AUDIT.json` is generated from `REVISION-RECEIPT.json`, `SURFACE-STATUS.json`, `RELEASE-MANIFEST.json`, and `innovation-packet.json`. The audit fails if the basis expected head, observed head, or session provenance still name an older carryover instead of the immediate underlier `rev0332`.

## Audit surfaces

- `BASIS-PROVENANCE-AUDIT.json`
- `docs/00-meta/basis-provenance-audit.md`
- `tools/basis_provenance_audit_lib.py`
- `tools/gen_basis_provenance_audit.py`
- `tools/check_basis_provenance_audit_contract.py`
- `tools/check_basis_provenance_currentness_contract.py`
- `tools/check_basis_provenance_witness_contract.py`
- `schemas/basis-provenance-audit.schema.json`
- `tools/check_current_witness_receipt_slot.py`

## Forbidden machinery

The following names remain quarantined, not admitted as authority: `basis-provenance-court`, `session-underlier-sovereign`, `reread-notary`, `anchor-freshness-tribunal`, `basis-waiver-board`, `resync-authority-senate`, `provenance-certification-court`, and `underlier-currentness-oracle`.

## Non-authority boundary

Basis provenance is session-underlier hygiene. It can fail closed when a receipt or derivative packet carries stale basis fields. It does not certify semantic truth, full historical reread, legal status, release legitimacy, archive minimality, or continuation authority.

## Reopen trigger

Reopen through `OQ-0228` if basis provenance rows become a reread-notary, if a resync token is treated as proof of full historical review, or if underlier-currentness evidence starts waiving direct inspection of the surfaces it claims to anchor.

## Validation checks

- `tools/check_basis_provenance_witness_contract.py`
- `tools/check_basis_provenance_audit_contract.py`
- `tools/check_basis_provenance_currentness_contract.py`
- `tools/check_schema_coverage_witness_contract.py`
- `tools/check_schema_conformance_audit_contract.py`
- `tools/check_schema_coverage_audit_contract.py`
- `tools/check_current_witness_receipt_slot.py`
