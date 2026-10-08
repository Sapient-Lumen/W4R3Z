# FT-0181 owner request packet prep

See [`ft0181-owner-contact-send-pack.md`](ft0181-owner-contact-send-pack.md) for the durable current send boundary and exact post-human-send command.
## Purpose

This is the executable first-contact lane for `AIEDU-SR-003`. It prepares the
small outbound packet that should be sent or adapted before any returned owner
CSV exists: a copy-paste email, a blank eight-row CSV, a send checklist, a
send-now brief, a local field-texture memo, a no-packet note, and a
machine-readable manifest.

The generated packet is `PREPARED_NOT_SENT`. It is not evidence, does not upgrade
source truth, does not authorize live-window work, does not support any public
claim, and does not close `FT-0181`.

Rev0281 added a bounded no-send outcome after packet prep: if no real accountable
owner route exists, record a local `owner-route-block` and stop without pretending
a send happened. Rev0282 adds the matching clarification firebreak: if one
bounded re-ask is needed, record `owner-reask-log` after the human sends/adapts
it before any `REASK_AWAITING_REPLY` contact clock exists. Rev0293 adds the
post-send compression helper: after a real human first send/adaptation,
`owner-after-human-send` records both the local send log and the sourced
`SENT_AWAITING_REPLY` clock.

## Safe local field-work target

For a clean local start, use the compressed field-work target before adding more
notes or controls:

```bash
make owner-field-work OUT=scratch/field/ft0181/ft0181-field-work/aiedu-sr-003
```

This runs the router, prepares the bounded first-contact packet only when that
is the safe local route, and reruns the router so the human-send or no-route fork
is visible. It cannot record a send log, contact status, intake, acceptance,
public support, or closure. That boundary remains true: `owner-field-work` stops
before human action.

## Field-next router

The lower-level router remains available when you need only the single next
command:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/aiedu-sr-003
```

The router scans only local/scratch packet, route-block, send-log, reask-log,
contact-status, intake-bundle, workbench-seed, workbench-review,
first-packet-decision, post-decision-ticket, and live-window-card manifests. It
writes a local docket labelled `not_evidence` and `does_not_close_ft0181`. In a
clean release extract it routes to packet prep. Prepared packet manifests include
`created_at_utc`; the router uses that creation clock before the requested return
date, so a regenerated packet is not hidden by an older packet with a farther due
date.

After a returned CSV is in hand, use:

```bash
make owner-field-next \
  CSV=/path/to/returned-owner-reply.csv \
  OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
```

The CSV path must be a plausible local field input. The router blocks shipped
fixtures, examples, templates, docs, tools, schemas, and smoke-marker CSV copies
before recommending intake.

## Command

Use a local `scratch/` path or an external local path. Keep recipient names,
contact details, learner facts, and protected facts out of the archive.

```bash
make owner-request-packet \
  OUT=scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact \
  SERVICE="AIEDU-SR-003 draft reminder pilot" \
  OWNER="accountable service owner" \
  SOURCE="owner-named local service record set" \
  DATE_RANGE="owner-named reminder cycle or short date range" \
  RETURN_DATE="2026-06-20"
```

For local scratch regeneration only, add `OVERWRITE=1`. The make target passes
the flag through to the tool, and the packet tool removes stale packet files
before rebuilding the non-evidence packet directory. The route-block, after-human-send, send-log, reask-log, and contact-status tools
also clear stale local files on overwrite so an old local operator note cannot
survive next to a new status manifest.

Equivalent direct command:

```bash
python3 tools/prepare_ft0181_owner_request_packet.py \
  --output-dir scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact
```

## Generated files

| File | Use | Boundary |
|---|---|---|
| `AIEDU-SR-003-owner-request-email.txt` | Copy/paste owner request body. | No learner-level records, raw exports, screenshots, protected facts, small cells, credentials, or vendor dumps. |
| `AIEDU-SR-003-eight-row-owner-reply-template.csv` | Blank fillable owner reply sheet. | Owner fills only `owner_response`; rows and columns stay fixed. |
| `SEND-CHECKLIST.md` | Human send guard and after-reply commands. | Local execution aid only. |
| `SEND-NOW-BRIEF.md` | One-page operator aid for completing the external send/adaptation or recording a no-owner-route block. | Local execution aid only; attach only the blank CSV and do not copy this brief into release evidence. |
| `NO-OWNER-PACKET-NOTE.md` | Local fallback note if no viable owner packet returns after the response clock and one clarification. | Non-evidence; keeps `FT-0181` live and forbids widening the ask. |
| `FIELD-TEXTURE-MEMO.md` | Local owner-contact friction memo. | Non-evidence; records implementation texture without owner answers, protected facts, contact details, raw exports, or public claims. |
| `packet-manifest.json` | Machine-readable packet state and creation clock. | `not_evidence`, `PREPARED_NOT_SENT`, `NO-OWNER-PACKET-YET`, `created_at_utc` for router packet ranking, and a packet version that must match the current release revision. |

## Send-or-block rule

Do not copy the generated packet into `docs/`, `examples/`, `fixtures/`,
`schemas/`, `templates/`, or `tools/`. The utility blocks those archive-controlled
paths. The packet should remain in `scratch/` or an external local directory,
because a prepared email can contain local recipient context after adaptation.

The outbound ask is deliberately narrow. The generated `SEND-NOW-BRIEF.md` tells
the operator to copy the generated email, attach only the blank CSV, avoid broader
attachments, and rerun the router after sending so it emits a minimal
`make owner-after-human-send` command. That helper writes both the local send log
and the sourced `SENT_AWAITING_REPLY` contact clock. The generated
field-texture memo can record whether the owner route was clear, which rows were
confusing, whether the bounded ask avoided a broader export, and whether the next
ask should be narrower, but it cannot carry owner answers or evidence.

If no accountable owner route exists, do not record a send log. Record the block
locally instead:

```bash
make owner-route-block \
  PACKET=scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact/packet-manifest.json \
  CONFIRM=human-confirmed-owner-route-block-no-send \
  OUT=scratch/field/ft0181/owner-route-blocks/aiedu-sr-003-route-block-YYYY-MM-DD
```

The route-block recorder accepts only a valid scratch packet manifest and stores
only class-level route failure. It must not store recipient names, addresses,
owner answers, learner facts, protected facts, screenshots, raw exports, security
payloads, or public-claim language. The router treats the latest valid route
block as `OWNER-ROUTE-BLOCK-RECORDED-NO-SEND`: keep `FT-0181` live and wait for a
real accountable owner route or new owner context.

The outbound ask itself asks for one service, one owner role, one source
record-set/date boundary, aggregate counts above local privacy thresholds,
draft-only/no-write/no-penalty confirmation, human fallback, rollback, incident
classes if any, workload signal if known, guidance note if known, public claim
ceiling, and an owner attestation that the reply is real operational material.

## After sending the request

Do not handwrite status dates from this document. Run the field router after the
human sends or adapts the packet, then execute only the dated
`make owner-after-human-send` command it emits. The helper records a minimal
local class-level send log and the sourced `SENT_AWAITING_REPLY` contact clock
in one guarded step. It must not store recipient names, addresses, owner answers,
learner facts, screenshots, protected facts, raw exports, or public-claim
language. The first response due date is bounded to no more than seven days after
the recorded send date.

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/aiedu-sr-003-after-send
```

The helper writes `send-log.json`, then writes `contact-status.json` whose
`SOURCE_ARTIFACT=` equivalent points to that send log, not to the prepared packet
manifest. The lower-level `owner-send-log` and `owner-contact-status` commands
remain repair paths for already-written scratch state, but they are not the
preferred clean path after first send.

If the first response clock lapses, rerun the router. It emits one bounded
`make owner-reask-log ... CONFIRM=human-sent-bounded-reask` command only after
the human sends/adapts the clarification outside the archive. Rerun the router
after `reask-log.json` exists; only then should it emit
`STATUS=reask-awaiting-reply` with `SOURCE_ARTIFACT=` pointing to that reask log
and a three-day clarification clock. If the re-ask clock also lapses, rerun it
again; it emits the bounded `STATUS=no-owner-packet` command whose sent and due
dates must match the source re-ask clock with
`CONFIRM=bounded-clock-passed-no-viable-owner-packet` instead of widening the
request.

## After a reply

Do not bypass the returned-CSV source firebreak with a direct intake command as
the operator's first move. Route the returned, owner-attested CSV through the
field router and execute only the command written to `FIELD-NEXT-ACTION.md`:

```bash
make owner-field-next \
  CSV=/path/to/returned-owner-reply.csv \
  OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
```

After a local intake bundle exists, rerun the router. If and only if the bundle is
`PROCEED-STAGED`, the router emits the bounded workbench-seed command:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake
```

## No-packet rule

If no viable packet returns after the local response clock and no more than one
clarification, use only the router-emitted `make owner-contact-status
STATUS=no-owner-packet ... CONFIRM=... SOURCE_ARTIFACT=...` command to record
`NO_OWNER_PACKET`. The clarification contact clock must have been sourced from a
valid `owner-reask-log`, not directly from a prior first clock, intake bundle, or
workbench review. Do not create a new first-contact surface, new registry, or new
sprint plan to compensate for silence. The live work then stays blocked until a
real owner-reviewed packet exists or the followthrough item is explicitly retired
as not fieldable.

## Audit notes

Validators: `tools/check_ft0181_owner_request_packet.py`,
`tools/check_ft0181_owner_route_block.py`, `tools/check_ft0181_owner_send_log.py`,
`tools/check_ft0181_owner_reask_log.py`,
`tools/check_ft0181_owner_contact_status.py`, and
`tools/check_ft0181_field_next_action.py` cover router-driven status dates,
safe local packet prep, after-human-send compression, returned-CSV source/smoke blocking, the send-now brief,
packet overwrite behavior,
route-block source verification, send-log source verification, reask-log source
verification, contact-status operator confirmation, verified source-artifact
traces, bounded first-contact and re-ask clocks, no-owner source-clock matching,
stale cleanup, and the field-texture memo boundary.

Utilities: `tools/decide_ft0181_field_next_action.py`,
`tools/prepare_ft0181_owner_request_packet.py`,
`tools/record_ft0181_owner_route_block.py`,
`tools/record_ft0181_owner_after_human_send.py`,
`tools/record_ft0181_owner_send_log.py`, `tools/record_ft0181_owner_reask_log.py`,
and `tools/record_ft0181_owner_contact_status.py`.

Fast lane: `make lint-owner-reply`.

This prep lane is intended to reduce operator hesitation and prevent fake field
progress. It does not reduce the real evidence requirement.
