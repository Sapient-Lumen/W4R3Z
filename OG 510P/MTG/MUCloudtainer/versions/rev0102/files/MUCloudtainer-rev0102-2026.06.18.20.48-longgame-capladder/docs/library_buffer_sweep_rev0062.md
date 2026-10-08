# rev0062 library-buffer legal-size sweep

## Why this revision exists

rev0061 found that an inert 60-Island deck can be competitive against the original 40-card Overlord threat shell. That was dangerous because it meant the old `cf34_counter_wall` story might be overexplaining a passive library-size artifact as if it were Jace/Counterspell strategy.

rev0062 therefore runs a focused legal-size control panel. It does **not** broaden MUC-5 deck legality beyond 40/60. Instead, it compares inert and active targets at legal 40/60 sizes against both the original 40-card threat shell and a deterministic 60-card scaled threat shell.

## Panel

```text
A_counter60_vs_threat40   original 60-card counter-wall vs original 40-card threat
K_buffer40_vs_threat40    all-Island 40 vs original 40-card threat
J_buffer60_vs_threat40    all-Island 60 vs original 40-card threat
L_buffer60_vs_threat60    all-Island 60 vs scaled 60-card threat
M_counter40_vs_threat40   scaled 40-card counter-wall vs original 40-card threat
N_counter60_vs_threat60   original 60-card counter-wall vs scaled 60-card threat
O_buffer40_vs_threat60    all-Island 40 vs scaled 60-card threat
```

Run size:

```text
games:                 168
forensic reruns:       168
truncations:             0
C++ chosen transitions: 39,887
C++ mismatches/skips:    0 / 0
replay samples:        12 / 12 passed
```

## Main scores

Target-perspective score, draw-half reporting:

```text
life 20:
  A counter60 vs threat40: 0.7500
  K buffer40  vs threat40: 0.3333
  J buffer60  vs threat40: 0.5000
  L buffer60  vs threat60: 0.2500
  M counter40 vs threat40: 0.8333
  N counter60 vs threat60: 0.5000
  O buffer40  vs threat60: 0.0833

life 40:
  A counter60 vs threat40: 0.8333
  K buffer40  vs threat40: 1.0000
  J buffer60  vs threat40: 0.8333
  L buffer60  vs threat60: 0.3333
  M counter40 vs threat40: 0.5000
  N counter60 vs threat60: 0.5000
  O buffer40  vs threat60: 0.3333
```

## Interpretation

The claim is now sharper and less flattering.

At **life 20**, the active shell still matters. The scaled 40-card counter-wall analogue beats the original 40-card threat shell more clearly than all-Island 40 does, and all-Island 60 drops when the opponent is normalized to 60 cards. So life 20 is not merely an all-Island waiting-room artifact.

At **life 40**, the original 40-card threat shell has a closure pathology: even all-Island 40 beats it in this panel. That means the life-40 `cf34_counter_wall` edge should no longer be interpreted as evidence of counter-wall skill. It is better read as the threat shell failing to convert pressure before self-decking.

The cleanest current label is:

```text
life 20: active counter-wall/control components plus library-buffer pressure
life 40: opponent closure/self-deck pathology dominates; all-Island controls can win
```

## Forensic signal

The forensic pass reinforces that library trajectory is central:

```text
life 20 mean final target library buffer:
  buffer40 vs threat40:  +23.83
  buffer60 vs threat40:  +40.42
  buffer60 vs threat60:  +25.25
  counter40 vs threat40:  +8.08
  counter60 vs threat60:  -4.00

life 40 mean final target library buffer:
  buffer40 vs threat40:  +24.17
  buffer60 vs threat40:  +45.67
  buffer60 vs threat60:  +33.58
  counter40 vs threat40:  -0.75
  counter60 vs threat60:  +5.58
```

The score is not identical to final library buffer because life-total losses still occur, especially when the target is inert and the threat shell draws enough pressure. But all target wins by all-Island arms are library-out wins.

## Consequence for the mission

The correct next high-risk target is not another deck/pilot sweep. It is a threat-closure audit: why the current `threat_rush` / Overlord shell often fails to kill an inert opponent before self-decking, especially at life 40. Until that is understood, life-40 “strategy” claims around this shell should carry a warning label.
