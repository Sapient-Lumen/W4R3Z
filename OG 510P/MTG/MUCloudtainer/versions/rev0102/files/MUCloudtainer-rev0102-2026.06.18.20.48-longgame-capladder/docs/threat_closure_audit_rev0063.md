# rev0063 threat-closure audit — overdrawfix

## Why this revision exists

rev0062 made the central MUC-5 claim riskier, not cleaner: all-Island controls could beat the 40-card Overlord threat shell, especially at life 40.  That raised a concrete concern that the historical `cf34_counter_wall` edge was not only a library-size artifact, but also an opponent-pilot closure failure.

rev0063 tests that failure directly.  It keeps simulator rules unchanged and compares the legacy public `threat_rush` pilot with a new public-information-only `threat_closure` pilot that is aware of its own library count, avoids Jace-zero/Overlord overdraw, avoids redundant Overlord casts when current attackers can close, and prefers the smallest attack packet that survives Overlord attack-trigger draws.

The focus score in this audit is the inert all-Island target score.  Lower target score means the threat shell closes better.

## Panel

```text
P/Q: threat40 legacy/closure vs buffer40
P/Q: threat40 legacy/closure vs buffer60
R/S: threat60 legacy/closure vs buffer40
life totals: 20 and 40
seats/start players/reps: both seats, both starting players, 3 reps
terminal games: 144
```

## Result summary

```text
buffer40 vs threat40, life 20:
  legacy inert target score:  0.4167
  guarded inert target score: 0.0833
  delta:                    -0.3333

buffer40 vs threat40, life 40:
  legacy inert target score:  0.8333
  guarded inert target score: 0.2500
  delta:                    -0.5833

buffer40 vs threat60, life 20:
  legacy inert target score:  0.1667
  guarded inert target score: 0.0000
  delta:                    -0.1667

buffer40 vs threat60, life 40:
  legacy inert target score:  0.5833
  guarded inert target score: 0.0000
  delta:                    -0.5833

buffer60 vs threat40, life 20:
  legacy inert target score:  0.3333
  guarded inert target score: 0.0833
  delta:                    -0.2500

buffer60 vs threat40, life 40:
  legacy inert target score:  1.0000
  guarded inert target score: 0.3333
  delta:                    -0.6667
```

## Mechanism

The legacy threat pilot repeatedly spent its library on Jace zero and excess Overlord draw bursts while failing to convert damage fast enough.  The guarded pilot removed Jace-zero draw entirely in this panel, increased face-attack pressure, and reduced inert-control wins in every size/life cell.

```text
legacy threat_rush vs buffer40/threat40/life40:
  inert target score:           0.8333
  mean Jace-zero activations:   1.25
  threat self-deck losses:     10 / 12
  mean attackers to player:     5.17

threat_closure vs buffer40/threat40/life40:
  inert target score:           0.2500
  mean Jace-zero activations:   0.00
  threat self-deck losses:      3 / 12
  mean attackers to player:     5.83
```

The 60-card threat control is stronger evidence that this is a closure failure, not merely deck legality.  Against buffer40 at life40, the guarded threat60 pilot swept the cell 12-0 while the legacy threat60 pilot still gave the inert target a 0.5833 score.

## Interpretation change

rev0062's warning label remains correct but should now be sharper:

```text
old warning: life-40 claims are confounded by threat-shell self-deck pathology.
new warning: a large share of that pathology is pilot-level overdraw / under-closure, especially legacy threat_rush Jace-zero usage and redundant threat deployment.
```

The guarded pilot is not a promoted strategy.  It is an audit instrument and a candidate baseline.  The next scientific step is to rerun the active counter-wall controls against `threat_closure`; if the counter-wall edge collapses, much of the historical claim was opponent-pilot pathology.  If it survives, then there is still an active control-shell phenomenon worth isolating.
