# Contact clock bounds audit rev0272

## Finding

Rev0271 split packet prep, send logging, and sent contact status. That removed
the prepared-packet-to-sent shortcut. The remaining false-progress seam was clock
stretching: local tools could still create a long first-contact or re-ask window
that delayed either owner intake or `NO_OWNER_PACKET` without adding evidence.

## Change

Rev0272 adds bounded clock checks to the existing field tools:

- `tools/decide_ft0181_field_next_action.py` clamps packet requested return dates
  to the bounded first-contact clock when it emits `make owner-send-log`;
- `tools/record_ft0181_owner_send_log.py` blocks first-contact response clocks
  longer than seven days;
- `tools/record_ft0181_owner_contact_status.py` requires exact attempt counts,
  blocks first-contact clocks longer than seven days, blocks re-ask/no-owner
  clocks longer than three days, and requires `NO_OWNER_PACKET` dates to match the
  source `REASK_AWAITING_REPLY` status;
- `tools/ft0181_field_guards.py` carries the shared clock constants and checks
  send-log integrity before a sent clock can be sourced.

## Why this matters

A field lane needs an end condition. Without one, the archive can appear prudent
while evading the practical outcome: either the owner returns a viable bounded
packet, one clarification is warranted, or no owner packet exists for this
attempt. The local no-owner-packet result is not failure; it is a truthful block
that prevents wider data asks and synthetic evidence.

## Boundary

The clock bounds do not prove contact, delivery, receipt, owner review, source
truth, safety, compliance, workload reduction, learning gain, or service value.
They only prevent local wait-state drift from replacing the evidence gate.

## Immediate next action

In a clean extract, run the router, prepare the packet, send or adapt externally,
record the send log through the router, and then let the router either intake a
returned CSV, emit one bounded re-ask, or record matching-clock `NO_OWNER_PACKET`.
