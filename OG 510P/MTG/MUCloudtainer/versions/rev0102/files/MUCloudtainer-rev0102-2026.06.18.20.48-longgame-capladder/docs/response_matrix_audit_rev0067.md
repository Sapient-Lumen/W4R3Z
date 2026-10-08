# rev0067 response matrix audit

## Question

`counter_guard` survived rev0066's first pressure response.  The risk was that we had created a new fixed-pilot exploit: a counter policy that beats `threat_closure` and `threat_pressure`, but only because those threat policies remain too patient or too willing to let Counterspell/Force wars decide the game.

## Change

rev0067 adds `threat_surge`, a public-information-only threat profile.  It makes three targeted changes relative to `threat_pressure`:

1. Spend Counterspell/Force more aggressively in stack fights over Counterspell/Force targets.
2. Prefer safe player damage and minimal lethal attacks over long Jace-centric play.
3. Continue the library guards from `threat_closure`/`threat_pressure`, so the policy does not win by reverting to self-decking behavior.

No referee or simulator semantics changed.

## Experiment

The response matrix evaluates `counter_guard` as target against three threat baselines:

```text
library_aware_threat_closure_targetguarded
jace_pressure_threat_response
face_protect_threat_surge
```

Cells:

```text
counter40_vs_threat40
counter60_vs_threat40
counter60_vs_threat60
life 20 and life 40
```

The revision includes a primary sweep, a seed-disjoint stress sweep, and an extra focused 60-vs-60 deep sweep because the first pass suggested `threat_surge` might refute the 60-vs-60 counter rescue.

## Cumulative result

```text
counter40 vs threat40, life 20: closure 0.5000 | pressure 0.3750 | surge 0.5000
counter40 vs threat40, life 40: closure 0.6500 | pressure 0.6500 | surge 0.8000
counter60 vs threat40, life 20: closure 0.1250 | pressure 0.5000 | surge 0.6250
counter60 vs threat40, life 40: closure 0.6500 | pressure 0.7500 | surge 0.7500
counter60 vs threat60, life 20: closure 0.3333 | pressure 0.4444 | surge 0.5556
counter60 vs threat60, life 40: closure 0.5417 | pressure 0.8333 | surge 0.4167
```

## Interpretation

The cleanest statement is deliberately cautious:

```text
counter_guard remains a live response candidate.
threat_surge does not globally refute it.
60-vs-60 life-40 is the current best threat-side pressure point.
```

The strongest warning is that `threat_surge` was seed-sensitive.  It looked like a sharp refutation in the first 60-vs-60 pass, then backfired at life 20 in the deeper seed-disjoint pass.  Future work should avoid declaring a winner until the policies are tested in a broader response ladder or with a small policy-search layer.

## Gates

```text
response-matrix games: 348
forensic reruns: 348
closure feature reruns: 348
counter ownership audit games: 348
selected own-spell counters: 0
truncations: 0
C++ chosen transitions: 59,869
C++ mismatches/skips: 0 / 0
replay samples: 12 / 12 passed
pytest: 232 passed
```
