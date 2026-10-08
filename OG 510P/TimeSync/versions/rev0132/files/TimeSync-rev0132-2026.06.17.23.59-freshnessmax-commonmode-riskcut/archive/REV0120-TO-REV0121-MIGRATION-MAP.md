# TimeSync rev0120 to rev0121 migration map

| rev0120 condition | rev0121 disposition |
|---|---|
| Receipt still declared rev0119 | Receipt becomes source of truth and is validated against baseline, filename, manifest, and output |
| Validator/linter hard-coded rev0120 | Both derive rev0121 from the receipt |
| `datetime.fromisoformat` collapsed >6 fractional digits | Exact rational RFC 3339 ordering/subtraction |
| 31 `.pyc` files shipped and ignored | Removed; release builder and integrity check reject generated caches |
| Manifest only listed file hashes | Manifest v2 adds revision and archive-root identity; every source file is covered |
| ZIP metadata inherited filesystem variation | Deterministic order, member timestamp, and normalized permissions |
| FT-0090 continued internal mutation/decomposition work | Closed; FT-0121 requires one real adapter and end-to-end evaluator |
| 361 semantic vectors / 88 derivations | 362 vectors / 89 derivations with nanosecond inversion regression |
| Mission direction scattered across many notes | Consolidated in `MISSION-COMPASS-2026.06.17-rev0121.md` |

No TimeState field, profile rule, evidence class, or abstract transport adapter changed in rev0121.
