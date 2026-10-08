# rev0308 source-chain field-lane firebreak refactor

## Problem

A returned CSV and activation `SOURCE_PACKET` now have explicit lane guards, but
the local source chain between and after those points was broader than it needed
to be. Packet manifests, contact status records, reask logs, workbench seeds,
reviews, decisions, tickets, receipts, cards, readouts, actions, rechecks, and
context receipts can each become the next source for a later command.

If one of those source artifacts is pulled from checker or release scratch, the
operator may be following a synthetic chain while believing they are still on the
live field lane.

## Change

`field_scratch_lane_error()` centralizes the local source-chain rule:
archive-local `FT-0181` source artifacts must resolve under
`scratch/field/ft0181/`. It blocks:

```text
scratch/checks/
scratch/releases/
scratch/<legacy-non-field-lane>/
*/check-*
*/smoke-*
*/test-*
*/fixture-*
```

The guard now covers direct CLI sources and embedded provenance references for
packet manifests, send/contact/reask/route state, intake references, workbench
seed and review materials, first-packet decisions, post-decision tickets,
activation receipts, live-window cards, terminal readouts, post-readout actions,
rechecks, context receipts, and scratch-returned CSV references.

External returned CSVs and external activation source packets still use their
separate external-or-field-lane guards because those are the human handoff points
where real material may arrive from outside the archive.

## Regression coverage

Positive checker fixtures were moved to field-lane validation directories when
they represent a source chain. Checker scratch remains available for negative
fixtures. The post-decision change-ticket validator now copies a valid decision
into checker scratch and proves it is blocked before a ticket can be recorded
from that source.

## Boundary

This is a lane-provenance control. It does not contact an owner, import a real
CSV, accept `SRC2+`, authorize a real active-change window, upgrade a public
claim, mutate a service record, move lifecycle state, or close `FT-0181`.
