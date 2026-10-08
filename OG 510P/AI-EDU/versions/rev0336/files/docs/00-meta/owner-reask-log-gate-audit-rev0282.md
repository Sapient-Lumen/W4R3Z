# Owner reask-log gate audit rev0282

## Risk named

A bounded clarification can be necessary, but the archive must not confuse
"clarification is needed" with "the clarification was sent." Before rev0282,
that distinction was too thin. A due first contact clock, a `RE-ASK-ONCE` intake
bundle, or a `REASK-OWNER` workbench review could route directly to a
`REASK_AWAITING_REPLY` contact-status artifact.

That made the second clock easier to manufacture than the first one. The first
ask had a send-log firebreak. The re-ask did not.

## Repair

Rev0282 adds `owner-reask-log` as a scratch-local non-evidence artifact. It can be
sourced only from one of the legitimate clarification triggers:

- an expired `SENT_AWAITING_REPLY` contact status with attempt count `1`,
- a local intake bundle with `triage_outcome: RE-ASK-ONCE`, or
- a workbench review with `decision: REASK-OWNER`.

The reask log requires `CONFIRM=human-sent-bounded-reask`, a sent date, a response
due date no more than three days later, a route class, and class-level notes only.
It stores no recipient, address, owner answer, raw row, protected fact, screenshot,
credential, or public-claim language.

## Executable behavior

The router now emits `make owner-reask-log ...` when one bounded clarification is
needed. Only after a valid `scratch/owner-reask-logs/**/reask-log.json` exists does
it emit `make owner-contact-status STATUS=reask-awaiting-reply ...` with the
reask log as `SOURCE_ARTIFACT`.

The contact-status recorder now rejects direct `REASK_AWAITING_REPLY` sources
from prior first clocks, intake bundles, or workbench reviews. The second clock
must be sourced from the reask-log firebreak.

## Boundary

A reask log is not evidence, not delivery proof, not owner response proof, not
SRC2+, not custody, not acceptance, not public-summary support, and not closure.
It only prevents a clarification need from pretending to be a clarification sent.

## Validation coverage

- `tools/check_ft0181_owner_reask_log.py` covers valid reask logs, source blocks,
  output blocks, argument blocks, clock bounds, overwrite cleanup, and the
  reask-log-to-contact-clock firebreak.
- `tools/check_ft0181_owner_contact_status.py` verifies that
  `REASK_AWAITING_REPLY` contact status is sourced from a valid reask log.
- `tools/check_ft0181_field_next_action.py` verifies router sequencing from due
  first clock, `RE-ASK-ONCE` intake, and `REASK-OWNER` workbench review to
  reask-log first, then contact status.
- `tools/check_owner_workbench_review.py` verifies the workbench reask path uses
  the new reask-log seam.
