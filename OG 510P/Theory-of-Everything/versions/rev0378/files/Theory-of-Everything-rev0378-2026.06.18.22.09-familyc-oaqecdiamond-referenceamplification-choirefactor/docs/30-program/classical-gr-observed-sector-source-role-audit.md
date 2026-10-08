# Classical-GR observed-sector source-role audit (rev0338)

This revision closes a remaining observed-sector recovery seam: routes could name `OSR-CLASSICAL-GR`, but the newest public classical-gravity constraints were not all route-local denominator pressure. The repair is deliberately conservative. EHT, S-star, and DESI gravity records are public burdens that a route must replay when it claims classical-GR recovery; they are not candidate-native evidence, black-hole microstate evidence, quantum-gravity evidence, or route promotion.

## Substantive boundary

- EHT M87*/Sgr A* records create horizon-scale image, polarization, plasma/source-model, calibration, and model-comparison pressure.
- GRAVITY S2 precession creates weak-field / Galactic-center relativistic-orbit replay pressure.
- DESI full-shape/growth constraints create cosmological-background and large-scale modified-gravity pressure.
- Agreement with these records can preserve only the current route state; failure rolls back the affected classical-GR wording.

## Repairs

- Added `DF-0024-CLASSICAL-GR-OBSERVED-SECTOR-REPLAY`.
- Added `ED-0030-CLASSICAL-GR-OBSERVED-SECTOR-PRESSURE`.
- Added `DX-0017-CLASSICAL-GR-OBSERVED-SECTOR-REPLAY`.
- Added `tools/classical_gr_observed_sector_policy.py` and generated audit `docs/30-program/classical-gr-observed-sector-source-role-audit.generated.md`.
- Repaired `OSR-CLASSICAL-GR.route_ids_touching` so it matches the route ledger's explicit `OSR-CLASSICAL-GR` declarations, including the FamilyB thermo-entropic route.
- Added current classical-GR refs `REF-0702` through `REF-0705` as source-role burden refs only.

## Non-promotion rule

No route is promoted. The new refs are excluded from acquired evidence-unit source credit. They can only constrain recovery claims and force route-local replay of public classical-gravity records.
