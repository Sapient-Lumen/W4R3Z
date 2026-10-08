# rev0166 — Paid-Action Transaction Journal Parser/Verifier CLI

## Heart of the change

rev0165 made the paid-action transaction spine visible outside private engine structs. rev0166 makes that exported `MTGSim.PaidActionTransactionJournal.v1` artifact challengeable: the engine can now parse the line-oriented journal, recompute terminal transaction hashes, recompute committed/rollback declaration snapshot hashes, and reject tampering without replaying an entire game.

This is deliberately a code-bearing verifier seam, not a new doctrine layer. The practical risk was that future agents or offline auditors would treat a journal row as trusted because MTGSim emitted it. The new surface lets them verify that the row and nested declaration snapshot still hash to the claimed receipt, and a state-bound verifier can compare the artifact against the producing `GameState` counts, state hash, journal hash, and transaction hashes.

## Online rules refresh

Online research during this pass rechecked Wizards' public rules page, which links the current Comprehensive Rules downloads: <https://magic.wizards.com/en/rules>. The observed current text artifact remains <https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.txt>, effective June 19, 2026. The local coverage ledger remains intentionally pinned to the packaged 2026-04-17 source manifest until a dedicated rules-diff revision, but this executable change is anchored to the current online paid-action/rollback model: spell casting locks costs and payment order around 601.2f-h; activated abilities continue to mirror the spell-casting payment sequence through 602.2/602.2b; illegal-action reversal remains tied to 733.

## Code changes

- Added public `PaidActionTransactionJournalHeader`, `PaidActionTransactionJournalRecord`, `PaidActionTransactionJournal`, parse result, verifier result, and verifier failure-kind types.
- Added `parse_paid_action_transaction_journal(...)`, `verify_paid_action_transaction_journal(...)`, and `verify_paid_action_transaction_journal_for_state(...)`.
- Added CLI support for `mtgsim_cli --verify-paid-action-journal JOURNAL` and `mtgsim_cli --paid-action-journal-roundtrip JOURNAL`.
- Added a regression that parses committed and rollback journals, verifies them against a producing `GameState`, and rejects tampered transaction hash, committed snapshot hash, speculative rollback snapshot hash, and state-binding hash fields.

## Audit/refactor notes

The audit/refactor target was the export/access seam. rev0165 had a serializer and demo writer; rev0166 moves the one-way artifact into a round-trippable, externally checkable format. The new fixture helpers factor committed and rollback paid-mana game construction out of the individual tests so later ability/loyalty journal verifier coverage can reuse the same shape without copy-pasted setup.

## Evidence

- All-in-one release smoke: `339/339` C++ cases passed with `0` failures.
- Targeted verifier case: `test_paid_action_transaction_journal_parse_verify_rejects_tampering`.
- CLI roundtrip evidence: `reports/harness/paid_action_transaction_journal_rev0166_roundtrip.stdout.txt`.
- Rule coverage: `0` errors, `0` warnings, `1676` linked tests.
- Datacube audit: `reports/audit/datacube_audit_rev0166_latest.json` after final packaging hygiene.

## Remaining risk

The verifier is intentionally format/hash verification, not a complete replay bundle. The next risky slice is multi-record journal verification across mixed spell, activated-ability, and loyalty transactions, followed by binding journal artifacts into a replay manifest that can reconstruct pre/post state roots instead of only checking the producing state header.
