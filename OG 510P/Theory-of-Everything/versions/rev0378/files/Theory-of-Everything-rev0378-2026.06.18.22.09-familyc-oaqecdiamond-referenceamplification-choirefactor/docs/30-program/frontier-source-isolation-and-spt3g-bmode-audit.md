# Frontier source isolation and SPT-3G B-mode pressure audit

Revision: `rev0320`

## Risk addressed

The live frontier-source layer had become too permissive: generic multi-route rows could carry fresh source references and thereby make unrelated routes look current. The most severe example was `EU-0014-METADATA-PROVENANCE-WRAPPER`, which spans all 13 live routes while carrying GW, DESI, Euclid, CERN, and Euclid-timeline refs. That is custody bleed, not scientific support.

## Corrections made

- Removed volatile frontier refs from `EU-0014-METADATA-PROVENANCE-WRAPPER`; it remains an S0 metadata/provenance wrapper only.
- Removed B-mode/LISA live-source refs from generic multi-route defeater rows where they were acting as source bleed rather than route-local pressure.
- Removed the learned-inverse benchmark ref from the multi-route `PRC-CODE-DATA-BENCHMARK` carrier so the benchmark does not accidentally refresh asymptotic-safety or causal-set lanes.
- Added `tools/frontier_source_policy.py` and generated `docs/30-program/frontier-source-custody-isolation-audit.generated.md` so volatile source refs must be route-local or watchlist-only.
- Added route-local SPT-3G acquired/public BB bandpower and likelihood pressure for the primordial-tensor B-mode lane via `ED-0016-SPT3G-BMODE-BANDPOWER-LIKELIHOOD-PRESSURE`.

## Scientific effect

The B-mode route is stronger than a pure successor-forecast corridor because it now has acquired public SPT-3G bandpower/likelihood pressure. It is still capped at `S2`: foreground power, field/mask dependence, delensing, likelihood/model choices, and absence of a tensor detection remain live blockers.

## Non-promotion rule

This revision does not promote any route. It removes source bleed, adds route-local replay pressure, and requires the generated authority graph and freshness/isolation audits to make that distinction executable.
