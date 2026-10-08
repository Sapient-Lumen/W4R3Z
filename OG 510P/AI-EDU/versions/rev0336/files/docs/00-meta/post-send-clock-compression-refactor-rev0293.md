# rev0293 post-send clock compression refactor

## Problem found

`rev0292` made the safe pre-send work executable, but a second seam remained.
After a real human send/adaptation, the maintainer still had to record a send
log, rerun the router, then record the contact status from the send log. That
sequence was safe but brittle. Missing one step could leave the cube with a real
external action and no bounded local contact clock.

## Refactor made

`tools/record_ft0181_owner_after_human_send.py` compresses only the post-human-send
bookkeeping:

1. verify the scratch packet manifest;
2. require `CONFIRM=human-sent-bounded-owner-request`;
3. record `send-log.json` using the existing send-log builder;
4. record `SENT_AWAITING_REPLY` using the existing contact-status builder, with
   `SOURCE_ARTIFACT=` pointing to that `send-log.json`;
5. write `AFTER-HUMAN-SEND-SESSION.md` and `after-human-send-session.json` as
   local non-evidence session records.

The Makefile exposes this as:

```bash
make owner-after-human-send \
  PACKET=scratch/owner-request-packets/aiedu-sr-003-first-contact/packet-manifest.json \
  CONFIRM=human-sent-bounded-owner-request
```

The router now emits the dated version of that command after packet prep. The
helper defaults the first response clock to seven days after `SENT_DATE` unless
the router emitted a bounded `RESPONSE_DUE_DATE`.

## Explicit non-automation boundary

The helper must not automate or infer:

- who the accountable owner is;
- whether the route was valid;
- whether delivery occurred;
- whether an owner saw or accepted the request;
- whether a returned packet is real;
- whether evidence is accepted;
- whether a public claim, service record, lifecycle state, custody state, or
  closure state may change.

It only records local bookkeeping after a human claims the bounded send/adaptation
happened.

## Lower-level repair paths

`make owner-send-log` and `make owner-contact-status` remain valid lower-level
repair paths. They are not the preferred clean path after packet prep. They exist
so a previously written send log can still be validated and converted into a
sourced contact clock without editing manifests by hand.

## Refactor result

The field rail is now shorter at both sides of the human-send boundary:

- before send: `owner-field-work` prepares the packet and reroutes;
- after real send: router-emitted `owner-after-human-send` records the local
  send log and contact clock together;
- after reply: `owner-field-next CSV=...` remains the only intake entry.

This reduces waste while preserving the cube's source-truth firebreak.
