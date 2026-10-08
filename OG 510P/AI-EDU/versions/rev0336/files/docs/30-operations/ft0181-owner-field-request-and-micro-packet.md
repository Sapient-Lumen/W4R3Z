# FT-0181 owner field request and micro-packet

## Purpose

This is the smallest field-facing request that can move `FT-0181` toward a real
`SRC2+` owner-reviewed pilot packet without asking a service owner for a broad
export, a new control family, or raw learner data.

Use it after the owner import action kit and before the owner packet workbench.
It translates the archive's internal intake language into a copy/pasteable ask
for one real owner, one service, one source path, one date range, and one
aggregate or minimized packet.

This surface does not close `FT-0181`. It only reduces friction for obtaining a
real source packet that can later be staged, normalized, accepted, rendered, and
reviewed through the existing gates.

## Copy/paste owner request

For the current first-contact lane, prefer the shorter exact sheet in
[`ft0181-eight-row-owner-reply-sheet.md`](ft0181-eight-row-owner-reply-sheet.md). This older
field request remains the plain-language fallback, but the eight-row sheet is the active outbound
form for `AIEDU-SR-003`.


Subject: Minimal owner packet request for one AI-education pilot service

Hello,

We are trying to test one AI-enabled education service record without collecting
raw learner data or making any effectiveness claim.

Could you send the smallest owner-reviewed packet that answers the fields below
for one service, one cohort or class window, one source system, and one date
range? Please aggregate or redact before sending. Do not include names, IDs, raw
chat logs, raw prompts, disability/accommodation details, discipline records,
clinical or wellbeing disclosures, API keys, credentials, or unrestricted
vendor telemetry.

The packet can be a short table, a filled form, a redacted export summary, or a
brief owner memo. The only required assertion is that the packet is from a real
operational owner path and has been minimized before transfer.

We will use it only to decide whether the archive can stage and review a real
pilot packet. We will not claim learning, safety, access, workload, compliance,
or service effectiveness from this packet alone.

## Micro-packet fields

Rev0249 keeps the first reply to eight core rows, preserves the fillable CSV twin, binds them to the eight-row owner reply sheet, and adds `tools/receipt_owner_reply_csv.py` plus `tools/triage_owner_reply_csv.py` for returned CSVs. Anything beyond these rows is optional follow-up
after a viable owner packet exists.

| Field | Minimal acceptable answer | Why it survives |
|---|---|---|
| Service and owner | One deployed or piloted service name plus accountable owner role and contact path. | Identifies the service and action owner. |
| Source and date | One source system or owner-maintained record set plus one date range. | Establishes custody and window boundaries. |
| Cohort aggregate | Eligible, exposed/drafted, human-sent if any, discarded/corrected, fallback/manual-route, and incident counts above local privacy thresholds. | Supports review without raw learner records. |
| AI action boundary | Draft, routing, hint, feedback, advising, summarization, or other bounded action plus what it cannot do. | Maps to action-authority ceiling. |
| Fallback, rollback, incident, and stop | Human fallback, rollback owner, incident class count if known, and one stop condition. | Creates an actionable next decision. |
| Workload and guidance | One burden signal and training/use-guidance note if known. | Separates adoption/workflow effects from unsupported effectiveness. |
| Public claim ceiling | What the owner would be comfortable saying publicly now. | Prevents claim laundering. |
| Redaction and attestation | Owner states raw/protected data were removed or kept local and whether the packet is real operational material. | Establishes source truth class and privacy boundary. |

The first reply should take about ten minutes for a real owner who knows the workflow. Do not require
a technical export owner, merged data lake, or full analytics dashboard before this core reply.

## Do not request

Do not request or accept these in the first packet unless a separate approved
custody route and protected review path are already in place.

- Names, emails, usernames, IDs, or direct identifiers.
- Raw learner prompts, raw chat logs, raw essays, raw messages, or raw advising
  transcripts.
- Disability, accommodation, protected-support, health, wellbeing, discipline,
  misconduct, or safeguarding details.
- Unrestricted gradebook exports, raw scores, or individual assessment records.
- Vendor telemetry that is not necessary to answer the micro-packet fields.
- API keys, credentials, system prompts, secrets, or security payloads.
- Free-text exports that cannot be reliably minimized before transfer.

## Field survival test

Every requested field must change at least one of these decisions. If it does
not, drop it before contacting the owner.

- Authority: who may start, stop, narrow, or continue the service?
- Evidence: what source truth class and evidence grade can be assigned?
- Construct: what learning, support, or administrative task is actually in view?
- Public language: what can be said without overclaiming?
- Lifecycle: should the service continue, rerun, pause, rollback, or archive?
- Security/privacy: does the packet need a protected route or rejection?
- Access/burden: did the service change who could use support or how costly it
  was to use it?

## Initial triage outcomes

Use one of these labels immediately after receiving a packet.

| Outcome | Use when | Next surface |
|---|---|---|
| `PROCEED-STAGED` | Packet is real, minimized, owner-reviewed, and enough for staging. | `templates/ft0181-proceed-staged-note-template.md`, then `ft0181-owner-packet-workbench.md` |
| `FALLBACK-SERVICE` | The owner can identify the service but not enough data yet. | `ft0181-owner-import-action-kit.md` |
| `BLOCK-OVERBROAD` | Packet includes raw or excessive learner data. | `minimum-real-data-request-packet.md` |
| `BLOCK-PROTECTED` | Packet includes protected, accommodation, wellbeing, discipline, or safeguarding material. | `public-summary-redaction-profiles.md` and protected-route governance. |
| `BLOCK-SECURITY` | Packet includes credentials, secrets, prompt-injection payloads, or dangerous system details. | `ai-service-security-red-team-and-agentic-tool-boundaries.md` |
| `BLOCK-EVIDENCE` | Packet is synthetic, mock, owner-unreviewed, or provenance-unclear. | `real-import-acceptance-tests-and-reviewer-calibration.md` |
| `NO-CHANGE-TRIM` | Packet only repeats fields that cannot change any decision. | Drop fields and re-ask once, or stop. |

## Post-receipt discipline

After the packet is received, do not add another validator just because the
packet is messy. First decide whether the current workbench, decision board,
change ticket, live-window card, readout gate, and post-readout dispatch already
cover the failure.

A new control is allowed only if the packet exposes a repeatable failure that is
not catchable by the current gates. Otherwise, the correction is to ask for less,
reject overbroad data, or route the packet to the existing protected or security
path.


## Rev0244 eight-row intake, CSV guard, and triage tool

The machine-readable ready request now has to match the eight-row human intake sheet, its CSV template at `templates/ft0181-eight-row-owner-reply-template.csv`, the local returned-CSV receipt tool `tools/receipt_owner_reply_csv.py`, and the local returned-CSV classifier `tools/triage_owner_reply_csv.py`. It should not list completed workbench, decision-board, live-window, readout, closeout, or signoff artifacts as `minimum_packet_fields`, and it should not require a technical/vendor owner before the core reply. Those artifacts and owners can matter after a real packet returns, but they are not fields to demand in the first email.

If the request cannot be sent as the eight-row sheet or CSV without explaining the archive's whole release-control chain, trim the request rather than adding another gate.


Run `tools/receipt_owner_reply_csv.py`, then `tools/triage_owner_reply_csv.py` on returned CSVs before opening the workbench. A tool outcome of `PROCEED-STAGED` only permits staging; it is not source evidence or closure.


## Rev0251 workbench seed note

If the owner returns the fillable CSV, first run `make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply` from the same scratch root that contains the active contact-status clock, then execute only its emitted `make owner-reply-intake ... SOURCE_CONTACT_STATUS=...` command before any workbench copy/paste. If the bundle returns `PROCEED-STAGED`, rerun `make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake` and execute only the emitted workbench-seed command. The bundle and seed keep receipt, triage, hashes, source-contact-status trace, and the routed local artifact together in scratch or an external local path; they do not copy owner answers into metadata, accept evidence, close `FT-0181`, or support public claims.
