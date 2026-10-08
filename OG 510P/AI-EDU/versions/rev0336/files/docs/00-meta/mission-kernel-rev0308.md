# rev0308 mission kernel

`rev0308` keeps the cube pointed at the same scarce event: real owner-reviewed
`FT-0181` evidence, returned through a path that cannot confuse local validator
byproducts with field source truth. The archive still has no accepted owner
packet, no accepted `SRC2+` evidence, no real live-window result, no public-claim
upgrade, and no closure.

## Heart of the work

The riskiest unfinished work is no longer a missing doctrine statement. It is the
source chain that would carry a real returned owner packet from contact status,
intake, seed, review, decision, ticket, activation, live-window, readout,
post-readout action, recheck, and context receipt. If any local artifact in that
chain can be sourced directly from checker or release scratch, a future operator
can waste effort on synthetic material or create false confidence near the point
of activation.

The mission behavior is simple: once an artifact becomes part of the local
`FT-0181` source chain, it must live under the deliberate live field lane:

```text
scratch/field/ft0181/
```

Checker, release, legacy, smoke, test, and fixture scratch can test the rail, but
they cannot source later field actions.

## rev0308 correction

`rev0306` blocked non-field returned CSV intake, and `rev0307` blocked non-field
activation `SOURCE_PACKET` paths. `rev0308` applies the same field-lane boundary
to the broader local source chain: packet manifests, send logs, contact status,
route blocks, reask logs, intake references, workbench seeds, review briefs,
reviews, first-packet decisions, post-decision tickets, activation receipts,
live-window cards, readouts, post-readout actions, rechecks, and context receipts.

The change is implemented as source-path guard behavior, not a new schema family
or a new registry. Positive validator chains now use
`scratch/field/ft0181/validation/...`; checker scratch remains available for
negative tests and generated checker output.

## Non-evidence boundary

This revision does not accept evidence. It makes synthetic or checker-origin
source chains harder to mistake for live field state. The actual unblocker remains
a real owner-reviewed packet or a documented route block.
