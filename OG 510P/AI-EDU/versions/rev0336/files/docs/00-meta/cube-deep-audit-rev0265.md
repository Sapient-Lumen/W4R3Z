# Cube deep audit rev0265

Date: 2026-06-13
Revision: rev0265
Status: packet-created-clock router repair; `FT-0181` remains live and unclosed.

## What was most at risk

The riskiest remaining failure was a small clock error in the first-contact lane.
Rev0264 required packet-manifest integrity before the router could emit a sent
clock, but packet ranking still treated `requested_return_date` as the packet
clock. That could make an older prepared packet with a farther response date
outrank a newer regenerated packet with a shorter, more realistic return window.

That is not evidence leakage, but it is operationally dangerous: the operator
could send or clock the wrong local packet after regenerating the request, then
spend another cycle waiting on stale scratch state. The field path would look
busy while the real blocker stayed unchanged: no owner packet has returned.

## Concrete forward motion

Prepared owner-request packet manifests now include `created_at_utc` and
`packet_version`. The field router ranks packet candidates by `created_at_utc`
first, with `requested_return_date` only as a fallback for older local scratch
artifacts. Packet integrity validation now also rejects a selected packet
manifest that lacks a parseable UTC creation timestamp.

The practical effect is narrow and useful: when a packet is regenerated, the
router selects the newly generated packet even if an older packet asked for a
later return date. The emitted `STATUS=sent-awaiting-reply` clock now follows the
actual latest prepared packet rather than the farthest due date in scratch.

## Audit/refactor result

`tools/prepare_ft0181_owner_request_packet.py` now stamps packet manifests with a
UTC creation clock. `tools/decide_ft0181_field_next_action.py` now uses that
clock in `artifact_sort_key()` for packet artifacts. `tools/ft0181_field_guards.py`
centralizes the new packet timestamp integrity check with the existing packet
non-evidence/closure/source-truth boundary.

`tools/check_ft0181_field_next_action.py` now includes a regression fixture with
two prepared packets: an older long-return packet and a newer short-return
packet. The router must select the newer packet by `created_at_utc` and emit a
sent clock based on that packet's requested return date. `tools/check_ft0181_owner_request_packet.py`
checks that packet manifests include `packet_version: rev0265` and a UTC
`created_at_utc` timestamp.

This is deliberately not a new policy surface. It is a state-integrity repair for
the one active field path.

## Still missing

`FT-0181` still lacks the only thing that would materially advance the pilot: a
real `SRC2+` owner-reviewed packet, a returned eight-row owner CSV, accepted
workbench content, a live-window readout, and a closure signoff. No rev0265
artifact changes that.

The next external move remains the same: run the router, send or adapt the
prepared owner packet outside the archive, record the sent clock through the
router-emitted command, and then either route a plausible returned owner CSV
through intake or record `NO_OWNER_PACKET` after the bounded follow-up path.

## Anti-waste note

Do not add another registry, broad request, evidence abstraction, or branch-tail
explanation to compensate for a missing owner packet. The cube's useful work now
is field execution and bounded local-state hygiene. A timestamped packet
manifest is enough for this failure mode; more doctrine would be waste.
