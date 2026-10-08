# Cube deep audit rev0250

## Finding

The rev0249 path made real owner CSVs receiptable, but the next practical failure was still possible:
a maintainer could run receipt, triage, and staging as separate commands and then leave partial outputs
or note-shaped artifacts in whatever directory happened to be convenient. At the same time,
`tools/stage_owner_reply_csv.py` guarded SRC0 smoke fixtures but did not itself refuse archive-output
paths for ordinary real-reply staging notes.

That was a concrete custody leak. A proceed-staged note can contain minimized owner answers. Even when
safe enough for local staging, it should not land directly in `docs/`, `examples/`, `templates/`, or
release-control files.

## Change

Rev0250 adds `tools/intake_owner_reply_csv.py` as the bounded local default after a real CSV arrives.
It writes one scratch/external bundle:

1. `receipt.json`
2. `triage.json`
3. exactly one routed local artifact: `proceed-staged.md` or `outcome-note.md`
4. `bundle-manifest.json`

It also adds `tools/check_owner_reply_intake_bundle.py`, a Make target (`owner-reply-intake`), and
schema/request fields for `owner_reply_intake.intake_tool_path` and
`owner_reply_intake.intake_bundle_output_rule`.

## Refactor/audit repair

Normal staging output is now archive-output guarded. `tools/stage_owner_reply_csv.py --output` refuses
root files and `docs/`, `examples/`, `fixtures/`, `schemas/`, `templates/`, and `tools/`. The stage
validator now tests that refusal.

This is deliberately not a new evidence gate. It is a local-bundle guard that keeps the practical path
runnable while preventing premature archive copy/paste.

## What remains risky

The actual external dependency remains unchanged: no real owner has been contacted and no real
`SRC2+` packet has been imported. The next real move is still to send or adapt the eight-row
`AIEDU-SR-003` request. If a real CSV arrives, run the intake bundle. If it does not, record
`NO-OWNER-PACKET` after the existing response clock rather than adding doctrine.

## Boundary

Rev0250 does not close `FT-0181`, upgrade public language, or prove learning, safety, access,
workload, compliance, scale, or effectiveness. It only narrows the local intake path from many manual
commands to one bounded bundle.
