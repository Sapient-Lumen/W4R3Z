# Structural audit rev0320

## Focus

Rev0320 audits the emergency-preparedness query path for a concrete defect: official 2024 Beaver Valley AAR findings existed in public sources, but the cube did not yet carry them into the 2026 exercise capture path as hard blockers and negative controls.

## Correction

The new route is:

`AAR baseline -> issue ledger -> prior issue carryforward -> packet/control surfaces -> firebreak validator -> SQLite open-blocker views -> public claim gate`

The legacy universal nuclear crossproduct tables remain compatibility surfaces. They are not used as emergency-readiness closure evidence.

## Zero-leak expectation

`rev0320_aar_public_source_to_local_closure_leak_v` must return zero rows. Public AARs, future exercise notices, AAR folders, news articles, and clean cross-border baselines cannot close local readiness.
