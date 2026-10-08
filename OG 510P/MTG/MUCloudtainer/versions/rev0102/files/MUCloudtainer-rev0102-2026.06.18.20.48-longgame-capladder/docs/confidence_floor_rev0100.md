# rev0100 confidence floor audit

rev0100 addresses a measurement ambiguity created by the otherwise useful rev0099 expanded-matrix refresh.

The rev0099 strategy summary reported the admitted PSRO response's `pure_floor_vs_population` as `0.5`. That value was technically correct for a square matrix row, but misleading as opponent evidence: the floor came from the self diagonal, not from an incumbent challenger.

## What changed

rev0100 adds executable helpers in `src/muc5/confidence_floor.py` and a runner in `scripts/run_rev0100_confidence_floor.py` that separate:

- the matrix self diagonal convention used for constant-sum solving;
- the floor against non-self incumbent opponents;
- a higher-resolution confidence floor against each incumbent;
- a self-control diagnostic.

This is an audit/refactor of the empirical-game measurement layer. It is not a strategic promotion.

## Configuration

The admitted response is still:

```text
oracle_map_08_60_mixed_threats_counter_wall
```

Each focal pair uses the shared balanced evaluation design:

```text
life totals: 20 and 40
repetitions per life/seat/start cell: 30
games per pair: 240
incumbent opponents: 8
self-control pair: 1
total game rows: 2,160
max decisions: 700
```

All rows record physical orientation, starting player, focal player, life total, repetition, seed, score, terminal reason, and truncation status.

## Main result

The rev0099 matrix self-floor comparison is:

```text
floor including self diagonal:      0.5
floor excluding self diagonal:      0.6625
self-diagonal floor gap:            0.1625
```

The new high-resolution incumbent confidence audit reports:

```text
minimum incumbent mean:             0.6625
minimum incumbent 95% CI lower:     0.6025503087483217
weakest incumbent by mean/CI:       pub_threat60_closure
truncations:                        0
confidence floor over 0.5:          true
```

The self-control diagnostic is deliberately separate:

```text
self-control mean:                  0.4875
self-control 95% CI:                [0.4241288824813318, 0.5508711175186681]
```

That self-control result is compatible with the 0.5 diagonal convention. It is not opponent evidence.

## Interpretation

The current admitted PSRO response is now harder to dismiss as a low-resolution matrix artifact against the original eight-strategy response ecology: at 240 balanced rows per incumbent, its weakest lower confidence bound is above 0.5.

This still does **not** mean the answer is solved. The audit only covers the fixed incumbent population. It does not prove robustness against a future generative response oracle, full deck space, alternate pilots, reduced-game equilibrium transfer, or independent semantic changes.

The right next target is a third-oracle or full-population stress loop that treats this response as a stronger incumbent, not as a final strategic answer.
