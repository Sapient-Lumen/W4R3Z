# FamilyC subregion-state portability audit (generated)

Generated from route, forecast, empirical-delta, decision-experiment, and evidence-unit ledgers. Do not edit directly; run `make index` after changing FamilyC subregion-state portability custody.

- Required current theory refs: `REF-0649, REF-0650`
- Checks run: `19`
- Subregion-state portability failures: `0`

| Check | Passed | Detail |
|---|---:|---|
| route present | `true` | R-OQ0057-FAMILYC-EW-CODE |
| route authority remains bounded S3 | `true` | authority_state=S3 |
| route ceiling remains S3 | `true` | promotion_ceiling=S3 |
| forecast present | `true` | DF-0015-FAMILYC-SUBREGION-STATE-DICTIONARY-PORTABILITY |
| forecast route-local | `true` | route_id=R-OQ0057-FAMILYC-EW-CODE |
| forecast current credit bounded | `true` | current_maximum_credit=S3 |
| forecast carries current source refs | `true` | missing=[] |
| forecast non-promotion language present | `true` | fresh subregion/gravitating-region state proposals are route pressure, not acquired candidate-native witness closure and not S4/S5 identity support |
| empirical delta present | `true` | ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE |
| delta route-local | `true` | route_ids=['R-OQ0057-FAMILYC-EW-CODE'] |
| delta ceiling bounded | `true` | promotion_ceiling=S3 |
| delta carries current source refs | `true` | missing=[] |
| delta residual blocks acquired-evidence overclaim | `true` | new theory pressure does not supply an acquired empirical witness, a unique candidate identity, or a general observed-sector bridge |
| decision row present | `true` | DX-0006-FAMILYC-PUBLIC-RECONSTRUCTION-BENCHMARK |
| decision hooks new delta | `true` | empirical_delta_hooks=['ED-0003-SUBREGION-ALGEBRA-AND-EDGE-MODE-PRESSURE', 'ED-0005-DUALITY-UNDERDETERMINATION-QUOTIENT', 'ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE'] |
| multi-route decision avoids fresh source bleed | `true` | leaked_refs=[] |
| evidence unit present | `true` | EU-0001-FAMILYC-EW-RECONSTRUCTION |
| fresh theory refs absent from acquired evidence unit | `true` | leaked_refs=[] |
| evidence maximum credit remains S3 | `true` | maximum_credit=S3 |

## Non-promotion rule

This audit allows new gravitating-region/subregion-state work to pressure the S3 FamilyC route, but prevents the same references from being carried as acquired evidence-unit support. It promotes no route.

