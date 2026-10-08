# rev0061 refactor and audit note

rev0061 moved the new causal-ablation machinery out of the run script and into reusable source code:

```text
src/muc5/mechanism_ablation.py
```

The module now owns:

```text
MechanismAblationArm
replace_jace_with_islands()
replace_counterspell_with_islands()
replace_jace_and_counterspell_with_islands()
all_island_buffer_deck()
rev0061_mechanism_ablation_arms()
mechanism_ablation_specs()
annotate_mechanism_ablation_rows()
compare_mechanism_ablation_by_life()
compare_forensic_ablation_by_life()
mechanism_ablation_gate_report()
```

The important audit fix is in the forensic validator:

```text
src/muc5/trajectory_forensics.py
```

Before rev0061, `validate_forensics_against_game_row()` accepted the historical pre-rev0060 decision-count contract but would reject fresh corrected rev0060+ rollout rows.  It now accepts either:

```text
expected decisions == corrected applied_decisions
expected decisions == legacy_terminal_row_decisions
```

That keeps old evidence reproducible while allowing new scripts to validate against corrected live game rows.

Tests added/expanded:

```text
tests/test_rev0061_mechanism_ablation.py
tests/test_rev0060_trajectory_forensics.py
```

Artifact retention remains disciplined: the revision generated 52,438 C++ chosen-transition checks but ships only a 240-row sample plus compact forensic summaries.
