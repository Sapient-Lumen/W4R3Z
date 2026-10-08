# FT-0181 first-contact reminder-workflow packet

## Purpose

This is the first packet to send before trying the harder minor-facing hint-tutor lane. Rev0244
keeps the default `FT-0181` first contact on `AIEDU-SR-003` capped assignment-reminder workflow,
but trims the first ask to a **ten-minute core owner reply**. The goal is not a complete export. The
goal is to discover whether a real operational owner can provide a minimized `SRC2+` packet without
raw learner data, protected facts, technical export work, or vendor-only claims.

This surface is not a new approval layer. It is the practical, owner-facing contact sheet for one
service, one first owner path, one source system, and one short date range. After a real minimized
packet returns, use the owner packet workbench and downstream gates.

## First target

| Field | Rev0244 default |
|---|---|
| selected service | `AIEDU-SR-003` capped assignment-reminder workflow |
| first owner path | course operations lead plus course coordinator; do not require the LMS integration owner before the core reply |
| source system | owner-known LMS sandbox workflow log or staff queue summary |
| date range | one reminder cycle or two adjacent low-stakes reminder cycles |
| source truth target | `SRC2+` local owner-reviewed operational summary |
| first-reply time target | ten minutes or less for the core fields |
| evidence claim ceiling | process/action-boundary packet only; no learning, safety, workload, compliance, or scale claim |
| fallback if unavailable | `AIEDU-SR-001` advising-navigation assistant only if an advising owner can answer aggregate correction/route counts without deadline, aid, credit, or protected-route details |
| do not use as fallback by default | `AIEDU-SR-004` hint tutor, unless a teacher owner already has an aggregate no-trace packet ready |

## Why this target goes first

The first import should maximize the odds of a real owner-reviewed packet while minimizing learner
privacy, protected-route, small-cell, and construct-overclaim risk. The reminder workflow is not the
most pedagogically interesting service, but it is the best first test of whether the cube can
receive real evidence without bloating the request or laundering claims.

Use it first because:

- the AI output is a draft reminder or staff queue note, not a grade, hint, answer, or protected
  support artifact;
- the main evidence can be aggregate workflow counts, review minutes, false-reminder corrections,
  rollback events, and incident class labels;
- course owners can usually answer the first version from staff workflow memory or logs without a
  technical export owner;
- the action ceiling is testable: no automatic send, no durable write, no penalty, and human review
  before any learner message;
- a block is still informative: if even this lane requires a full export, the cube should stop and
  trim rather than escalate to harder learner-facing evidence.

## Copy/paste first contact

Use the exact outbound body and inbound table in
[`ft0181-eight-row-owner-reply-sheet.md`](ft0181-eight-row-owner-reply-sheet.md). Do not send the
long archive explanation first. The first contact should be a short email plus either the eight-row table or the fillable CSV template at `templates/ft0181-eight-row-owner-reply-template.csv`.

The sheet asks for exactly:

1. service, owner/contact path, source system or local record set, and date range;
2. aggregate eligible, draft-reminder, human-sent, discarded/corrected, fallback/manual-route, and
   incident counts above local privacy thresholds;
3. draft-only/no-send/no-write/no-penalty/no-protected-inference action boundary;
4. human fallback, rollback owner, incident class labels if any, and one stop condition;
5. workload signal or explicit unknown;
6. training/use-guidance note or explicit unknown;
7. public claim ceiling;
8. redaction assertion and owner attestation.

A maintainer may add only the recipient name and local context. Do not add downstream gates,
technical export requests, or extra evidence families to the first message.

## Fillable CSV option

Use `templates/ft0181-eight-row-owner-reply-template.csv` when an owner is likely to complete a small form faster than editing an email. The template is intentionally blank in `owner_response`; do not pre-fill invented values, add hidden validation tabs, or request an attached export. A filled CSV is still only an intake artifact. It must be triaged before any workbench row is promoted.

## Optional follow-up only if the core reply is viable

Do not ask for these before the core reply. Use them only to clarify a real minimized packet that is
already viable.

| Follow-up | Ask only when |
|---|---|
| field dictionary | a count or status label is ambiguous |
| technical owner confirmation | source meaning cannot be resolved by the course owner |
| workload breakdown | the first reply says workload changed but method is unclear |
| incident reconstruction | the owner names an incident class and a safe abstract narrative is needed |
| public wording review | the owner gives language that might overclaim |

## Immediate triage

If the reply is the CSV template, run `python3 tools/receipt_owner_reply_csv.py returned-owner-reply.csv --output scratch/field/ft0181/owner-reply-receipts/returned-owner-reply.receipt.json`, then `python3 tools/triage_owner_reply_csv.py returned-owner-reply.csv --json` before any workbench copy/paste. The receipt is only a content-minimized source fingerprint; the triage outcome and `next_action` are the intake landing decision, not evidence: workbench for `PROCEED-STAGED`, the re-ask template for `RE-ASK-ONCE`, and the outcome-note template for block/no-packet results.


| Owner response | Archive action |
|---|---|
| Can answer the eight-row sheet or CSV from aggregate workflow records | Triage the returned sheet, then route surviving rows to `ft0181-owner-packet-workbench.md`. |
| Can answer only after a full LMS export or vendor telemetry dump | Record `BLOCK-OVERBROAD`; do not widen. |
| Needs learner names, raw messages, gradebook rows, protected facts, or small cells | Record `BLOCK-PROTECTED` or `BLOCK-OVERBROAD`; keep facts local. |
| Cannot confirm draft-only/no-write/no-penalty boundary | Record `BLOCK-AUTHORITY`; do not start live-window work. |
| Can only provide testimonial or vendor-written benefit claim | Record `BLOCK-EVIDENCE`. |
| Does not respond after one follow-up | Record `NO-OWNER-PACKET`; do not add a new control. |

## Outreach clock

Use a short clock so the cube stops waiting passively:

- send one first contact;
- allow three business days for an initial answer;
- send one field-trim follow-up if the owner says the ask is too broad;
- after seven business days without a viable owner path, record `NO-OWNER-PACKET` and either name a
  real next owner or stop the sprint;
- do not convert silence into a new schema, registry, export meeting, or closure workaround.

## Closure boundary

This contact packet does **not** close `FT-0181`, does not import real evidence, and does not prove
that the reminder workflow improves learning, safety, access, workload, compliance, or service
effectiveness. It only makes the first real owner ask concrete enough to send and small enough to be
answered.


## Rev0251 workbench seed note

If the owner returns the fillable CSV, first run `make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply` from the same scratch root that contains the active contact-status clock, then execute only its emitted `make owner-reply-intake ... SOURCE_CONTACT_STATUS=...` command before any workbench copy/paste. If the bundle returns `PROCEED-STAGED`, rerun `make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake` and execute only the emitted workbench-seed command. The bundle and seed keep receipt, triage, hashes, source-contact-status trace, and the routed local artifact together in scratch or an external local path; they do not copy owner answers into metadata, accept evidence, close `FT-0181`, or support public claims.
