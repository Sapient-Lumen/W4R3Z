# FT-0181 owner re-ask once message

Use this only when `tools/triage_owner_reply_csv.py` returns `RE-ASK-ONCE` for the first
`AIEDU-SR-003` eight-row owner reply. Do not use it to add rows, request a full export, invite raw
learner data, or reopen the first-contact scope.

## Subject

One clarification on the draft-reminder owner reply

## Message

Hello,

Thank you for the eight-row reply. I can keep the review small, but I need one clarification before
staging it internally.

Could you please update only the row(s) listed below and resend the same eight-row sheet or CSV?

- Row(s) needing clarification: `[row_id(s)]`
- Clarification needed: `[brief field meaning, method note, date/source boundary, or missing answer]`

Please do not attach a full LMS export, roster, screenshot bundle, gradebook rows, messages,
protected-support facts, small cells, vendor dashboard, raw telemetry, credentials, system prompts,
or other raw material. A short aggregate/minimized correction is enough.

If those rows cannot be answered without broader or protected material, please say so. I will record
the result as a block or `NO-OWNER-PACKET` rather than widening the request.

Thanks.

## Boundary

This is the only follow-up allowed by the first-contact path. After this re-ask, route the result to
`PROCEED-STAGED`, a block outcome, or `NO-OWNER-PACKET`. Do not add a new control, registry, owner
role, or export request because the first reply was incomplete.
