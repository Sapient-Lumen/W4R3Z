# rev0065 refactor/audit note

rev0065 adds `src/muc5/counter_response.py` as a reusable counter-policy response gate, plus a public `counter_guard` scoring profile in `src/muc5/public_agents.py`.

## What moved out of one-off script logic

- matched counter-policy arm construction for `counter60_vs_threat40`, `counter40_vs_threat40`, and `counter60_vs_threat60`;
- balanced spec generation over life, seat, start player, seed, and counter-policy axis;
- seed-disjoint stress-spec generation for selected rescue cells;
- target-perspective annotation and mechanism summaries for counter-response games;
- legacy-vs-`counter_guard` comparison rows;
- executable claim-quarantine rows that attach rev0064 guarded-threat demotions to rev0065 counter-response status;
- live gate checks for primary/stress game count, truncation absence, C++ parity, forensic coverage, closure-feature coverage, and replay samples.

## Audit correction

rev0064's demotion was valid for the historical CF34/ranker pilot, but it could be misread as a deck-level impossibility result.  rev0065 splits those two claims.  Old CF34 evidence remains quarantined, while `counter_guard` creates a new named response candidate that must be evaluated on its own evidence.

## Ballast discipline

rev0065 generated 50254 C++ checked transition rows across primary and stress panels, but ships only compact 240-row samples for each panel plus summary/forensic tables.  The live artifact audit forbids `data/rev0065*_cpp_transitions.csv` and `data/rev0065*_transition_rows.csv`.

## Semantics

No simulator rules changed.  Existing CF34/ranker behavior remains unchanged.  `counter_guard` is a new explicit public profile, not a replacement for old agents.
