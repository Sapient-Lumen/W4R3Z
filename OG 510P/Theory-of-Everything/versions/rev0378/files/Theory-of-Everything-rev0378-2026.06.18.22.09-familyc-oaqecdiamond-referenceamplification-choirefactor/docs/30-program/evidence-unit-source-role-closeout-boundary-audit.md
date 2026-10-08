# Evidence-unit source-role closeout boundary audit

`rev0337` repairs a narrow but consequential B-mode evidence-unit leak. The archive already separated successor/runway and causal-source ambiguity from acquired likelihood pressure, but `EU-0013-CMB-BMODE-PRIMORDIAL` still retained `REF-0633` in acquired evidence-unit `source_refs`. That reference is CMB-S4 closeout/status custody, not an acquired B-mode map, bandpower, or likelihood product.

## Repair

- `REF-0633` is removed from `EU-0013-CMB-BMODE-PRIMORDIAL.source_refs`.
- `EU-0013-CMB-BMODE-PRIMORDIAL.status_or_forecast_refs` now stages `REF-0633`, `REF-0685`, `REF-0686`, and `REF-0687` outside acquired source credit.
- `tools/cmb_bmode_source_role_policy.py` now rejects closeout/status refs in acquired evidence-unit `source_refs` and requires `REF-0633` to remain in the status/forecast staging field.
- SPT-3G public products `REF-0640`, `REF-0641`, and `REF-0642` remain acquired/public S2 replay, foreground, and likelihood pressure.

## Why this is substantive

CMB-S4 status is important for forecast-realization and public-record runway accounting, but it cannot carry acquired tensor evidence. A shutdown/closeout notice should change planning pressure and expectations; it should not sit inside the same evidence-unit source bucket as an actual public likelihood or bandpower product.

The B-mode lane therefore remains a constraint lane:

- SPT-3G/BICEP-style products can support public replay and upper-bound pressure.
- CMB-S4 closeout and successor forecasts support status/runway pressure.
- many-source/foreground/causal-source ambiguity remains denominator pressure.
- none of these imply tensor detection, inflationary identity, quantum-gravity ontology, or ToE promotion.

## Non-promotion rule

No route is promoted. `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` remains `S2`. This change only prevents a status/closeout source from being spent as acquired evidence-unit support.
