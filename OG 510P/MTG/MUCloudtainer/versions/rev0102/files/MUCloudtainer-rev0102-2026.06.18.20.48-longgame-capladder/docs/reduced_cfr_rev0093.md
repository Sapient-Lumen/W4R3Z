# rev0093 reduced CFR calibration

**Revision:** rev0093 (`cfrcalibrator-supportrefactor`)  
**Status:** executable calibration subgame, not a full MUC-5 solve.

## Why this exists

rev0092 restarted the original method roadmap by making PSRO executable. The riskiest remaining method gap was that CFR/search had no independent extensive-form reference. Without one, the empirical PSRO loop could keep expanding a population while still lacking an equilibrium sanity check for imperfect-information semantics.

rev0093 adds the first tabular CFR reference. It deliberately solves a small game, not the full simulator. The value is that the small game is independently represented and preserves the exact semantics most likely to break learning:

- Jace +2 gives player 0 private top-card knowledge.
- The leave/bottom choice is public without revealing the card identity.
- Force of Will's pitch identity becomes public if Force is used.
- Waiting can favor the controller through closure only when the top-card situation is safe.
- Best response is grouped by information set, so exploitability cannot be measured by cheating at concrete hidden states.

## Game sketch

Player 0 is the control/Jace/Force player. Player 1 is the pressure player.

Chance deals:

```text
player 1 top card: threat 0.55, blank 0.45
player 0 Force resource: none 0.45, Force+Island pitch 0.35, Force+Jace pitch 0.20
```

The sequence is:

```text
P0: hold counter or use Jace +2
if Jace: P0 privately sees top, then publicly leaves or bottoms it
P1: cast threat or wait
if cast: P0 declines, counters, or Forces when legal
if Force: P1 sees the pitched card and chooses stop or press again
terminal payoff to P0 reflects closure, resolved pressure, countering, or Force resource loss
```

This is intentionally small enough for deterministic tabular CFR and explicit exploitability checks.

## Result

`PYTHONPATH=. python scripts/run_rev0093_reduced_cfr.py` trains vanilla tabular CFR for 5,000 iterations and writes:

- `data/rev0093_reduced_cfr_summary.json`
- `data/rev0093_reduced_cfr_audit.json`
- `data/rev0093_reduced_cfr_convergence.csv`
- `data/rev0093_reduced_cfr_strategy.csv`

Final audit values:

```text
chance deals: 6
information sets: 33
initial exploitability: 0.029747317090571955
final exploitability: 0.000006188374239561936
reduction factor: 4806.968024073107
```

The qualitative average policy is also useful: with no Force or a Force that pitches Jace, the controller almost always holds counter mana; with Force+Island, the controller nearly always uses Jace. That is exactly the kind of policy distinction that a memoryless snapshot interface would make hard to validate.

## Audit/refactor lesson

The first draft of the best-response evaluator used a concrete-state shortcut: maximize separately at each hidden state. That is invalid in imperfect-information games because it lets the best response peek through information sets. rev0093's evaluator now collects all states in each responding-player information set using chance/opponent reach weights and selects one shared action for the whole information set.

This matters because exploitability is only meaningful if the measuring tool obeys the same information boundary as the policy being measured.

## How this changes the roadmap

The CFR branch is no longer purely aspirational. The right next CFR/search step is not full-game Deep CFR. It is to expand this reduced reference only when a specific missing mechanism is needed by PSRO or by a neural/evolutionary oracle comparison.

rev0093 therefore clears the method architecture for two parallel tracks:

1. continue PSRO response-oracle rounds against the empirical simulator;
2. keep the reduced CFR reference small and use it to catch information-state and exploitability mistakes before scaling.
