# Route decision handoff and package-smoke audit

Revision: `rev0319`

## Risk repaired

`rev0318` made every live candidate route visible to forecast-or-decision pressure, but seven routes still had no explicit decision-experiment handoff. That left a failure mode where a lane could carry a forecast row and still avoid an outcome map: the route had a prospective target, but no executable decision surface saying what positive, confounded, null, or rollback outcomes would do to route wording.

`rev0319` closes that gap. Each live route now has at least one `DECISION-EXPERIMENT-LEDGER.json` row, and the generated decision/forecast route-edge audit has a first-class zero-count invariant for routes lacking decision experiments.

## Rows added

- `DX-0007-FAMILYB-LOCAL-LAW-RECOVERY-STRESS-TEST`
- `DX-0008-STRINGM-OBSERVED-SECTOR-INVERSE-ATLAS`
- `DX-0009-AS-REGULATOR-PORTABILITY-EXTRACTION`
- `DX-0010-CAUSAL-SET-MATTER-CONTINUUM-RECOVERY`
- `DX-0011-AMPLITUDES-BOOTSTRAP-CONSTRAINT-INVERSION`
- `DX-0012-QRF-PUBLIC-WITNESS-PORTABILITY-ASSAY`
- `DX-0013-GRAVITON-COUNTING-STATE-STATISTICS-CORRIDOR`

The new rows reuse existing route-local empirical-delta pressure where available, including `ED-0015-FAMILYB-THERMO-LOCAL-LAW-SCOPE-PRESSURE`, `ED-0013-AS-AMPLITUDE-REGULATOR-PORTABILITY-PRESSURE`, and `ED-0014-CAUSAL-SET-QSG-DYNAMICS-PRESSURE`. That avoids manufacturing a parallel registry layer just to satisfy a coverage metric.

## Refactor/audit change

The decision/forecast audit now reports both routes lacking any route-facing forecast-or-decision row and routes lacking a route-facing decision-experiment row. `tools/lint_archive.py` rejects either failure. Forecasts can point toward future tests, but route-facing authority changes must pass through a decision row with public artifacts, negative controls, empirical-delta hooks, and outcome effects.

The release-boundary refactor remains in force: `make package` runs `index`, `lint`, deterministic packaging, extraction smoke, extracted-tree lint, and byte-identical rebuild verification. The package smoke check is not scientific support; it is a guard against stale generated surfaces, transient files, nested archives, and non-replayable release bytes.

## Non-promotion rule

No row added here promotes a route. Decision experiments describe how realized public artifacts would be interpreted later. They do not create realized evidence and cannot bypass route ceilings, empirical-delta gates, observed-sector obligations, negative controls, or rollback rules.
