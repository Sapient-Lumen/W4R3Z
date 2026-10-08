# Rev0620 contract-table digest binding

## What changed

Rev0620 stops trusting the operation-contract table's self-declared root label as sufficient evidence for the enriched table that the runner actually uses. The policy profile now carries `operation_contract_table_digest_sha256`, and the runner compares it with `sha256` of the exact contract-table file bytes before any route/channel normalization occurs.

This directly addresses the highest-risk rev0619 finding: a caller could previously change a route in `gateway/rev0618-cpp-slim-normalization-contract-table.json`, preserve the declared `operation_contract_root_sha256`, and keep the signed policy envelope valid. That substitution is now rejected because the table byte digest changes.

## Validator probe

`tools/validate_rev0620_contract_table_digest_binding.py` mutates the first OpenAPI route while preserving the legacy declared operation-contract root. The revised binary fails before processing cases with:

`operation contract table digest does not match operator-pinned policy profile digest`

The validator also removes the new pin from the controls file and verifies that the runner fails closed with:

`policy profile is missing the operator-pinned operation_contract_table_digest_sha256`

The generated audit is `audit/rev0620-contract-table-digest-binding-audit.json`.

## Related repair carried forward

The revision retains the rev0619 SQLite evidence fix: schema v3 persists `operation_id` and `contract_digest_sha256` from verified JWT claims, not from normalized case metadata. The validator decodes all 326 positive fixture JWTs and compares the stored SQLite rows to those verified claim pairs. It also rejects legacy schema-v2 profiles and a schema-v3 row with an empty digest.

## Remaining ceiling

This is a practical local hardening step, not the final trust model. The new table digest is pinned by the operator-supplied controls file; it is not yet a signed canonical contract-table root with external release provenance. The next substantive step should be one signed operator-root configuration that binds the contract table digest, identity profile, policy envelopes, ledger backend profile, restore roots, runtime clock source, and allowed execution mode.
