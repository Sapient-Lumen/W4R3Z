# Cube deep audit rev0242: owner reply intake collapse

## Finding

Rev0242 made the first `FT-0181` ask small enough to describe, but the sendable artifact was still
spread across several surfaces. The first-contact packet, owner request, sprint pack, action kit,
and minimum real-data request all pointed in the same direction, but a maintainer still had to decide
which table to paste, which rows were active, and whether the broader action-kit field list was
allowed in the first owner email.

That is the current high-risk waste pattern: **a first contact can be delayed by choosing among
archive surfaces even after the archive has agreed to ask for less**.

## What changed

Rev0242 collapses the first inbound ask into one exact sheet:

- `docs/30-operations/ft0181-eight-row-owner-reply-sheet.md` is now the active pasteable outbound
  body and inbound owner table.
- `examples/real-data-requests/ft0181-minimum-real-data-request.json` now includes
  `owner_reply_intake`, binding the machine-readable request to the sheet, its eight rows, accepted
  intake outcomes, `NO-OWNER-PACKET`, and local-only exclusions.
- `schemas/real-data-request.schema.json` and `tools/check_real_data_requests.py` now fail a ready
  request that lacks the eight-row intake link or accepted staging/block/no-owner outcomes.
- The owner import action kit no longer says the first owner packet may contain ten fields. It now
  points to the eight rows and moves any broader local note to optional follow-up.

## Risk reduced

This reduces three practical risks.

1. **Surface-choice drag.** A maintainer should not need to synthesize a sendable email from five
   documents. The sheet is the sendable artifact.
2. **Field creep after trimming.** The first request cannot silently expand back to a ten-field or
   export-flavored packet while still passing `check_real_data_requests.py`.
3. **Silence-to-bureaucracy relapse.** The intake object keeps `NO-OWNER-PACKET` as a valid progress
   result after one follow-up instead of encouraging another schema, registry, or meeting.

## What is still missing

No real owner has been contacted in this archive session. No real owner reply has been received. No
`SRC2+` packet exists. `FT-0181` remains live.

The next material action is now sharply defined: send the eight-row sheet to one plausible
`AIEDU-SR-003` owner path, or record that no owner path exists. If a reply arrives, run the owner
packet workbench. If no reply arrives after the short clock, record `NO-OWNER-PACKET` and either
name a different real owner path or stop the sprint.

## Refactor note

The audit did not add a new artifact family. It refactored the existing real-data-request family by
adding one intake subobject and one field-facing sheet. This is justified only because it removes a
real sendability ambiguity. Future changes should not add another pre-receipt control unless a real
owner reply exposes a failure that the eight-row sheet, workbench, decision board, change ticket,
live-window card, readout gate, post-readout dispatch, closeout, and claim lexicon cannot catch.
