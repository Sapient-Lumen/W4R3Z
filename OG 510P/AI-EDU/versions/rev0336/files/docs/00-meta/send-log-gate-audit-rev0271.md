# Send-log gate audit rev0271

## Finding

Rev0270 made `SOURCE_ARTIFACT` real enough to block phantom or wrong-class
status paths, but the first `SENT_AWAITING_REPLY` state could still be sourced
directly from a prepared packet manifest. That left a small but important false
progress seam: a packet that only existed locally as `PREPARED_NOT_SENT` could be
used as the source artifact for a sent contact clock after an operator copied a
router command.

This is not a proof problem the archive can fully solve. The archive cannot prove
email delivery or owner receipt without external systems. It can, however, require
one separate local operator artifact between packet prep and contact-status
recording. That artifact should say less, not more: no recipient details, no owner
answers, no learner data, no screenshots, no raw exports, and no public claims.

## Change

Rev0271 adds a minimal send-log gate.

```bash
make owner-send-log \
  PACKET=scratch/owner-request-packets/.../packet-manifest.json \
  SENT_DATE=2026-06-13 \
  RESPONSE_DUE_DATE=2026-06-20 \
  CONFIRM=human-sent-bounded-owner-request \
  OUT=scratch/owner-send-logs/aiedu-sr-003-sent-2026-06-13
```

The field router now routes a prepared packet to `make owner-send-log` first. Only
after `send-log.json` exists does it route to `make owner-contact-status
STATUS=sent-awaiting-reply ... SOURCE_ARTIFACT=.../send-log.json`.

`tools/record_ft0181_owner_contact_status.py` now rejects a prepared
`packet-manifest.json` as the direct source for `sent-awaiting-reply`. Re-ask and
no-owner-packet routing remain sourced from prior contact status or a
`RE-ASK-ONCE` intake bundle.

## What the send log may contain

| Field class | Allowed | Blocked |
|---|---|---|
| Packet source | Scratch `packet-manifest.json` that still passes packet integrity. | Edited packet claiming sent, evidence, closure, or another followthrough. |
| Send fact | Date, due date, route class, channel class, adapted/not adapted flag. | Recipient names, addresses, mailbox content, owner answers, or copied message headers. |
| Data | Service label, aggregate source/date boundary, local operator token. | Learner identifiers, protected facts, screenshots, raw LMS exports, credentials, prompts, or small cells. |
| Effect | May source one local `SENT_AWAITING_REPLY` status. | Evidence upgrade, live-window authorization, closure, or public-claim support. |

## Refactor effect

This is a tool refactor, not a new doctrine branch. It moves the next concrete
execution step from a prose instruction to a checked command, then updates the
router and contact-status recorder so the command sequence is enforceable:

1. prepare packet;
2. human sends or adapts outside the archive;
3. record minimal send log;
4. rerun router;
5. record sent contact clock from `send-log.json`;
6. await a real CSV, one bounded re-ask, or a bounded no-owner-packet outcome.

## Remaining gap

The send log is still a local assertion. It does not prove delivery, receipt,
owner review, source truth, `SRC2+` evidence, or service performance. The only
thing it proves inside this archive is that a maintainer did not advance the
contact clock from a prepared-only packet manifest.

## Immediate next action

In a clean extract:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003
make owner-request-packet OUT=scratch/owner-request-packets/aiedu-sr-003-first-contact
# human sends/adapts outside archive
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003-after-send OVERWRITE=1
# execute only the emitted make owner-send-log command
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003-after-send-log OVERWRITE=1
# execute only the emitted make owner-contact-status command
```
