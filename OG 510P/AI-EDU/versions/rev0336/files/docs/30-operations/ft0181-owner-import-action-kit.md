# FT-0181 owner import action kit

This is the practical handoff for the first real import. Use it when a maintainer has a possible
record owner and wants to move `FT-0181` without widening the request into a data grab. The exact
eight-row first-contact sheet lives in
[`ft0181-eight-row-owner-reply-sheet.md`](ft0181-eight-row-owner-reply-sheet.md), with a fillable CSV twin at `templates/ft0181-eight-row-owner-reply-template.csv`, with the older
field-facing explanation in
[`ft0181-owner-field-request-and-micro-packet.md`](ft0181-owner-field-request-and-micro-packet.md).
Arrival handling begins after receipt with `tools/receipt_owner_reply_csv.py` for a content-minimized local fingerprint, then `tools/triage_owner_reply_csv.py` for CSV replies. Rev0249 keeps the triage tool's `next_action` route: `PROCEED-STAGED` first runs `tools/stage_owner_reply_csv.py` and uses `templates/ft0181-proceed-staged-note-template.md`, then opens [`ft0181-owner-packet-workbench.md`](ft0181-owner-packet-workbench.md); `RE-ASK-ONCE` uses `templates/ft0181-owner-reask-once-message.md`, and block/no-packet outcomes use `templates/ft0181-triage-outcome-note-template.md`.

## Smoke rehearsal before contact

Before sending or adapting the owner contact, run `make owner-reply-smoke`. This uses the SRC0
fixture `fixtures/owner-reply-pipeline/ft0181-proceed-staged-smoke.csv` to prove the same triage and
staging path is runnable. Rev0249 preserves the rev0248 smoke/staging block and direct normal staging of `fixtures/` and blocks smoke notes from archive-controlled output paths. The smoke output is not owner evidence, not `SRC2+`, and not a reason to
widen the request.

## One-sentence ask

Please complete the eight-row owner reply sheet or fillable CSV for one service and one date range, using only aggregate/minimized fields that can change action authority, evidence grade, construct posture, public claim, rollback, protected-route safety, security handling, access, or burden. Keep archive-internal gates out of the first email.

## Default lane

| Slot | Default | Fallback | Reserved |
|---|---|---|---|
| service | `AIEDU-SR-003` capped assignment-reminder workflow | `AIEDU-SR-001` advising navigation assistant | `AIEDU-SR-004` middle-school hint tutor sandbox |
| reason | staff-facing, draft-only, reversible, and answerable with aggregate workflow counts | aggregate correction/route counts may be safer if reminders cannot be isolated | tests learning claims but is too privacy- and trace-sensitive for the first contact |
| packet shape | ten-minute aggregate eligible/draft/sent-after-human-review/discarded/fallback/correction/incident/review-time reply; no named roster rows | aggregate route, correction, fallback, escalation, and no-penalty counts; no deadline/credit/aid/protected facts | teacher-reviewed aggregate no-trace summary only, if already available |
| abort trigger | owner needs roster rows, gradebook screenshots, message bodies, protected facts, or full LMS/vendor export | advising packet includes protected route, aid, deadline, credit, or eligibility decision details | raw prompts, essays, transcripts, small cells, disability or family facts are needed |

Use [`ft0181-first-contact-reminder-workflow-packet.md`](ft0181-first-contact-reminder-workflow-packet.md) before any broader owner meeting.

## Packet ceiling

The request is capped before it leaves the archive.

| Dimension | Ceiling |
|---|---|
| services | one service ID |
| owners | one record/service owner pair, or one person explicitly serving both roles; do not require a technical export owner before the core reply |
| date ranges | one short date range |
| source systems | one source system or owner-maintained local record set |
| learner data | none in raw form |
| protected-route data | none in public/archive form |
| security data | class labels only; no exploit strings, keys, prompts, or tool payloads |
| public claims | no effectiveness, safety, access, or compliance claim unless source truth supports it |

## What the owner can send

The first owner packet should contain only the eight rows from
[`ft0181-eight-row-owner-reply-sheet.md`](ft0181-eight-row-owner-reply-sheet.md) or the CSV template. Do not ask the
owner to complete downstream archive gates before the first packet returns:

1. service, owner/contact path, source system or local record set, and date range;
2. aggregate eligible, draft-reminder, human-sent, discarded/corrected, fallback/manual-route, and
   incident counts above local privacy thresholds;
3. draft-only/no-send/no-write/no-penalty/no-protected-inference action boundary;
4. human fallback, rollback owner, incident class labels if any, and one stop condition;
5. workload signal or explicit unknown;
6. training/use-guidance note or explicit unknown;
7. public claim ceiling;
8. redaction assertion and owner attestation that the packet is real operational material.

Any broader local note belongs in optional follow-up after the eight-row packet or CSV is viable.

The owner should not send:

- raw learner prompts, chats, work, recordings, essays, names, IDs, screenshots, or private messages;
- diagnosis, disability, accommodation, language-access, hardship, immigration, discipline,
  counselling, family, or protected support facts;
- raw exploit strings, system prompts, credentials, API keys, tool payloads, or vendor security
  incident details;
- small subgroup cells or protected-status cuts;
- vendor-authored impact claims unless the local owner has independently reviewed the claim.

## Triage outcome router

After the CSV classifier runs, take exactly one next action.

| Outcome | Next artifact | Rule |
|---|---|---|
| `PROCEED-STAGED` | `templates/ft0181-proceed-staged-note-template.md` via `tools/stage_owner_reply_csv.py` | generate a minimized note, then copy only survivor rows into the workbench |
| `RE-ASK-ONCE` | `templates/ft0181-owner-reask-once-message.md` | one clarification only; no full export or new registry |
| block outcomes or `NO-OWNER-PACKET` | `templates/ft0181-triage-outcome-note-template.md` | record abstract outcome only; keep raw/protected/security material local |

## First 30-minute owner meeting

Use this order and stop early if the packet cannot stay small enough to send as a micro-packet.

| Minute | Question | Output |
|---|---|---|
| 0-5 | Which one service and date range can you safely discuss? | selected reminder-workflow lane, lower-risk fallback, or block |
| 5-10 | What did the AI actually have authority to do? | action ceiling and rollback route |
| 10-15 | What evidence exists without raw learner data? | aggregate metric candidates |
| 15-20 | What must stay local or protected? | exclusion list |
| 20-25 | Which fields would change a decision? | survival categories |
| 25-30 | Can you send this packet without widening it or completing downstream gates first? | send, fallback, or block decision |

## Field survival sheet

After the packet arrives, mark every received field with one outcome.

| Outcome | Keep? | Meaning |
|---|---|---|
| `SURVIVE-AUTHORITY` | yes | changes action ceiling, human handoff, rollback, or no-penalty route |
| `SURVIVE-EVIDENCE` | yes | changes evidence grade, expiry, method, or claim family |
| `SURVIVE-CONSTRUCT` | yes | changes cognitive-effort or assessed-construct posture |
| `SURVIVE-PUBLIC` | yes | changes public-summary language or forbidden claim boundary |
| `SURVIVE-PROTECTED` | yes, abstracted | changes protected-route separation without exposing protected facts |
| `SURVIVE-SECURITY` | yes, abstracted | changes security class, stop trigger, or owner action without raw payloads |
| `LOCAL-ONLY` | no archive field | needed locally but not safe or useful in public/archive records |
| `TRIM` | no | present in export but did not change a decision |
| `RE-REQUEST` | not yet | field meaning, owner, date range, or source class is unclear |

A field that cannot be mapped to one of the survival outcomes should not become a new schema field.

## Import day sequence

The import day starts with the proceed-staged note, then the owner packet workbench, not with schema mapping. A packet that cannot
fit the workbench should be blocked, trimmed, or moved to the lower-risk fallback service or blocked before any public
example changes.

| Step | Action | Gate |
|---|---|---|
| `D0` | receive owner packet outside public archive, run `tools/receipt_owner_reply_csv.py` to create a local content-minimized fingerprint, then run `tools/triage_owner_reply_csv.py` for CSV replies before workbench triage | local receipt exists without raw answer copy; `next_action` routes to proceed-staged note, one re-ask, or outcome note |
| `D0.5` | if `PROCEED-STAGED`, run `tools/stage_owner_reply_csv.py` and then complete the workbench only for surviving rows | source owner, source class, selected service, date range, and exclusions named |
| `D1` | run custody triage | raw/protected/security data absent or quarantined |
| `D2` | write or update source dictionary | field meaning and sensitivity known |
| `D3` | map only workbench-surviving fields | decision-neutral fields trimmed or marked local-only |
| `D4` | run acceptance review with two reviewers | closure-critical disagreements resolved or block retained |
| `D5` | write decision delta | changes, trims, and no-change findings named |
| `D6` | render public summary | no overclaim, no small cells, no stale evidence |
| `D7` | closeout board decision | keep `FT-0181` live or close only if all gates pass |

## Blockers that count as progress

Record a block instead of widening the request when:

- the owner can only provide a full export;
- raw learner traces are required to understand the evidence;
- protected support facts are mixed into ordinary service records;
- the service action ceiling cannot be reconstructed;
- the learning signal is only usage, satisfaction, or time saved;
- evidence would require small cells or protected subgroup cuts;
- the owner cannot distinguish vendor claims from local observations.

These blocks should update the decision-delta log and request packet. They should not trigger a new
control unless an existing gate fails to represent the problem. A first owner ask that becomes too
long should be trimmed, not promoted into another registry or release-control family.


## Rev0251 workbench seed note

If the owner returns the fillable CSV, first run `make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply` from the same scratch root that contains the active contact-status clock, then execute only its emitted `make owner-reply-intake ... SOURCE_CONTACT_STATUS=...` command before any workbench copy/paste. If the bundle returns `PROCEED-STAGED`, rerun `make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake` and execute only the emitted workbench-seed command. The bundle and seed keep receipt, triage, hashes, source-contact-status trace, and the routed local artifact together in scratch or an external local path; they do not copy owner answers into metadata, accept evidence, close `FT-0181`, or support public claims.
