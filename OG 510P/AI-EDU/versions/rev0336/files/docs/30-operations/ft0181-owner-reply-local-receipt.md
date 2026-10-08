# FT-0181 owner reply local receipt

## Purpose

This receipt is the smallest local custody artifact after an owner returns the eight-row CSV. Rev0251 keeps it available as a component, but the default path is now the bounded intake bundle followed, when `PROCEED-STAGED`, by a guarded workbench seed. The bundle creates the receipt, triage JSON, and routed local artifact together without copying owner answers into archive surfaces; the seed carries only hashes and `NOT_ACCEPTED` next-step metadata.

Use it before generating a proceed-staged note, re-asking once, or recording a block/no-packet
outcome. It is deliberately smaller than the workbench. It fingerprints the returned CSV, counts row
presence, records the triage outcome and next action, and keeps raw owner content local.

## Default bundle command

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
# then execute the emitted make owner-reply-intake ... SOURCE_CONTACT_STATUS=... command
```

Use the standalone receipt command only when you need the fingerprint alone:

```bash
python3 tools/receipt_owner_reply_csv.py returned-owner-reply.csv --output scratch/field/ft0181/owner-reply-receipts/returned-owner-reply.receipt.json
```

If you do not want a file yet, omit `--output` and read the JSON on stdout. The output path should be
`scratch/` or an external local path. The tool refuses root release-control files and archive-controlled
folders such as `docs/`, `examples/`, `fixtures/`, `schemas/`, `templates/`, and `tools/`.

## What the receipt contains

| Field family | Included | Not included |
|---|---|---|
| source fingerprint | CSV SHA-256, size, row count, columns, basename or relative reference | raw owner answers, learner rows, protected facts, row-answer hashes |
| content minimization | explicit `raw_owner_answers_copied=false` and `row_answer_hashes_included=false` | pasted owner narrative or blocked material |
| row presence | nonempty, blank, and unknown row IDs | the answer text behind those rows |
| triage summary | outcome, staging flag, real-packet flag, next action, reason count | full triage reasons that might tempt copy/paste |
| claim ceiling | local receipt only; not `SRC2+` acceptance or closure evidence | public claims or proof of learning/safety/workload benefit |

## Use rule

A receipt can make a returned file traceable. It cannot make the file acceptable.

After standalone receipt:

1. Prefer `tools/intake_owner_reply_csv.py` so receipt, triage, and the routed local artifact stay in one scratch bundle.
2. If triage says `PROCEED-STAGED`, run `tools/seed_owner_packet_workbench.py` on the intake bundle before opening the workbench; the seed is `NOT_ACCEPTED` and copies no owner answers.
3. Then copy only minimized survivor rows from the generated proceed-staged note into the workbench.
4. If triage says `RE-ASK-ONCE`, send only the one clarification in
   `templates/ft0181-owner-reask-once-message.md`.
5. If triage says `BLOCK-*` or `NO-OWNER-PACKET`, use
   `templates/ft0181-triage-outcome-note-template.md` and keep forbidden material local.

Do not use the receipt to broaden the owner ask, infer implementation approval, or claim that
`FT-0181` is closure-ready.

## Smoke boundary

Normal receipt creation refuses files under `fixtures/` and rows labeled as synthetic smoke. Use
`make owner-reply-smoke` for the SRC0 plumbing rehearsal. Do not create a normal receipt for smoke
output, and do not paste smoke receipt or smoke staging output into custody, public summaries, or
release records.

## Audit/refactor note

Rev0251 keeps the rev0249 receipt but wraps it in a bounded intake bundle and workbench-seed handoff. The audit repair is that staging notes can contain minimized owner answers and intake manifests can otherwise become self-hash stale, so normal staging, intake bundle, and seed outputs are scratch/external only and blocked from archive-controlled paths.
