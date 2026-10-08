# rev0064 refactor/audit note

rev0064 adds `src/muc5/closure_vs_counter.py` as a reusable claim-demotion gate for active counter-wall targets against matched threat policies.

## What moved out of one-off script logic

- matched policy-pair arm construction for `counter60_vs_threat40`, `counter40_vs_threat40`, and `counter60_vs_threat60`;
- balanced C++ shadow spec generation over life, seat, start player, and seed;
- counter-wall target-perspective annotation;
- legacy-vs-closure comparison rows;
- closure-feature adapter keyed on `size_axis`;
- live revision gate checks for game count, truncations, C++ parity, feature rerun coverage, policy coverage, and size-cell coverage.

## Audit correction

rev0063's feature comparison helper was specific to inert-target labels (`target_size_axis`).  rev0064 adds a size-axis adapter so the same closure feature extractor can be used against active counter targets without emitting empty comparison artifacts.

## Ballast discipline

rev0064 generated 37748 C++ checked transitions, but ships only a 240-row compact sample plus summary/forensic tables.  The live artifact audit forbids `data/rev0064*_cpp_transitions.csv` and `data/rev0064*_transition_rows.csv`.

## Semantics

No simulator rules changed.  Existing `threat_rush` behavior remains unchanged.  `threat_closure` remains an explicit audit/control profile rather than a promoted default strategy.
