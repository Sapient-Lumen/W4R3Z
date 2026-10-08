# rev0304 field execution risk burndown

| Risk | rev0304 control | Residual boundary |
|---|---|---|
| Checker scratch is mistaken for field state | Default field scan root moved to `scratch/field/ft0181`; checker fixtures moved to `scratch/checks`; rev0303 provenance firebreak remains | Legacy `SCRATCH=` overrides can still scan other roots if the operator chooses them |
| A clean maintainer run starts from an ambiguous scratch tree | `make owner-field-work` now prepares and reroutes inside the field lane without requiring custom path discipline | Operators should start fresh if the field lane contains old manual experiments |
| Control sprawl substitutes for owner action | The revision changes the execution plane only; no new schema, registry family, or followthrough was created | Future turns must continue to prefer real owner-route work over new doctrine |
| Prepared packet is mistaken for evidence | Existing packet, router, and after-human-send boundaries remain: prepared packet is `PREPARED_NOT_SENT` and `not_evidence` | A human still has to send/adapt the packet outside the archive before any send clock can be recorded |
| Returned owner context bypasses the receipt/intake path | The router keeps the returned CSV source guard and post-readout context receipt path | Actual owner context must remain outside the archive until the receipt gate links it |
| Late-stage local artifacts imply closure | Existing no-service/no-public/no-lifecycle/no-closure fields remain on readout, dispatch, recheck, and context receipt | Real SRC2+ acceptance and closeout remain absent |

The highest priority remains external: obtain or route real owner-reviewed material.
The highest local priority is now simple: keep `scratch/field/ft0181` as the only
ordinary live lane and do not spend field time interpreting checker scratch.
