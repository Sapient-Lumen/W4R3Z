# DeriveBSD rev0561 session review

## Focus

This pass continued the scarce FreeBSD host-proof import lane without adding a new registry or doctrine surface. The risk addressed was durable provenance after a one-command sealed import: `import.receipt.json` previously described the transient unsealed scratch handoff, which is removed by default, and did not bind the original sealed archive bytes.

## What changed

- Added durable `source_transport` provenance to FreeBSD host-proof import receipts.
- Direct loose-handoff imports now record `kind = unsealed-handoff-directory`, source handoff path, and the byte digest of `SHA256SUMS`.
- One-command sealed imports now record `kind = deterministic-sealed-handoff-archive`, archive path, archive byte SHA-256, archive size, archive format, sealed import policy, transient scratch handoff, and cleanup behavior.
- Refactored source-transport kind and policy strings into `tools/freebsd/host_proof_contract.py`.
- Extended the import-root auditor so missing, stale, or inconsistent `source_transport` provenance fails.
- Extended importer, sealed-importer, and import-audit release-critical checks with tamper cases for missing provenance and kind-specific invariants.
- Refreshed current docs, examples, generated catalogs, and hygiene ledgers for `2026-06-16r590`.
- Pruned front-door sediment in `docs/00-index.md` rather than raising its line/byte budget.

## Validation

- Captured `release-critical` ledger: 48 / 48 passed.
- `schema-cube-audit`: 3 / 3 passed.
- `validate_spec_examples.py`: 469 examples validated.
- Strict duplicate-key scan: 1426 JSON files scanned.
- Generated docs and generated artifact version checks passed.

## Remaining risk

The cube still does not contain a non-simulated FreeBSD `real-host-proof` import. This revision improves the cloudtainer receive/import/audit path so that, when scarce real host proof arrives, the durable import receipt still binds the sealed transport artifact instead of only remembering removed scratch state.
