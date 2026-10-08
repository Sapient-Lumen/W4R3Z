# rev0077 adaptive pooling guard

rev0077 closes a sampling-design leak in the population work.

rev0069 and rev0070 are complete seed-disjoint population panels. rev0075 is not another generic panel: it is a targeted challenge selected after inspecting high-point, underpowered strata. It is valid evidence for those selected strata, but it must not silently enter broad pooled promotion gates as though it were an unbiased population sample.

The new guard classifies every population summary row by sampling frame:

- `complete_population_panel`: eligible for broad pooled promotion gates.
- `targeted_stratum_challenge`: retained for selected-stratum stress, excluded from broad pooled promotion gates.
- `unknown_sampling_frame`: fail-closed, excluded.

Observed split:

```text
summary rows total:               90
eligible complete-panel rows:     72
excluded targeted challenge rows: 18
eligible summary game rows:       432
excluded summary game rows:       288
unknown sampling rows:            0
```

Guarded broad-pool result, using only rev0069+rev0070 complete panels:

```text
gate rows:                 1
gate passed cells:         0
status:                    quarantined_low_security_floor
conservative LCB:          0.29827953478001323
mean pure security floor:  0.4583333333333333
max CI width:              0.3201075971066403
```

Naively adding rev0075 as if it were another complete panel would still not promote, but it would materially move the broad global result:

```text
naive conservative LCB:          0.4343561940744842
naive mean pure security floor:  0.5583333333333333
LCB delta vs guarded pool:       +0.136076659294471
mean-floor delta vs guarded:     +0.10000000000000003
```

The read is substantive: `public_counter_guard` remains quarantined, and the cube now prevents post-hoc challenge data from making broad security floors look better than the preregistered panels justify.
