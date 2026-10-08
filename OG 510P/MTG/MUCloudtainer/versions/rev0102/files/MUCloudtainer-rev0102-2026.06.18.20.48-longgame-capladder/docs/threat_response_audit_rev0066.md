# rev0066 threat-response audit — self-counter guard and pressure gate

## Purpose

rev0065 produced a real but risky `counter_guard` rescue signal against a fixed `threat_closure` baseline.  rev0066 tests the next fragile point: did `counter_guard` find a robust counter-wall response, or merely exploit the next fixed threat pilot?

While tracing that question, rev0066 exposed a sharper audit issue: the legal menu allows a player to counter their own spell, and the guarded public scorers were valuing a counter target by card name without checking target controller.  A threat pilot could therefore choose Counterspell/Force against its own Overlord or Jace.  The simulator rules are unchanged, but the guarded public profiles now penalize selected own-spell counters.

## Code changes

```text
src/muc5/public_agents.py
  _stack_spell_for_action()
  _targets_own_spell()
  threat_closure target-ownership guard
  counter_guard target-ownership guard
  new threat_pressure profile

src/muc5/threat_response.py
  threat-response panel builder
  counter target-ownership audit
  threat-response comparison/gate helpers
```

`threat_pressure` remains public-information-only.  It uses visible stack target ownership, public Jace loyalty, public creature counts, own hand, and own library count.  It attacks opposing Jace harder and avoids redundant Overlord churn once bodies/library pressure are already sufficient.

## Primary panel

Focus score is the `counter_guard` target score.  Lower score means the threat side has weakened or refuted the counter rescue.

```text
primary games: 144
life totals: 20, 40
cells: counter40/threat40, counter60/threat40, counter60/threat60
threat axis: repaired threat_closure vs threat_pressure
```

|size_axis|starting_life|counter_guard_score_vs_repaired_closure|counter_guard_score_vs_threat_pressure|pressure_minus_closure_counter_score_delta|provisional_read|
|---|---|---|---|---|---|
|counter40_vs_threat40|20|0.3333333333333333|0.4166666666666667|0.0833|mixed_or_underpowered|
|counter40_vs_threat40|40|0.9166666666666666|0.75|-0.1667|counter_guard_mixed_under_pressure|
|counter60_vs_threat40|20|0.25|0.5|0.2500|counter_guard_mixed_under_pressure|
|counter60_vs_threat40|40|0.6666666666666666|0.9166666666666666|0.2500|counter_guard_rescue_survives_pressure|
|counter60_vs_threat60|20|0.4166666666666667|0.4166666666666667|0.0000|mixed_or_underpowered|
|counter60_vs_threat60|40|0.5|0.4166666666666667|-0.0833|mixed_or_underpowered|

The primary panel is mixed.  The new threat pressure does not globally refute `counter_guard`.  It weakens some life-40 cells, but it backfires or washes out elsewhere.  The strongest primary survival signal is still `counter60_vs_threat40` at life 40, where `counter_guard` scores 0.9167 against `threat_pressure`.

## Seed-disjoint stress pass

The stress pass expands the two rev0065 rescue cells that mattered most:

```text
counter60_vs_threat40, life 40
counter60_vs_threat60, life 20
stress games: 64
```

|size_axis|starting_life|counter_guard_score_vs_repaired_closure|counter_guard_score_vs_threat_pressure|pressure_minus_closure_counter_score_delta|provisional_read|
|---|---|---|---|---|---|
|counter60_vs_threat40|40|0.9375|0.625|-0.3125|counter_guard_mixed_under_pressure|
|counter60_vs_threat60|20|0.3125|0.5|0.1875|counter_guard_mixed_under_pressure|

Stress changes the read.  `threat_pressure` materially reduces the 60-vs-40 life-40 rescue cell from 0.9375 to 0.6250, but does not kill it.  In the 60-vs-60 life-20 cell, pressure is worse for the threat side than repaired closure in this seed block.  The honest label is therefore:

```text
counter_guard survives current threat-pressure stress in selected cells,
but the edge is policy-ladder-sensitive and should not be promoted as stable.
```

## Stack target-ownership audit

The new ownership audit reruns every game and counts selected counter actions whose target spell was controlled by the acting player.

|size_axis|starting_life|threat_policy_axis|games|sum_selected_counter_actions|sum_selected_own_spell_counters|sum_threat_selected_own_spell_counters|
|---|---|---|---|---|---|---|
|counter40_vs_threat40|20|jace_pressure_threat_response|12|106|0|0|
|counter40_vs_threat40|20|library_aware_threat_closure_targetguarded|12|87|0|0|
|counter40_vs_threat40|40|jace_pressure_threat_response|12|93|0|0|
|counter40_vs_threat40|40|library_aware_threat_closure_targetguarded|12|124|0|0|
|counter60_vs_threat40|20|jace_pressure_threat_response|12|96|0|0|
|counter60_vs_threat40|20|library_aware_threat_closure_targetguarded|12|76|0|0|
|counter60_vs_threat40|40|jace_pressure_threat_response|12|88|0|0|
|counter60_vs_threat40|40|library_aware_threat_closure_targetguarded|12|89|0|0|
|counter60_vs_threat60|20|jace_pressure_threat_response|12|95|0|0|
|counter60_vs_threat60|20|library_aware_threat_closure_targetguarded|12|71|0|0|
|counter60_vs_threat60|40|jace_pressure_threat_response|12|85|0|0|
|counter60_vs_threat60|40|library_aware_threat_closure_targetguarded|12|109|0|0|

Across primary + stress:

```text
counter-ownership audit games: 208
selected own-spell counters:   0
threat own-spell counters:     0
```

This is now a live gate: future guarded public profiles should not accidentally counter their own spells unless a revision explicitly studies that tactic.

## Validation summary

```text
pytest:                            see data/rev0066_test_report.txt
smoke:                             see data/rev0066_smoke.txt
primary threat-response games:      144
stress threat-response games:        64
forensic reruns:                    208
closure feature reruns:             208
counter ownership audit games:      208
truncations:                        0
C++ chosen transitions checked:     33446
C++ mismatches/skips:               0 / 0
replay samples:                     12 / 12 passed
selected own-spell counters:        0
```

## Next highest-risk work

The next step should not be more doctrine.  It should be a small policy-ladder tournament with live gates:

```text
threat_closure_targetguarded
threat_pressure
counter_guard
counter_guard_no_jace_zero
counter_guard_attack_jace_variant
```

The goal is to determine whether the current counter rescue survives local counterplay or is merely the next exploit in a two-policy ladder.
