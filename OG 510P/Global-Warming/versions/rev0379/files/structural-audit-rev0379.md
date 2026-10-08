# Structural audit — rev0379

## Highest-risk incomplete work

The cube now has mature request language but still lacks the actual external event: dispatch receipts and response packets. Rev0379 therefore avoids adding more doctrine and instead builds a current execution surface: route targets, workorders, sidecars, intake CLI, and wait-state clocks.

## Concrete defect corrected

The active surface was still too easy to misuse: older request packets and prior validation/report surfaces remained nearby, creating duplicate-dispatch and stale-route risk. Rev0379 classifies only eight request workorders as active and binds each to a sidecar and route-target row.

## Route/terminology controls

- FEMA/DHS: online route only; do not use stale email/mail FOIA assumptions.
- NRC: ADAMS APS first, FOIA/PDR only if records are not public.
- Ohio/Columbiana: preserve ENS/IPAWS/EAS/WEA/siren aliases because the current Columbiana plan replaced WENS with ENS and defines an ENS/IPAWS concept of operations.
- West Virginia/Hancock: preserve direct-to-custodian FOIA logic and Hancock OEM route context.

## Refactor

The active capsule is now a dispatch/intake capsule, not a history capsule. It excludes old validation-report mirrors, historical source-canonical tables, and superseded request generations unless a current workorder points to a canonical request file.

## Remaining blockers

No request is sent; no receipt is imported; no official post-meeting packet is imported; no EOF closure packet is imported; no local readiness proofcut is closed.
