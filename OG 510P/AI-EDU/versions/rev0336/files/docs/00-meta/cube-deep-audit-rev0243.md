# Cube deep audit rev0243: fillable reply template and pre-workbench triage

## Finding

Rev0242 made the owner ask exact, but it still assumed the owner would edit a Markdown table or
email body correctly. That is a practical risk. Real owners often reply faster to a small file or
form, and they may otherwise attach the wrong thing: a full export, screenshot, vendor dashboard,
raw roster row, or narrative that mixes protected facts with ordinary workflow notes.

The risk is not missing doctrine. The risk is that the first owner reply arrives in a format that is
slow to triage or unsafe to copy into the archive. If that happens, the cube can waste another pass
inventing intake process instead of deciding `PROCEED-STAGED`, `RE-ASK-ONCE`, `BLOCK-*`, or
`NO-OWNER-PACKET`.

## What changed

Rev0243 adds one fillable, non-canonical-control artifact and tightens the existing request family:

- `templates/ft0181-eight-row-owner-reply-template.csv` is the owner-fillable twin of the eight-row
  Markdown sheet.
- `examples/real-data-requests/ft0181-minimum-real-data-request.json` now points to both the human
  sheet and the CSV template through `owner_reply_intake.reply_template_path`.
- `schemas/real-data-request.schema.json` and `tools/check_real_data_requests.py` now require a
  ready request to name a CSV template, validate that it has exactly eight blank owner-response rows,
  and check that it carries local-only cautions for raw, protected, small-cell, and vendor material.
- `ft0181-owner-packet-workbench.md` now starts with a pre-workbench triage step so a returned sheet
  is screened before any broader form is opened.
- `FOLLOWTHROUGH_QUEUE.json` now matches the three-day initial reply, one-follow-up, seven-business-day
  `NO-OWNER-PACKET` clock instead of carrying a stale five-day action note.

## Risk reduced

This reduces four practical risks.

1. **Attachment drift.** The owner has one small file to fill rather than a reason to improvise an
   export or screenshot bundle.
2. **Unsafe copy/paste.** The workbench now says to triage before copying returned rows into archive
   fields.
3. **Template creep.** The validator fails a ready request if the fillable template grows beyond the
   eight owner rows or arrives pre-filled with invented answers.
4. **Process relapse.** A bad or missing reply routes to `RE-ASK-ONCE`, `BLOCK-*`, or
   `NO-OWNER-PACKET`; it does not justify a new registry or another pre-receipt gate.

## What is still missing

No owner has been contacted in this archive session. No filled CSV or eight-row table has been
received. No `SRC2+` packet exists. `FT-0181` remains live.

The next material action is still external: send the sheet or CSV to one plausible `AIEDU-SR-003`
owner path. If a reply returns, use the pre-workbench triage table first. If no reply returns after
one follow-up and seven business days, record `NO-OWNER-PACKET` rather than broadening the request.

## Refactor note

This is not a new evidence gate. It is a practical form factor for the existing eight-row intake and
a guard against dumping unsafe owner material into the workbench. The cube should not add another
pre-receipt surface unless a real returned sheet exposes a failure that the eight-row sheet, CSV
fill-in template, triage step, workbench, decision board, change ticket, live-window card, readout,
post-readout dispatch, closeout, and claim lexicon cannot catch.
