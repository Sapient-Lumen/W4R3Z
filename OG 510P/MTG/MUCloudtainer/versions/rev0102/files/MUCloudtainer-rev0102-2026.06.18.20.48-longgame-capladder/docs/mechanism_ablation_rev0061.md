# rev0061 mechanism ablation: Jace, Counterspell, and passive buffer

rev0061 tests the riskiest remaining causal ambiguity in the `cf34_counter_wall` result: whether the edge is driven by active Jace/Brainstorm and dense Counterspell play, or by the passive 60-vs-40 library-size asymmetry causing the 40-card Overlord shell to deck itself.

The panel is seed-disjoint from the prior rev0058-rev0060 focused evidence and uses the same terminal-clean, public-agent, C++ chosen-transition shadow discipline.

## Arms

```text
A_original_size_skew
  60-card counter-wall/Jace shell vs 40-card Overlord threat shell.

G_target_no_jace60
  Same target shell, but all five Jace copies are replaced by Islands.

H_target_no_counterspell60
  Same target shell, but all sixteen Counterspell copies are replaced by Islands.

I_target_no_jace_no_counterspell60
  Jace and Counterspell both removed; Force and the singleton Overlord remain.

J_target_all_island60
  60 Islands only.  This isolates passive library-size pressure.
```

Each arm has 24 games per life total: two target seats × two starting players × six reps.

## Main result

```text
life 20 target score:
  A original:                   0.7083
  G no Jace:                    0.5417
  H no Counterspell:            0.6250
  I no Jace/no Counterspell:    0.5833
  J all-Island buffer only:     0.5833

life 40 target score:
  A original:                   0.8750
  G no Jace:                    0.8333
  H no Counterspell:            0.8750
  I no Jace/no Counterspell:    0.6667
  J all-Island buffer only:     0.7083
```

The surprise is the all-Island arm.  A deck with no Jace, no Counterspell, no Force, and no Overlord still wins 14/24 at life 20 and 17/24 at life 40, always by opponent library-out when it wins.  That does not mean the original shell is fake, but it sharply demotes the active-mechanism story.

## Current interpretation

The best current claim is:

```text
The replicated cf34_counter_wall edge is primarily a passive deck-size / opponent self-decking exploit in this MUC-5 local setup.
Jace and Counterspell improve or stabilize some cells, especially life 20, but neither is necessary for a positive edge against pub_threat_overlord.
```

The phrase “counter-wall endurance shell” should be treated as too flattering unless it is explicitly qualified.  A more honest label is “60-card library-buffer exploit against a 40-card threat shell.”

## Validation

```text
games: 240
terminal games: 240
truncations: 0
C++ chosen transitions checked: 52,438
C++ mismatches/skips: 0 / 0
forensic reruns: 240
forensic validation errors: 0
replay samples: 10 / 10 passed
```

The run ships compact transition samples and forensic features, not raw full transition CSVs.
