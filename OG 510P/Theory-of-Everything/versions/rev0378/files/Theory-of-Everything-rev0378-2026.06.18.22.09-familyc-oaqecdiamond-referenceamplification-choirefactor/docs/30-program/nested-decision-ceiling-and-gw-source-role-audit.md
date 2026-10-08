# Nested decision-ceiling and GW source-role audit

Revision: `rev0327`

## Why this was the risky seam

`rev0326` closed the visible multi-route authority-ceiling loophole, but the executable check still read only top-level S-level fields. Decision rows can carry conditional authority in nested `outcome_effects[*].promotion_ceiling` clauses, and those clauses are just as spendable as a top-level field when a later reader asks what a public record would authorize.

The first recursive pass exposed four concrete failures:

- `DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION` carried a nested `S3` outcome while `R-OQ0057-GW-STRONGFIELD-GR` is capped at `S2`.
- `DX-0004-DESI-LATE-TIME-DARK-ENERGY-DYNAMICS` carried a nested `S3` outcome while `R-OQ0057-COSMO-DARK-ENERGY-BAO` is capped at `S2`.
- `DX-0005-CMB-PRIMORDIAL-TENSOR-BMODE` carried a nested `S3` outcome while `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` is capped at `S2`.
- `DX-0006-FAMILYC-PUBLIC-RECONSTRUCTION-BENCHMARK` was a multi-route row with nested S-level effects but no route-specific spendable ceiling map.

These were not cosmetic failures. They let generic S2 lanes advertise S3 outcomes through a nested decision clause, even after route ceilings and multi-route caps existed.

## Changes made

`tools/route_condition_ceiling_policy.py` now walks nested dictionaries and lists and treats every `promotion_ceiling`, `maximum_authority_effect`, `maximum_credit`, and `current_maximum_credit` value as spendable authority wherever it appears. The generated ceiling audit therefore sees `outcome_effects[*].promotion_ceiling` and similar future nested clauses.

The three generic empirical routes were capped back to their current route ceilings:

- GW strong-field catalog/deviation outcomes remain `S2` unless a candidate-native split route and independent evidence unit are opened.
- DESI late-time expansion candidate-fit outcomes remain `S2` unless a separate candidate dark-energy route is opened.
- Primordial B-mode clean-detection outcomes remain `S2` unless a separate tensor-interpretation route and foreground/likelihood replay surface are opened.

`DX-0006-FAMILYC-PUBLIC-RECONSTRUCTION-BENCHMARK` now carries explicit route-specific spendable caps:

- `R-OQ0057-FAMILYC-EW-CODE`: `S3`
- `R-OQ0057-FAMILYC-LEARNED-INVERSE`: `S2`

## GW strong-field source-role repair

The strong-field GW route has a second overcredit risk: future detector runway can sit next to acquired public catalog/test records and make current evidence look stronger than it is.

This revision removes LISA and next-generation detector runway refs from the current acquired evidence and current-credit rows:

- `EU-0009-GW-STRONGFIELD-CATALOG`
- `CA-GW-STRONGFIELD-GR`

Those future/runway refs remain allowed on forecast and decision rows where they belong:

- `ED-0011-LISA-AND-NEXTGEN-GW-FORECAST-CORRIDOR`
- `DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION`

The current strong-field public-test pressure is instead carried by route-local S2 source refs:

- `REF-0677`: GWTC-4 parameterized tests of GR.
- `REF-0678`: GW250114 black-hole spectroscopy and tests of GR.

The new generated audit `docs/30-program/gw-strongfield-public-test-source-role-audit.generated.md` enforces the split: current public-test refs must appear on the GW evidence/control rows, future runway refs must not appear on acquired evidence/current-credit rows, and nested decision outcomes must stay within the route ceiling.

## Non-promotion rule

No route is promoted. This revision tightens what the cube may spend from already-important empirical corridors. Current GW catalog/test records remain S2 constraint pressure; future LISA/next-generation detector runway remains forecast/decision custody; a stronger candidate claim requires a new route split with its own evidence unit, waveform/calibration/selection controls, and public replay boundary.
