# Minimum real-data request packet

`FT-0181` cannot close until a real pilot record set exists. This surface defines
how to ask for that record set without inviting overcollection, protected-route
leakage, raw log dumping, or control-plane work that belongs after receipt.

The request posture is: **ask for the smallest packet that can change a
decision**. Rev0249 keeps that rule, adds a content-minimized local receipt/fingerprint before staging, routes `PROCEED-STAGED` through a proceed-staged note before workbench copy/paste, and preserves the fillable CSV template plus executable triage tool for the eight-row owner-reply intake guard. The first
external ask must be a field-facing core reply, not a demand for a technical
export, completed owner packet workbench, decision board, live-window card,
closeout minute, signoff quorum, or other downstream artifact.

The preferred executable first-contact route is now `make owner-request-packet`,
which prepares the copy-paste email, blank eight-row CSV, send checklist, and
manifest in `scratch/` or an external local path. That prepared packet is
`PREPARED_NOT_SENT`, `NO-OWNER-PACKET-YET`, and not evidence.


## Request packet states

| Code | Meaning | Archive action |
|---|---|---|
| `RDR0` | No partner or source owner identified | Keep `FT-0181` queued. |
| `RDR1` | Source owner and pilot context identified | Prepare the owner field request; do not request raw logs. |
| `RDR2` | Micro-packet request ready to send | Request one minimized owner-reviewed packet. |
| `RDR3` | Source packet received but not normalized | Stage outside public examples; run workbench and custody checks. |
| `RDR4` | Candidate record normalized from `SRC2+` packet | Run acceptance, calibration, and decision-delta review. |
| `RDR5` | Public-safe summary and schema delta prepared | Eligible for closure review only if later gates pass. |
| `RDRX` | Source cannot be safely transferred or interpreted | Quarantine, decline, fallback, or trim and re-ask once. |

## Sendable first ask

The first owner request should be the exact eight-row sheet in [`ft0181-eight-row-owner-reply-sheet.md`](ft0181-eight-row-owner-reply-sheet.md) or the fillable CSV template `templates/ft0181-eight-row-owner-reply-template.csv`. It should fit in an email, short table, filled form, or
brief owner memo. It should ask for one service, one accountable owner path, one
source system, one date range, aggregate or minimized fields only, no raw learner
data, and no technical export owner before the core reply.

| Core field | Minimal acceptable answer | Drop or block if |
|---|---|---|
| Service and owner | One service name or service-record ID plus accountable owner role/contact path. | More than one service or no accountable owner is needed. |
| Source and date | One source system or owner-maintained record set plus one date range. | A merged data lake, broad vendor dump, or technical export is required before the core reply. |
| Cohort aggregate | Eligible, exposed/drafted, human-sent if any, discarded/corrected, fallback/manual-route, and incident counts above privacy thresholds. | Named rows, small cells, protected subgroup cuts, or gradebook rows are needed. |
| AI action boundary | Educational task/support function plus bounded AI action and explicit no-send/no-write/no-penalty/no-protected-inference boundary. | The service purpose is only a marketing claim or the action boundary is unclear. |
| Fallback, incident, and stop | Human fallback, rollback owner, incident class count if known, and one stop condition. | Rollback depends on vendor action alone or incidents require raw payloads. |
| Workload and guidance | One workload signal plus training/use-guidance note if known. | A workload claim requires raw messages, staff surveillance, or protected facts. |
| Public claim ceiling | What the owner is comfortable saying publicly now. | The owner wants to claim learning, safety, access, compliance, workload reduction, or scale from this packet alone. |
| Redaction and attestation | Assertion that raw/protected data were removed or kept local and that the packet is real operational material. | The packet is a mock, rehearsal, vendor-only claim, or unreviewed analytics export. |

## Downstream gates are not first-ask fields

The owner packet workbench, first-packet decision board, post-decision change
ticket, live-window stop/rollback card, end-window readout, post-readout action
dispatch, closeout minutes, and signoff quorum are still required later when a
real packet actually moves through the archive. They must not be converted into
fields the owner must complete before the first packet can be sent.

This separation is executable. `tools/check_real_data_requests.py` fails a ready request if `minimum_packet_fields` requires downstream completion artifacts instead of a sendable micro-packet, and it also checks that the request points to an exact eight-row owner reply sheet, CSV template, local receipt tool, and local triage tool with staging, re-ask, block, and `NO-OWNER-PACKET` outcomes. `tools/triage_owner_reply_csv.py` then classifies a returned CSV before the workbench opens.

## Required owner attestations

Before transfer or normalization, the requester should get attestations that:

1. the source owner understands the requested fields and can explain local
   meanings;
2. the packet is from a real operational owner path and is `SRC2` or stronger;
3. learner identifiers, raw traces, protected facts, small cells, and security
   payloads have been removed or kept local;
4. aggregate metrics are large enough to avoid singling out learners or protected
   routes;
5. public claims will be no stronger than the weakest relevant claim-family
   evidence;
6. the packet may be used only for staging and review, not for public
   effectiveness, learning, safety, access, workload, compliance, or scale
   claims.

## Prohibited transfer material

Do not transfer:

- raw prompts, chat transcripts, essays, recordings, screenshots, names, emails,
  usernames, IDs, or private messages;
- diagnosis, disability, accommodation, language-access, hardship, immigration,
  discipline, safeguarding, counselling, family, or protected support facts;
- API keys, credentials, exploit strings, tool payloads, system prompts, or
  unsafe red-team artifacts;
- small subgroup metrics, small cells, protected-status cuts, or any row that can
  identify a learner or protected route;
- unrestricted gradebook exports, raw scores, individual assessment records,
  attendance histories, or discipline-linked reminder records;
- vendor-written effectiveness claims, marketing screenshots, testimonials, or
  unreviewed analytics not attested by a local operational owner.

## Field survival test

Every requested field must change at least one of these decisions. If it does
not, leave it out of the first ask or mark it `TRIM` after receipt.

| Decision changed | Example surviving field |
|---|---|
| Authority | Human override route, unauthorized action count, rollback owner. |
| Evidence | Source truth class, method note, expiry, weakest supported claim family. |
| Construct | Educational task, independent-effort boundary, support function. |
| Public language | Public claim ceiling, claim to remove, notice language. |
| Protected route | Abstract owner note that protected facts stayed local. |
| Security | Risk class, stop trigger, owner action, no raw payload. |
| Access or burden | Fallback, opt-out, correction, appeal, exclusion, workload, or rework aggregate. |

## Request JSON contract

Real-data request packets live in `examples/real-data-requests/`. They declare
the minimum requested fields, prohibited transfer fields, owner attestations,
aggregate metrics, decision-delta questions, redaction-before-transfer steps,
and stop conditions.

`tools/check_real_data_requests.py` verifies the shipped request examples. A
passing request packet does not close `FT-0181`; it only makes the next external
request safer, smaller, and more specific.

## Current archive bet

The best first real import is likely a small owner-reviewed packet, not a large
export. The request should get easier to send over time, not more ceremonial. If
a field does not change action authority, evidence grade, construct proof, public
summary, protected-route handling, security posture, rollback, access, burden, or
stop decision, it should probably stay out of the import.

`python3 tools/receipt_owner_reply_csv.py returned-owner-reply.csv --output scratch/field/ft0181/owner-reply-receipts/returned-owner-reply.receipt.json` is the local fingerprint step, and `python3 tools/triage_owner_reply_csv.py returned-owner-reply.csv --json` is the receipt-side classifier for CSV replies. Run both before any rows move to the workbench; the receipt must not copy raw owner answers, and the triage result controls `next_action`: workbench for `PROCEED-STAGED`, one re-ask message for `RE-ASK-ONCE`, and outcome note for block/no-packet results.

Use [`ft0181-eight-row-owner-reply-sheet.md`](ft0181-eight-row-owner-reply-sheet.md) or `templates/ft0181-eight-row-owner-reply-template.csv` as the first sendable ask, with [`ft0181-owner-field-request-and-micro-packet.md`](ft0181-owner-field-request-and-micro-packet.md) only as the explanatory fallback, then route any real packet through
[`ft0181-owner-packet-workbench.md`](ft0181-owner-packet-workbench.md),
[`ft0181-first-packet-decision-board.md`](ft0181-first-packet-decision-board.md),
[`ft0181-post-decision-change-ticket.md`](ft0181-post-decision-change-ticket.md),
[`ft0181-live-window-stop-rollback-card.md`](ft0181-live-window-stop-rollback-card.md),
[`ft0181-end-of-window-readout-disposition-gate.md`](ft0181-end-of-window-readout-disposition-gate.md),
and [`ft0181-post-readout-action-dispatch.md`](ft0181-post-readout-action-dispatch.md)
only after receipt.

## Handoff and closeout boundary

A ready request packet is still not an import. After a real packet arrives, route
it through the operator handoff, custody workbench, lifecycle decision,
evaluator-independence controls, closeout-board minutes, and decision-delta log
before changing `FT-0181` or public evidence claims.

Completing or validating this request does **not** close `FT-0181`, does not
upgrade examples into source evidence, and does not prove learning, safety,
access, workload, compliance, or service effectiveness.


## Rev0251 workbench seed note

If the owner returns the fillable CSV, first run `make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply` from the same scratch root that contains the active contact-status clock, then execute only its emitted `make owner-reply-intake ... SOURCE_CONTACT_STATUS=...` command before any workbench copy/paste. If the bundle returns `PROCEED-STAGED`, rerun `make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake` and execute only the emitted workbench-seed command. The bundle and seed keep receipt, triage, hashes, source-contact-status trace, and the routed local artifact together in scratch or an external local path; they do not copy owner answers into metadata, accept evidence, close `FT-0181`, or support public claims.
