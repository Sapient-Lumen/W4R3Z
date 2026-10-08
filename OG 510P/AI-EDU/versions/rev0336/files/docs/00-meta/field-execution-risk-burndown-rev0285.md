# Field execution risk burndown rev0285

## Highest current risk

`FT-0181` is still externally gated. No real owner route has been confirmed, no
real owner-reviewed `SRC2+` packet has been received, no accepted import exists,
no live-window readout exists, and no closure signoff exists.

The highest local risk is therefore false completion: a sequence of scratch
artifacts that looks like field progress while the real packet is still missing
or no longer matches the chain that produced the decision.

## Risks reduced

| Risk | Rev0285 reduction |
|---|---|
| An unrelated local file is used as the activation source packet | Activation receipt now requires the source-packet hash to equal the source CSV hash preserved through intake, seed, review, and first-packet decision. |
| A hand-edited review or seed keeps stale lineage alive | The shared guard recomputes workbench-review, workbench-seed, decision, and packet hashes before active-change routing. |
| A `ready_for_real_packet` ticket is mistaken for accepted `SRC2+` evidence | Router still stops at readiness and names the activation receipt template only. |
| A candidate workbench review launders source truth | Proceed review remains `SRC2-CANDIDATE-NOT-ACCEPTED` until the lineage-matched activation receipt exists. |
| A local activation receipt becomes evidence by implication | Receipt, ticket, and card still carry `not_evidence`, no closure effect, and no public-claim effect. |

## What remains risky

The cube still cannot create the missing external fact. A human must still send
or adapt the owner packet through an accountable route, record the send/re-ask
clock honestly, and receive a real owner-reviewed packet. Rev0285 only ensures
that if activation happens later, it must activate the same returned-packet hash
that the decision chain actually reviewed.

## Next useful work

Use `make owner-field-next` as the front door. If it emits the
`ready_for_real_packet` stop, do not create an active ticket. Locate the same
returned owner-reviewed source packet that seeded the decision, then run
`make owner-activation-receipt` with that file. If the hash does not match,
return to intake/workbench instead of activating.
