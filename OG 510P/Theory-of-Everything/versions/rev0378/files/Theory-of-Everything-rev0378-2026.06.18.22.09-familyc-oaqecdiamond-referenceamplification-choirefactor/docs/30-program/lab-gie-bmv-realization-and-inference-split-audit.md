# Lab GIE/BMV realization and inference-split audit

Revision: `rev0321`

## Why this audit exists

The Lab GIE/BMV route was the riskiest live overcredit pocket left in the cube. Its route state and evidence unit were spending too much current authority for a direct experiment that remains proposal/feasibility/public-protocol territory rather than an acquired challengeable public lab record.

The repair is not a new registry. It is a scientific-pressure correction: a future clean GIE/BMV run can still matter, but the current cube must not treat proposal/review/status literature as if the direct public experiment had already happened.

## Correction made

- `R-OQ0057-LAB-GIE-BMV` is current `S2`, not current `S3`.
- Its `promotion_ceiling` remains conditional `S3` for a future clean direct public record.
- `EU-0008-LAB-GIE-MEDIATOR` is now `forecast-public-record` with current maximum credit `S2`.
- The new empirical delta `ED-0017-GIE-BMV-INFERENCE-SPLIT-PRESSURE` records the current inference split.
- `DX-0001-DIRECT-GIE-BMV-ENTANGLEMENT` now treats a positive-clean outcome as conditional on direct acquisition, public custody, model-class split, subsystem controls, nuisance controls, and replay.
- `SV-0003-DIRECT-GIE-BMV-SEVERITY` now requires the same direct-record and model-class burden before severe-test credit can be spent.

## Source-pressure interpretation

`REF-0643` sharpens a classical-gravity / QFT-matter counterpressure: entanglement alone cannot be scored as theory-independent proof of fundamental gravity quantization unless the stronger mediation and state-space assumptions are declared and tied to the public record.

`REF-0644` prevents the opposite overcorrection. Some semiclassical-potential model classes do not generate GIE, so the right cube posture is not “entanglement proves nothing.” It is narrower: GIE/BMV is a model-class discriminator, and the relevant class split must be explicit.

`REF-0645` and `REF-0646` keep the route live as an important laboratory quantum-gravity corridor, while also confirming that the decisive object is a future direct public record rather than the existence of proposals and reviews.

## Executable controls added

- `tools/route_realization_policy.py`
- `docs/30-program/route-realization-status-audit.generated.md`
- lint enforcement that the route remains current `S2` while `EU-0008` is only `forecast-public-record`
- frontier-source isolation policy for `REF-0643` through `REF-0646`
- frontier-source freshness assertion `FSF-0008-GIE-BMV-INFERENCE-SPLIT`

## Non-promotion and demotion rule

This revision demotes current route authority for the lab GIE/BMV lane. It does not demote the scientific importance of the experiment. It separates the future experiment's possible discriminator value from the present record's actual realization status.

No route is promoted. The lab GIE/BMV lane is constrained until a direct acquired public record exists and survives the named controls.

## Release-smoke cloudtainer note

The release smoke harness now executes the extracted-tree lint/schema tools directly in this cloudtainer while retaining the historical `make lint` compatibility marker in the smoke source. This avoids nested make process instability without reducing the checks performed.
