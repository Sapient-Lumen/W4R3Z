# rev0054 Matchup Claim Results

The rev0054 dossier ran 160 terminal-clean games for `cf34_counter_wall` versus `pub_threat_overlord`.

## Result

```text
games:                     160
life 20 games:              80
life 40 games:              80
truncations:                 0
replay samples:          8 / 8 passed
C++ shadow transitions: 45,316
C++ skipped:                 0
C++ mismatches:              0
```

Target-perspective score:

```text
life 20: 0.600
life 40: 0.800
average: 0.700
total score LCB 95: 0.5926
life delta high-minus-low: +0.200
```

The previous rev0053 result was positive at both life totals but looked relatively stable.  rev0054 still supports the matchup as positive overall, but it now looks life-sensitive: the target is much stronger at 40 life than 20 life in this sample.

## Interpretation

This is a meaningful upgrade from “watch cell” to a claim-candidate dossier, but not a final theorem.  The most honest label is:

```text
life_sensitive_matchup_claim_candidate
```

That means:

- the total terminal-clean signal is positive,
- both life totals remain nonnegative/positive on mean score,
- 40 life appears materially better for the target in this sample,
- future claim work should split by life total rather than report only an all-life average.

No gameplay policy is promoted in rev0054.
