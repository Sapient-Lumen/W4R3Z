# simulator rev0030

rev0030 does not change card rules. It changes measurement and learning surfaces:

```text
opening-hand counterfactual branch rollouts are repeated
first-look counterfactual mulligan policy can be trained from mean branch deltas
no-choice forced-action runs now have start/end fingerprints
```

Rules authority remains Python. C++ remains a shadow/parity path.

New simulator-adjacent outputs:

```text
rev0030_repeated_opening_counterfactual_*.csv/json
rev0030_nochoice_segment_*.csv/json
```

All new payoff traffic passed replay and C++ trace checks in the archived run.
