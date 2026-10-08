# rev0065 counter-response audit — quarantine gate plus rescue stress

## Purpose

rev0064 proved that the historical `cf34_counter_wall` edge collapses when the Overlord opponent switches from legacy `threat_rush` to guarded `threat_closure`.  rev0065 asks the next risk-bearing question: is the counter-wall deck itself dead, or was the old counter pilot also stale once the threat pilot stopped self-decking?

This revision adds a public-information-only `counter_guard` profile and tests it against a fixed `threat_closure` opponent.  It also converts the rev0064 demotion into an executable claim-quarantine table so old `threat_rush`-dependent wins cannot be cited as current evidence without rerunning against a guarded threat baseline.

## Primary panel

```text
A: counter60 vs threat40, fixed threat_closure
B: counter40 vs threat40, fixed threat_closure
C: counter60 vs threat60, fixed threat_closure
counter policy axis: legacy CF34/ranker vs public counter_guard
life totals: 20 and 40
reps: 3 per seat/start/life/arm
primary terminal games: 144
```

|size_axis|starting_life|legacy_cf34_counter_score|public_counter_guard_score|guard_minus_legacy_counter_score_delta|provisional_read|
|---|---|---|---|---|---|
|counter40_vs_threat40|20|0.0833|0.5833|0.5000|counter_policy_improves_but_underpowered|
|counter40_vs_threat40|40|0.1667|0.3333|0.1667|mixed_or_underpowered|
|counter60_vs_threat40|20|0.0833|0.4167|0.3333|mixed_or_underpowered|
|counter60_vs_threat40|40|0.4167|0.8333|0.4167|counter_deck_rescue_candidate|
|counter60_vs_threat60|20|0.0833|0.6667|0.5833|counter_deck_rescue_candidate|
|counter60_vs_threat60|40|0.1667|0.4167|0.2500|mixed_or_underpowered|

The result is materially different from rev0064.  `counter_guard` improves every tested cell, and two primary cells become counter-deck rescue candidates: `counter60_vs_threat40` at life 40 and `counter60_vs_threat60` at life 20.  The 40-vs-40 life-20 cell is not a clean rescue, but it does move from near-dead to competitive.

## Seed-disjoint stress pass

Because the primary panel has only 12 games per cell, rev0065 expands the three promising cells on disjoint seeds:

```text
counter40_vs_threat40, life 20
counter60_vs_threat40, life 40
counter60_vs_threat60, life 20
stress reps: 4 per seat/start/policy/cell
stress terminal games: 96
```

|size_axis|starting_life|legacy_cf34_counter_score|public_counter_guard_score|guard_minus_legacy_counter_score_delta|provisional_read|
|---|---|---|---|---|---|
|counter40_vs_threat40|20|0.3750|0.5625|0.1875|counter_policy_improves_but_underpowered|
|counter60_vs_threat40|40|0.4375|0.6875|0.2500|counter_deck_rescue_candidate|
|counter60_vs_threat60|20|0.0625|0.6875|0.6250|counter_deck_rescue_candidate|

The stress pass supports the rescue signal in the two strongest cells and keeps the 40-vs-40 life-20 cell in partial-rescue territory.  That means rev0064's claim demotion was correct for the old CF34/ranker pilot, but too strong if read as “the counter-wall deck has no response.”  The better current label is:

```text
old claim: CF34 counter-wall beats legacy threat_rush
rev0064 status: old claim quarantined under guarded threat_closure
rev0065 candidate: public counter_guard can rescue selected counter-wall cells against guarded threat_closure
```

## Claim quarantine output

|size_axis|starting_life|historical_legacy_threat_score|guarded_threat_score|public_counter_guard_score_against_guarded_threat|quarantine_status|counter_response_status|
|---|---|---|---|---|---|---|
|counter40_vs_threat40|20|0.5000|0.0833|0.5833|quarantined_old_edge_threat_baseline_artifact|partial_counter_guard_rescue|
|counter40_vs_threat40|40|0.5833|0.1667|0.3333|quarantined_old_edge_threat_baseline_artifact|no_current_counter_guard_rescue|
|counter60_vs_threat40|20|0.6667|0.0833|0.4167|quarantined_old_edge_threat_baseline_artifact|no_current_counter_guard_rescue|
|counter60_vs_threat40|40|0.6667|0.1667|0.8333|quarantined_old_edge_threat_baseline_artifact|counter_guard_rescue_candidate|
|counter60_vs_threat60|20|0.4167|0.0000|0.6667|quarantined_old_edge_threat_baseline_artifact|counter_guard_rescue_candidate|
|counter60_vs_threat60|40|0.5833|0.0000|0.4167|quarantined_old_edge_threat_baseline_artifact|no_current_counter_guard_rescue|

Every historical counter-wall cell remains quarantined because the old edge was measured against `threat_rush`, not `threat_closure`.  The quarantine does not say “counter is impossible.”  It says old evidence is not current evidence, and any future citation must name the threat baseline and use the live guarded-threat results.

## Mechanism read

The `counter_guard` improvement comes from fixing obvious counter-side leaks rather than changing rules: it avoids low-library Brainstorm, treats Jace as tempo/ultimate pressure, counters Overlord/Jace as the public priority, is less eager to Force away its own interaction, and guards against self-decking Overlord attacks.  It remains public-information-only.

Most `counter_guard` wins are still library-out wins, not fast life-total wins.  The candidate is therefore a guarded endurance response, not a proof of a proactive counter kill.

## Validation summary

```text
pytest: 223 passed
smoke: passed
primary counter-response games: 144
stress counter-response games: 96
forensic reruns: 240
closure feature reruns: 240
truncations: 0
C++ chosen transitions: 50254
C++ mismatches/skips: 0 / 0
replay samples: 12 / 12 passed
```

## Next highest-risk work

The next substantive risk is overfitting the new `counter_guard` to the current `threat_closure`.  The next revision should build a small threat-policy ladder: current closure, less-conservative closure, counter-aware closure, and maybe a no-Jace threat closure.  The goal is to learn whether `counter_guard` found a robust counter response or merely the next exploit in the policy ladder.
