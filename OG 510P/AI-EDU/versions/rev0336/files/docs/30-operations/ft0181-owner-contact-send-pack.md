# FT-0181 owner contact send pack

This pack exists because the riskiest unfinished work is not another local control. It is crossing
one human boundary without weakening source truth. The archive can prepare the `AIEDU-SR-003` owner
request packet, but only an operator can identify an accountable owner, send the request, or record
that no safe route exists.

## Current router state

In rev0336, the preferred entry remains the composed field handoff bundle:

```bash
make field-handoff-bundle OVERWRITE=1
```

Then open `scratch/field-handoff/rev0336/ft0181-owner-request/SEND-NOW-BRIEF.md`. The safe local router remains the field-lane entry point after the human send or route block. It prepared the local first-contact
packet under `scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact/` and then
stopped at the correct human boundary.

The next action emitted by the router is:

```bash
make owner-after-human-send \
  PACKET=scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact/packet-manifest.json \
  SENT_DATE=2026-06-18 \
  RESPONSE_DUE_DATE=2026-06-25 \
  CONFIRM=human-sent-bounded-owner-request \
  OUT=scratch/field/ft0181/owner-after-human-send/aiedu-sr-003-sent-2026-06-18
```

Run that command only after a human actually sends the bounded request. If no accountable owner route
exists, do not fake a send log. Record the route block instead:

```bash
make owner-route-block \
  PACKET=scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact/packet-manifest.json \
  CONFIRM=human-confirmed-owner-route-block-no-send \
  OUT=scratch/field/ft0181/owner-route-block/aiedu-sr-003-no-owner-route-2026-06-18
```

## Send checklist

Do these in order:

1. Regenerate the packet with `make owner-field-work` if the scratch path is absent.
2. Identify the accountable service owner or record that no safe route exists.
3. Send only the bounded request and the eight-row owner reply template.
4. Do not attach learner names, raw work, gradebook rows, protected support facts, screenshots,
   recordings, security payloads, vendor dashboard exports, or staff surveillance records.
5. After the human send, record only the send log with the router-emitted command above.
6. Re-run `make owner-field-next`; execute only the next emitted command.

## Minimum message contents

Use [`../../templates/ft0181-owner-first-contact-message.md`](../../templates/ft0181-owner-first-contact-message.md)
for the sendable text. The message asks for a small owner-attested packet, not for a dashboard dump
or a general data export.

The owner should be able to answer in eight aggregate rows:

- service identifier and owner role;
- date range covered;
- whether the record set is owner-reviewed;
- aggregate counts needed for the requested claim family;
- incident or access issue counts, with small cells suppressed;
- public claim ceiling;
- fields the owner refuses to provide and why;
- owner attestation.

## Claim boundary

This send pack is not evidence. A prepared packet, sent email, route block, send log, reminder, or
no-owner-packet status does not prove learning, safety, access, workload, compliance, effectiveness,
service authority, custody, public support, or `FT-0181` closure. Only an accepted real `SRC2+`
owner packet can move the rail.

## rev0336 teacher/tutor lane note

The teacher/tutor lane now blocks generic post-result repetition: non-retire local result decisions require a follow-through seed and a fresh packet. This does not change `FT-0181`, which still requires real owner contact or a documented route block.
