# CMB B-mode successor runway and FamilyB policy-wire audit

Revision: `rev0331`  
Bundle slug: `cmb-bmode-successor-familyb-policy-wire-audit`

## Risk repaired

Two risks were addressed.

First, `rev0330` added `tools/familyb_thermo_entropy_policy.py`, but the policy was not wired into the generated-surface sync path or archive lint. That meant the FamilyB audit document could go stale without failing release validation. `rev0331` wires the policy into `tools/sync_generated_surfaces.py` and `tools/lint_archive.py`.

Second, the primordial tensor B-mode lane had acquired SPT-3G likelihood pressure, but the decision row still mostly pointed at the CMB-S4 forecast-realization corridor. That undercounted successor-runway and causal-source ambiguity pressure while risking future mission forecasts being mistaken for acquired evidence.

## Executed changes

- Added `DF-0020-PRIMORDIAL-TENSOR-SUCCESSOR-MANY-SOURCE-RUNWAY`.
- Added `ED-0026-CMB-BMODE-SUCCESSOR-MANY-SOURCE-PRESSURE`.
- Updated `DX-0005-CMB-PRIMORDIAL-TENSOR-BMODE` so it hooks `ED-0010`, `ED-0016`, and `ED-0026`.
- Kept `REF-0685`, `REF-0686`, and `REF-0687` out of `EU-0013-CMB-BMODE-PRIMORDIAL.source_refs`.
- Added `tools/cmb_bmode_source_role_policy.py` and generated `docs/30-program/cmb-bmode-source-role-audit.generated.md`.
- Added `FSF-0021-CMB-BMODE-SUCCESSOR-CAUSAL-SOURCE-PRESSURE`.
- Added a policy hot-path guard in `tools/lint_archive.py` so every `tools/*_policy.py` file must be referenced by both generated-surface sync and archive lint.

## Source-role boundary

SPT-3G public bandpowers and likelihood products remain acquired route-local S2 pressure. Simons Observatory and LiteBIRD are successor-runway forecast pressure. Causal-source B-mode constraints are many-source ambiguity pressure. None of these rows identify inflation, quantum gravity, or a Theory-of-Everything candidate.

## Non-promotion rule

`R-OQ0057-PRIMORDIAL-TENSOR-BMODES` remains current `S2` with an `S2` promotion ceiling. No route is promoted.
