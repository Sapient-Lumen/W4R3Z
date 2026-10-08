# rev0064 closure-vs-counter audit — claim demotion pass

## Purpose

rev0063 showed that `threat_closure` fixes much of the inert all-Island pathology caused by legacy `threat_rush`.  rev0064 asks the claim-relevant follow-up: does the active `cf34_counter_wall` edge survive against a threat pilot that no longer self-decks casually?

This is a matched-policy audit.  The focal score is the active counter-wall target's score; the only policy axis being swapped inside each size cell is `threat_rush` vs `threat_closure`.

## Panel

```text
A legacy/closure: counter60 vs threat40
B legacy/closure: counter40 vs threat40
C legacy/closure: counter60 vs threat60
life totals: 20 and 40
reps: 3 per seat/start/life/arm
terminal games: 144
```

## Main result

|size_axis|starting_life|legacy_counter_score|closure_counter_score|closure_minus_legacy_counter_score_delta|provisional_read|
|---|---|---|---|---|---|
|counter40_vs_threat40|20|0.5000|0.0833|-0.4167|counter_edge_mostly_legacy_threat_artifact|
|counter40_vs_threat40|40|0.5833|0.1667|-0.4167|counter_edge_mostly_legacy_threat_artifact|
|counter60_vs_threat40|20|0.6667|0.0833|-0.5833|counter_edge_mostly_legacy_threat_artifact|
|counter60_vs_threat40|40|0.6667|0.1667|-0.5000|counter_edge_mostly_legacy_threat_artifact|
|counter60_vs_threat60|20|0.4167|0.0000|-0.4167|counter_edge_mostly_legacy_threat_artifact|
|counter60_vs_threat60|40|0.5833|0.0000|-0.5833|counter_edge_mostly_legacy_threat_artifact|

The counter-wall claim does not merely weaken under the guarded threat policy; it collapses in every tested size/life cell.  The old wins were overwhelmingly library-out wins against the threat shell.  Once `threat_closure` stops low-library Jace-zero and redundant Overlord draw bursts, the threat shell becomes the dominant side.

## Closure feature explanation

|size_axis|starting_life|legacy_threat_selfdeck_event_rate|closure_threat_selfdeck_event_rate|legacy_mean_jace_zero_actions|closure_mean_jace_zero_actions|legacy_threat_selfdeck_losses|closure_threat_selfdeck_losses|
|---|---|---|---|---|---|---|---|
|counter40_vs_threat40|20|0.1667|0.0000|2.2500|0.0000|5|0|
|counter40_vs_threat40|40|0.5833|0.0000|5.0833|0.0000|7|2|
|counter60_vs_threat40|20|0.2500|0.0000|3.0833|0.0000|7|1|
|counter60_vs_threat40|40|0.2500|0.0000|2.4167|0.0000|8|2|
|counter60_vs_threat60|20|0.2500|0.0000|10.3333|0.0000|5|0|
|counter60_vs_threat60|40|0.5000|0.0000|13.4167|0.0000|7|0|

The mechanism is visible at the feature level: `threat_closure` eliminates Jace-zero self-deck events in this panel and sharply reduces threat self-deck losses.  In the 60-vs-60 cells, the guarded threat side goes 12/12 at both life totals.

## Updated claim status

The historical `cf34_counter_wall` story should now be demoted again:

```text
old: counter-wall / Jace endurance edge
rev0061: mostly 60-card library buffer
rev0063: partly legacy threat_rush closure failure
rev0064: active counter-wall edge is not robust to guarded threat closure
```

The strongest current claim is not that counter-wall has discovered a reliable local strategic advantage.  It is that MUC-5's old threat baseline was exploitable because it overused public draw engines and under-planned lethal closure.

## Validation summary

```text
pytest: 214 passed
smoke: passed
closure-vs-counter games: 144
forensic reruns: 144
closure feature reruns: 144
truncations: 0
C++ chosen transitions: 37748
C++ mismatches/skips: 0 / 0
replay samples: 12 / 12 passed
```

## Next highest-risk work

The next experiment should stop treating `threat_closure` as merely an audit profile and build a small threat-policy ladder: legacy rush, guarded closure, less conservative closure, and maybe a counter-aware closure variant.  The risk is that rev0064's `threat_closure` may be too specifically tuned to avoid self-deck, so we need to test whether it remains strong against other non-inert opponents without losing pressure.
