# rev0337 claim-language current-boundary and realization audit

## Risk targeted

Structured S-level ceilings were already enforced, but claim-language permissions still controlled the prose surface: what the cube is allowed to say in summaries, ledgers, and handoff notes.  A route may have a higher `promotion_ceiling` than its current `authority_state`, but that ceiling must not leak into current-language wording.

The concrete leak was in conditional-ceiling rows:

- `LPP-0006-CAUSAL-SET` allowed bare maximum `S2` language while `R-OQ0057-CAUSAL-SET` is current `S1`.
- `LPP-0011-LAB-GRAVITON-COUNTING` allowed bare maximum `S3` language while the route is current `S2`.
- `LPP-0008-LAB-GIE-BMV` had the right human posture but lacked machine-readable current/conditional boundary fields.

## Substantive boundary

Causal-set current language remains `S1`: QSG/Bell-causality, continuum-emergence, matter-correlator/scattering, and horizon/entropy rows are route-local pressure until public continuum/dynamics/matter-sector replay survives the route controls.  `S2` language is conditional only.

Lab graviton-counting current language remains `S2`: quantum-sensing, stimulated-absorption, and count/statistics proposals are serious route-local pressure, but classical GW trigger catalogs are timing/source covariates and not detector-local quantum-click evidence.  `S3` language is conditional only after a detector-local acquired public count/click/statistics record survives source-state, background, trigger-correlation, and model-class controls.

Lab GIE/BMV current language remains `S2`: protocol-relaxation, shielding/stability, thermal-noise, and classical/nonlocal comparator papers are feasibility and inference-boundary pressure.  `S3` wording is conditional only after a direct acquired public GIE/BMV record survives shielding, thermal-noise, subsystem, nuisance, and model-class controls.

## Changes made

- Added `tools/claim_language_current_boundary_policy.py`.
- Added generated audit `docs/30-program/claim-language-current-boundary-audit.generated.md`.
- Wired the new policy into `tools/sync_generated_surfaces.py` and `tools/lint_archive.py`.
- Added machine-readable `current_authority_state`, `conditional_authority_ceiling`, `required_qualifiers`, and `ceiling_spend_rule` fields to the conditional claim-language rows.
- Removed bare maximum-ceiling phrasing from conditional rows and added explicit forbidden unqualified-current ceiling phrases.
- Added route-local source context refs to the affected claim-language rows without changing evidence-unit source credit.

## Refactor note

This is not a new registry lane.  It is a cross-cutting guard over an existing prose authority surface.  The evaluator summarizes pass/fail coverage compactly and rejects drift when `make index` is not rerun.

## Non-promotion rule

No route is promoted.  The revision narrows allowed wording and makes conditional ceilings harder to spend.
