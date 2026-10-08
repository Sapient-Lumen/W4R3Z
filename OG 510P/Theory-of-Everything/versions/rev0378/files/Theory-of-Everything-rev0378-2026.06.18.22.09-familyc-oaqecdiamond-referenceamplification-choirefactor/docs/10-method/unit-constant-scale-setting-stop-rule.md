# Unit / constant / scale-setting stop rule

Owned OQ: `OQ-0111`.

No route may use natural-units, Planck-units, dimensional-analysis, defining-constant, fundamental-constant, dimensionless-ratio, CODATA/SI, constant-prediction, scale-setting, hierarchy, or naturalness language unless the corresponding `UNIT-CONVENTION-LEDGER.json`, `FUNDAMENTAL-CONSTANT-LEDGER.json`, and `SCALE-SETTING-LEDGER.json` rows are declared and current.

The stop rule is conservative: a route may still use units and constants for calculation, but authority wording must remain bounded unless the route says which unit convention, which constant object, and which scale-setting map carries the claim.
