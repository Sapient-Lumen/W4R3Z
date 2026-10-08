# Graviton-counting source partition audit (rev0321)

## Risk corrected

The lab graviton-counting lane needs independently observed gravitational-wave events as source/timing triggers, but that does not make a classical GW catalog, LISA mission schedule, or LISA hardware update into detector-local quantum-graviton evidence. rev0320 allowed the same fresh frontier refs to sit on graviton-counting evidence, severity, calibration, credit, and carrier rows. That was a source-role bleed: the route could look newly current because LISA or GWTC moved, even though the quantum-click/counting artifact had not materialized.

## Change made

rev0321 removes LISA and LISA-science/runway refs from route-local graviton-counting rows and replaces them with route-local single-graviton / graviton-detection sources. Classical GW catalog refs remain allowed only as trigger/source-timing carriers on explicitly trigger-bearing rows. The new generated audit `docs/30-program/graviton-counting-source-role-audit.generated.md` enforces this split.

## Lint enforcement repair

A second bug was found while making this repair: `tools/lint_archive.py` imported the frontier source-isolation evaluator but did not call it. The source-isolation audit could be generated yet not enforced by `make lint`. rev0321 wires both `evaluate_frontier_source_isolation()` and `evaluate_graviton_source_role()` into lint, so future source-role drift fails the package path instead of surviving as a stale generated table.

## Non-promotion rule

Single-graviton access remains a serious discriminator corridor, not a theory selector. A clean future click/count/tomography record could strengthen an S3 method pocket only after detector-local records, calibration, background rejection, source-state controls, and public replay exist. Classical GW events are trigger covariates; LISA status is forecast runway for strong-field GW science; neither is ToE-candidate identity.

## Release-smoke cloudtainer note

The release smoke harness now executes the extracted-tree lint/schema tools directly in this cloudtainer while retaining the historical `make lint` compatibility marker in the smoke source. This avoids nested make process instability without reducing the checks performed.
