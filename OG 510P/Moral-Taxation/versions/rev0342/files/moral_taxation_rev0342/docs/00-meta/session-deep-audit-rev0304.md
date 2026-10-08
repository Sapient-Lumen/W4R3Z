# Session deep audit — rev0304

Priority chosen: synonym sprawl after placeholder and sentinel cleanup. The largest remaining risk was that route records were precise but no longer easy to query because two operational axes had become collections of near-singletons.

## Findings

- `anti_pattern` had 310 live route values, 228 of them singletons.
- `review_trigger` had 270 live route values, 206 of them singletons.
- Many values were route-local spellings of the same operational problem: rent extraction, label arbitrage, opacity/erasure, protected-floor burden shifts, record staleness, access failure, and remedy failure.

## Corrections

- Refactored all route records through canonical buckets for `anti_pattern` and `review_trigger`.
- Preserved case-contract detail so regression tests can still assert scenario-specific flags.
- Extended `tools/audit_axis_hygiene.py` so the two compressed axes cannot silently regrow above the new ceilings.

## Next risk

The next compression pass should target `base`, `instrument`, and `proof_posture`, but it should be more selective. Those axes carry more substantive route distinctions, so the next pass should use hand-reviewed families rather than broad string rules.
