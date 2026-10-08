# FT-0181 eight-row owner reply sheet

## Purpose

This is the exact sheet to paste under the first `AIEDU-SR-003` owner contact. It replaces broad
"send whatever you have" language with eight rows that a course operations owner or course
coordinator can answer from aggregate workflow records in about ten minutes.

The Markdown table has a fillable CSV twin at [`templates/ft0181-eight-row-owner-reply-template.csv`](../../templates/ft0181-eight-row-owner-reply-template.csv). Use the CSV when the owner is more likely to reply to a form than to an email table.

The sheet is not a new approval gate. It is the smallest inbound form that can produce a real
`SRC2+` owner-reviewed packet, a block record, or `NO-OWNER-PACKET` without widening into a full LMS
export, vendor telemetry dump, learner trace collection, or new registry.


## Preferred prep command

Before sending, prepare the local first-contact packet rather than hand-copying
from multiple archive surfaces:

```bash
make owner-request-packet \
  OUT=scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact \
  SERVICE="AIEDU-SR-003 draft reminder pilot" \
  OWNER="accountable service owner"
```

The generated email, blank CSV, checklist, and manifest are `PREPARED_NOT_SENT`
local execution aids. They are not evidence and cannot close `FT-0181`. Keep
recipient contact details and local learner facts out of the archive.

## Send this body

Subject: 10-minute owner reply for one draft-reminder workflow

Hello,

Could you fill the eight rows below for one capped assignment-reminder workflow, one source system
or local staff record set, and one reminder cycle or short date range?

Please answer only from aggregate/minimized owner-held records. Do not send learner names, emails,
IDs, messages, assignment text, gradebook rows, protected-support facts, screenshots, credentials,
system prompts, raw security payloads, small cells, vendor marketing claims, or a full LMS/export
file.

A brief reply in this table is enough. It is only for internal staging review. It will not be used to
claim learning improvement, safety, access, workload reduction, compliance, scale, or effectiveness.

| Row | Owner reply |
|---|---|
| 1. Service, accountable owner role/contact path, source system or local record set, and date range |  |
| 2. Aggregate counts above local privacy thresholds: eligible, draft-reminder, human-sent if any, discarded/corrected, fallback/manual-route, and incident count if known |  |
| 3. Action boundary: confirm draft-only, no automatic send, no durable write, no penalty, and no protected-status inference |  |
| 4. Human fallback route, rollback owner, incident class labels if any, and one stop condition |  |
| 5. Workload signal, if known, with method note; otherwise say unknown |  |
| 6. Training or use-guidance note, if known, naming who owned guidance; otherwise say unknown |  |
| 7. Public claim ceiling: what could safely be said now without claiming learning, safety, access, workload, compliance, scale, or effectiveness |  |
| 8. Redaction assertion and owner attestation that this is real operational material, not a mock, rehearsal, vendor-only claim, or unreviewed analytics export |  |

## Fillable template rule

If using the CSV, leave `owner_response` blank before sending and keep the eight `row_id` values exactly as shipped. Do not add columns for learner identifiers, gradebook rows, protected support facts, raw messages, screenshots, raw telemetry, vendor dashboards, or downstream archive gates. If the owner wants to attach a broader export instead of filling the CSV, classify the result as `BLOCK-OVERBROAD` rather than expanding the template.

## Executable CSV triage

If the owner returns the CSV, first create a local content-minimized receipt/fingerprint, then run triage before opening the workbench:

```bash
python3 tools/receipt_owner_reply_csv.py returned-owner-reply.csv --output scratch/field/ft0181/owner-reply-receipts/returned-owner-reply.receipt.json
python3 tools/triage_owner_reply_csv.py returned-owner-reply.csv --json
```

The receipt tool records SHA-256, row presence, triage outcome, and next action without copying raw owner answers. It refuses smoke fixtures and refuses output into archive-controlled directories.

If the outcome is `PROCEED-STAGED`, generate the small staging note before opening the workbench:

```bash
python3 tools/stage_owner_reply_csv.py returned-owner-reply.csv --output local-proceed-staged-note.md
```

The triage tool is conservative. It treats a blank template as `NO-OWNER-PACKET`, routes one or two missing or malformed rows to `RE-ASK-ONCE`, blocks protected, overbroad, security, authority, and unsupported-claim material, and stages only a minimized eight-row reply. Rev0249 preserves the rev0248 firebreak and refuses synthetic smoke fixtures through the normal staging CLI; use `make owner-reply-smoke` for rehearsal rather than staging `fixtures/` directly. The tool output is an intake classification only; it is not evidence and cannot close `FT-0181`. The triage result emits `next_action` and routes `PROCEED-STAGED` to a proceed-staged note before the workbench, while `RE-ASK-ONCE` still lands in the one re-ask message and block/no-packet outcomes land in the triage outcome note.

## Intake result after reply

Classify the first reply before opening any downstream gate. A returned CSV or pasted table should be triaged first, preferably with `tools/triage_owner_reply_csv.py`, then copied selectively into the workbench only if it passes local-only checks.

| Result | Use when | Next step |
|---|---|---|
| `PROCEED-STAGED` | all eight rows are answered or explicitly marked unknown without forbidden data | run `tools/stage_owner_reply_csv.py` and use `templates/ft0181-proceed-staged-note-template.md`, then copy only minimized survivor rows into the workbench |
| `RE-ASK-ONCE` | one or two row meanings are ambiguous but the packet is still minimized | use `templates/ft0181-owner-reask-once-message.md`, then stage or block |
| `BLOCK-OVERBROAD` | owner needs a full export, unrestricted vendor dump, screenshots, raw messages, or broad telemetry | record an abstract note with `templates/ft0181-triage-outcome-note-template.md` and do not widen |
| `BLOCK-PROTECTED` | answer requires protected support facts, small cells, accommodation/wellbeing/discipline facts, or protected-route cuts | keep facts local and record only an abstract note |
| `BLOCK-AUTHORITY` | draft-only/no-write/no-penalty/no-protected-inference or local rollback boundary cannot be confirmed | record authority block; do not start live-window work |
| `BLOCK-SECURITY` | reply includes credentials, secrets, raw security payloads, exploit strings, system prompts, or tool payloads | quarantine locally and record only abstract class/owner action if safe |
| `BLOCK-EVIDENCE` | reply is synthetic, mock, vendor-only, testimonial, owner-unreviewed, or makes unsupported public claims | record evidence block and keep `FT-0181` live |
| `NO-OWNER-PACKET` | no viable owner reply after one follow-up and seven business days | record the no-packet outcome note; do not add a new control |

## Outcome-router rule

The triage result controls the next artifact. Do not open a broader gate because a result feels
important. `PROCEED-STAGED` goes to the proceed-staged note before the workbench; `RE-ASK-ONCE` goes to the one re-ask message; all
block outcomes and `NO-OWNER-PACKET` go to the triage outcome note. If the tool output and a human
preference disagree, use the safer path: block, re-ask once, or keep local.

## What to do with extra material

If the owner sends more than the eight rows, triage it before copying anything into the archive.

| Extra material | Treatment |
|---|---|
| raw learner identifiers, messages, submissions, assignment text, screenshots, gradebook rows, protected facts, or small cells | quarantine or delete per local process; do not import |
| extra aggregate fields that do not change authority, evidence, construct, public language, protected routing, security, access, burden, rollback, or stop decisions | mark `TRIM` |
| ambiguous but decision-relevant row meaning | ask once for a field meaning or method note |
| safe local narrative that clarifies a stop trigger or rollback event | abstract to class label and owner action only |
| vendor claim not independently owner-attested | mark `BLOCK-EVIDENCE` or `LOCAL-ONLY` |

## Boundary

A completed real eight-row owner reply can start a local receipt, then the proceed-staged note, and then the owner packet workbench. A synthetic smoke fixture can only test plumbing through `make owner-reply-smoke`. Neither path closes `FT-0181`, and the smoke path does
not upgrade synthetic examples into real evidence, and does not prove that a service improves
learning, safety, access, workload, compliance, scale, or effectiveness.


## After a CSV returns

Use the bounded local intake bundle before opening the workbench:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
# then execute the emitted make owner-reply-intake ... SOURCE_CONTACT_STATUS=... command
```

The bundle creates a receipt, triage JSON, source-contact-status trace, and one routed local artifact. It is not evidence acceptance or closure.
