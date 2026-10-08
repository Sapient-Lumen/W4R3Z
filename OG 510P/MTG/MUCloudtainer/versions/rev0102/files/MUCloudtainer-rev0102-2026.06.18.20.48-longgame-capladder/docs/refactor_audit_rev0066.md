# rev0066 refactor audit

rev0066 changes the cube in two places: policy scoring and reusable diagnostics.  It does not change referee/gameplay rules.

## Refactored policy target ownership

Added central public helpers in `src/muc5/public_agents.py`:

```text
_stack_spell_for_action(obs, action)
_targets_own_spell(obs, action)
```

These helpers inspect only public stack data already present in the `DecisionFrame` observation.  `threat_closure`, `threat_pressure`, and `counter_guard` now penalize selected Counterspell/Force actions that target the acting player's own spell.

Why this mattered: while investigating `counter_guard` rescue cells, a trace showed the threat side countering its own Overlord.  That is legal under the referee, but it was not intended by the public baseline profile and could poison claim interpretation.

## New reusable threat-response layer

Added `src/muc5/threat_response.py` with:

```text
rev0066_threat_response_arms()
threat_response_specs()
threat_response_stress_specs()
annotate_threat_response_rows()
compare_threat_response_by_life()
counter_target_ownership_features_from_spec()
summarize_counter_ownership_rows()
threat_response_gate_report()
```

The new layer keeps the rev0066 experiment from becoming a one-off script and creates a target-ownership gate for future public profiles.

## Artifact discipline

rev0066 generated 33446 C++ transition rows but shipped only compact transition samples and forensic summaries.  No full `rev0066*_cpp_transitions.csv` ballast is included.

## Known caveat

The inherited monolithic `scripts/audit_cube.py` remains broad and historically focused.  rev0066 therefore uses both the inherited audit and a live artifact audit for current-revision files.
