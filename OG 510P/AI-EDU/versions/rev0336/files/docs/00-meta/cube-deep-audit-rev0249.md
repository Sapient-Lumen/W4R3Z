# Cube deep audit rev0249 — owner-reply local receipt boundary

## Finding

Rev0248 correctly separated SRC0 smoke fixtures from real owner staging, but the first real returned
CSV still had a custody gap. A maintainer could triage and stage a CSV, then later be unable to show
which local source file produced the staging note without copying the owner answers into a broader
archive surface.

That is a practical risk, not a doctrine gap. The archive needed a small source fingerprint before
staging, not another approval board.

## Correction

Rev0249 adds `tools/receipt_owner_reply_csv.py` and
`docs/30-operations/ft0181-owner-reply-local-receipt.md`. The receipt tool records:

- source CSV SHA-256;
- size, row count, column list, and safe source reference;
- source truth class at receipt;
- row-presence counts and blank/unknown row IDs;
- triage outcome, staging flag, and next action;
- an explicit claim ceiling and `FT-0181` live status.

It does not copy raw owner answers, row-answer hashes, learner rows, protected facts, small cells,
credentials, or public claim language.

## Audit/refactor

The refactor moves receipt handling before staging in the active owner-reply path:

```bash
python3 tools/receipt_owner_reply_csv.py returned-owner-reply.csv --output scratch/owner-reply-receipts/returned-owner-reply.receipt.json
python3 tools/triage_owner_reply_csv.py returned-owner-reply.csv --json
```

The receipt output is local/scratch metadata. The tool refuses normal receipt creation for `fixtures/`
or smoke-labeled rows and refuses output into root, `docs/`, `examples/`, `fixtures/`, `schemas/`,
`templates/`, or `tools/`.

## What this fixes

- A real owner CSV can now be fingerprinted before any answer text moves.
- A blocked or overbroad CSV can be recorded as metadata without importing the blocked content.
- A proceed-staged note can be tied back to a source hash.
- Smoke fixtures remain runnable through the smoke harness but cannot receive ordinary owner-reply
  receipts.

## What this does not fix

No owner has been contacted. No returned CSV exists. No `SRC2+` evidence has been imported. The local
receipt is not acceptance, not closure evidence, and not public-summary support. `FT-0181` remains
live.

## Next best move

Send or adapt the eight-row `AIEDU-SR-003` owner sheet. If a CSV returns, run receipt, then triage,
then follow the single routed artifact. Do not add another registry unless this executable path fails
on a real packet in a way the existing block/re-ask/stage routes cannot represent.
