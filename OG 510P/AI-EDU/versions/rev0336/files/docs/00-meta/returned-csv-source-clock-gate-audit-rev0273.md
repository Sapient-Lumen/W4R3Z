# Returned CSV source-clock gate audit rev0273

## Problem found

Rev0272 hardened packet, send-log, and contact-clock state, but the returned-CSV
branch still had a false-progress seam. A local file that looked like a returned
owner CSV could be routed to `owner-reply-intake` without proving it belonged to
a bounded contact clock. The normal intake tool blocked archive fixtures and
smoke markers, but it did not require a source `contact-status.json`.

That meant a maintainer could accidentally stage a free-floating, locally
fabricated, copied, or contextless CSV. The bundle would still be non-evidence,
but the path to `PROCEED-STAGED` would look too smooth and could pull attention
away from the harder external owner step.

## Rev0273 correction

Rev0273 adds a source-clock gate:

- `make owner-reply-intake` now requires `SOURCE_CONTACT_STATUS`.
- `tools/intake_owner_reply_csv.py` requires `--source-contact-status`.
- The source must resolve under archive `scratch/` and end in
  `contact-status.json`.
- The contact status must be an active `SENT_AWAITING_REPLY` or
  `REASK_AWAITING_REPLY` clock with the expected FT-0181 non-evidence fields,
  attempt count, bounded max-days value, verified source-artifact flag, and
  no-widening confirmation.
- `tools/decide_ft0181_field_next_action.py` now blocks `CSV=...` routing when
  the selected scratch root lacks an active contact clock, or when the latest
  contact clock is malformed, terminal, or otherwise unable to source intake.
- Intake bundle manifests now preserve the `source_contact_status` reference and
  clock summary as provenance metadata only.

## Why this is not bureaucracy

This is not a new approval doctrine. It is a path dependency check in the tool
that would otherwise receive owner material. It answers one narrow question:
"Does this CSV belong to the bounded owner-contact attempt currently being
executed?"

A valid answer does not make the CSV evidence. It only allows local receipt,
triage, and routing to proceed.

## What remains unsolved

The archive still cannot prove that a human actually sent the request, that the
recipient was the right owner, or that a returned CSV is truthful. Those remain
field and custody questions. The source-clock gate only prevents a returned-file
path from skipping the bounded contact state machine.

## Refactor result

The owner-reply intake family is now linked as:

1. packet manifest;
2. send log;
3. sent or re-ask contact status;
4. returned CSV routed through `owner-field-next`;
5. intake bundle with source-contact-status trace;
6. optional workbench seed if triage is `PROCEED-STAGED`.

This reduces free-floating local artifacts and keeps the next real step focused:
either owner material comes back through the bounded path, one clarification is
sent, or `NO_OWNER_PACKET` is recorded.
