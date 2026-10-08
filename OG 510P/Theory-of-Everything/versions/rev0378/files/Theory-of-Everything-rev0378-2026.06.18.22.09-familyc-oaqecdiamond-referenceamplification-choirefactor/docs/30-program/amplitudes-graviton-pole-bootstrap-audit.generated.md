# Amplitudes/bootstrap gravity-IR positivity source-role audit (generated)

Generated from the amplitudes/bootstrap route, forecast, decision, empirical-delta, evidence-unit, and route-control ledgers. Do not edit directly; run `make index` after changing these rows.

- Route checked: `R-OQ0057-AMPLITUDES-BOOTSTRAP`
- Required current refs: `REF-0652`, `REF-0653`, `REF-0654`, `REF-0655`, `REF-0656`
- Empirical-delta rows: `37`
- Duplicate empirical-delta ordinal stems: `0`
- Missing empirical-delta ordinal stems: `0`
- Gravity/IR positivity checks: `37`
- Gravity/IR positivity failures: `0`

| Check | Passed | Detail |
|---|---:|---|
| `route-present` | `true` | route `R-OQ0057-AMPLITUDES-BOOTSTRAP` must exist |
| `route-current-state-capped` | `true` | current authority is `S2`; expected `S2` |
| `route-promotion-ceiling-capped` | `true` | promotion ceiling is `S2`; expected `S2` |
| `route-names-gravity-ir-pressure` | `true` | route text missing terms [] |
| `forecast-present` | `true` | forecast `DF-0016-AMPLITUDES-GRAVITY-IR-LOOP-POSITIVITY-STABILITY` must exist |
| `forecast-route-local` | `true` | forecast route is `R-OQ0057-AMPLITUDES-BOOTSTRAP` |
| `forecast-credit-capped` | `true` | forecast current maximum is `S2`; expected `S2` |
| `forecast-current-refs` | `true` | missing refs []; present ['REF-0652', 'REF-0653', 'REF-0654', 'REF-0655', 'REF-0656'] |
| `forecast-non-promotion` | `true` | forecast must explicitly block closure/promotion spending |
| `forecast-replay-denominators` | `true` | required_public_record missing terms [] |
| `delta-present` | `true` | delta `ED-0021-AMPLITUDES-GRAVITY-IR-POSITIVITY-PRESSURE` must exist |
| `delta-route-local` | `true` | delta route_ids are `['R-OQ0057-AMPLITUDES-BOOTSTRAP']` |
| `delta-credit-capped` | `true` | delta promotion ceiling is `S2`; expected `S2` |
| `delta-current-refs` | `true` | missing refs []; present ['REF-0652', 'REF-0653', 'REF-0654', 'REF-0655', 'REF-0656'] |
| `delta-hard-denominators` | `true` | delta text missing terms [] |
| `decision-present` | `true` | decision experiment `DX-0011-AMPLITUDES-BOOTSTRAP-CONSTRAINT-INVERSION` must exist |
| `decision-current-refs` | `true` | missing refs []; present ['REF-0166', 'REF-0174', 'REF-0335', 'REF-0652', 'REF-0653', 'REF-0654', 'REF-0655', 'REF-0656'] |
| `decision-hooks-delta` | `true` | decision hooks ['ED-0005-DUALITY-UNDERDETERMINATION-QUOTIENT', 'ED-0021-AMPLITUDES-GRAVITY-IR-POSITIVITY-PRESSURE'] |
| `decision-public-artifact-denominators` | `true` | decision artifact missing terms [] |
| `evidence-present` | `true` | evidence unit `EU-0007-AMPLITUDES-BOOTSTRAP-CONSISTENCY` must exist |
| `fresh-refs-not-acquired-evidence` | `true` | fresh refs incorrectly present on acquired evidence unit: [] |
| `evidence-credit-capped` | `true` | evidence maximum credit is `S2`; expected `S2` |
| `evidence-names-current-delta-handoff` | `true` | evidence empirical_delta_ids should expose the route-local pressure handoff without carrying fresh refs: ['ED-0005-DUALITY-UNDERDETERMINATION-QUOTIENT', 'ED-0021-AMPLITUDES-GRAVITY-IR-POSITIVITY-PRESSURE', 'ED-0031-QM-QFT-GAUGE-OBSERVED-SECTOR-PRESSURE', 'ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE', 'ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE', 'ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE', 'ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE'] |
| `condition-row-present-STB-0007-AMPLITUDES-BOOTSTRAP` | `true` | STABILITY-POSITIVITY-LEDGER.json:STB-0007-AMPLITUDES-BOOTSTRAP |
| `condition-row-refs-STB-0007-AMPLITUDES-BOOTSTRAP` | `true` | missing refs []; present ['REF-0335', 'REF-0336', 'REF-0338', 'REF-0652', 'REF-0653', 'REF-0654', 'REF-0655'] |
| `condition-row-present-SCAT-0007-AMPLITUDES-BOOTSTRAP` | `true` | SCATTERING-OBSERVABLE-LEDGER.json:SCAT-0007-AMPLITUDES-BOOTSTRAP |
| `condition-row-refs-SCAT-0007-AMPLITUDES-BOOTSTRAP` | `true` | missing refs []; present ['REF-0451', 'REF-0453', 'REF-0455', 'REF-0456', 'REF-0652', 'REF-0653', 'REF-0656', 'REF-0710', 'REF-0711'] |
| `condition-row-present-IRD-0007-AMPLITUDES-BOOTSTRAP` | `true` | INFRARED-DRESSING-LEDGER.json:IRD-0007-AMPLITUDES-BOOTSTRAP |
| `condition-row-refs-IRD-0007-AMPLITUDES-BOOTSTRAP` | `true` | missing refs []; present ['REF-0450', 'REF-0452', 'REF-0453', 'REF-0454', 'REF-0654', 'REF-0655'] |
| `condition-row-present-ASYM-0007-AMPLITUDES-BOOTSTRAP` | `true` | ASYMPTOTIC-STATE-LEDGER.json:ASYM-0007-AMPLITUDES-BOOTSTRAP |
| `condition-row-refs-ASYM-0007-AMPLITUDES-BOOTSTRAP` | `true` | missing refs []; present ['REF-0450', 'REF-0451', 'REF-0453', 'REF-0656'] |
| `empirical-delta-ordinal-stems-unique` | `true` | duplicate stems [] |
| `empirical-delta-ids-well-formed` | `true` | bad ids [] |
| `empirical-delta-ordinals-contiguous` | `true` | missing ordinals [] |
| `old-familyc-ordinal-absent` | `true` | old id present=False |
| `familyc-renumbered-present` | `true` | expected id `ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE` present=True |
| `amplitudes-delta-present-in-namespace` | `true` | expected id `ED-0021-AMPLITUDES-GRAVITY-IR-POSITIVITY-PRESSURE` present=True |

## Non-promotion rule

Current gravitational S-matrix/bootstrap papers can strengthen only route-local constraint, IR/loop stability, and kinematic-domain pressure. They may be named by the acquired evidence unit only as an empirical-delta handoff handle; the fresh refs and source pressure remain route-local, and the route cannot move above S2 without an independent candidate-native bridge, observed-sector public record, and replayable gravity-specific stability controls.
