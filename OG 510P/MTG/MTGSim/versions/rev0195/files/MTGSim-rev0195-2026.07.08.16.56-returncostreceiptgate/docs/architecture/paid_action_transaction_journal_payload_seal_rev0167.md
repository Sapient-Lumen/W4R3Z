# rev0167 — Paid-Action Transaction Journal Payload Seal

## Why this was the riskiest next seam

rev0166 made `MTGSim.PaidActionTransactionJournal.v1` parseable and verifier-visible, but the verifier still mostly reasoned one record at a time. That left a subtle artifact risk: a committed journal header could be kept while a valid row from some other journal was spliced in, or a future exporter could add stray fields that the parser would silently ignore. Individual transaction and snapshot hashes still caught direct payload tampering, but the artifact did not fail closed against row-level mixing or schema drift.

rev0167 therefore bumps the emitted journal format to `MTGSim.PaidActionTransactionJournal.v2` and adds a header-level `record_payload_hash`. The hash covers the ordered exported transaction rows, their parsed transaction payloads, their exported recomputed transaction hashes, and their committed/speculative snapshot recomputed hashes. It is not a cryptographic authenticity mechanism and does not replace state-bound verification, but it catches truncation, accidental splicing, stale-row substitution, and exporter/parser disagreement before a downstream agent treats the journal as coherent.

## Code changes

- Added `PaidActionTransactionJournalHeader::record_payload_hash`.
- Bumped `kPaidActionTransactionJournalSchemaVersion` from `1` to `2` for newly emitted journals.
- Kept parser awareness of v1 headers for compatibility, while v2 requires and verifies the new payload seal.
- Added strict header and record-field allowlists so unknown fields, unexpected snapshot-prefixed fields, and blank lines fail parsing instead of being ignored.
- Added `PaidActionTransactionJournalVerifyFailureKind::RecordPayloadHashMismatch` and CLI reporting as `record_payload_hash_mismatch`.
- Extended the existing journal parser/verifier regression to reject tampered payload hashes, unknown header fields, unknown record fields, spliced valid rows from another journal, and blank-line insertion.

## Online research context

Wizards' public rules page remains the authority surface for Comprehensive Rules access: https://magic.wizards.com/en/rules. The WPN rules-documents page remains a separate tournament/documentation surface: https://wpn.wizards.com/en/rules-documents. Scryfall bulk data still describes itself as bulk card-object data refreshed on a cadence rather than a rules procedure oracle: https://scryfall.com/docs/api/bulk-data. MTGJSON still describes itself as a portable card-data aggregation/download project: https://mtgjson.com/ and https://mtgjson.com/downloads/.

The design implication is unchanged: MTGSim should keep using external card-data projects as data surfaces, but the datacube's mission is the smaller trusted transition kernel: declare, pay, commit/rollback, export, verify.

## Audit/refactor note

This revision touched the journal parser boundary rather than adding another registry layer. The refactor deliberately centralizes known-field checks next to parsing helpers so future journal schema additions must be accepted explicitly. That is the useful bureaucracy: a fail-closed parser boundary, not another prose-only inventory.

## Evidence

- Release binary smoke: `reports/harness/cpp_allinone_release_rev0167_smoke.json` (`339/339`, 0 failures).
- CLI writer/verifier artifact: `reports/harness/paid_action_transaction_journal_rev0167_roundtrip.txt` and stdout/stderr companions.
- Datacube audit: `reports/audit/datacube_audit_rev0167_latest.json`.
- Rule coverage/progress: `reports/rules/rule_coverage_rev0167_latest.json`, `reports/rules/rules_progress_rev0167_latest.json`.
