# rev0073 population pool robustness

rev0073 addresses the main scientific risk left after rev0071: the pooled population floor might have been a convenient aggregate that hid a fragile size, life-total, or source-revision effect.

The change is executable rather than doctrinal.  The current empirical game has two row policies and three threat columns, so rev0073 replaces the promotion-gate mixed-security calculation with an exact two-row maximin solver.  Fictitious play remains available only as a fallback for games with more than two row policies.

The robustness runner reuses the seed-disjoint rev0069 and rev0070 population panels and recomputes weighted confidence intervals for fifteen cuts:

- all source rows pooled;
- each source revision alone and each leave-one-source complement;
- each size axis alone and each leave-one-size complement;
- each starting life alone and each leave-one-life complement.

Results:

```text
evaluation cuts:                 15
gate rows:                       15
exact solver gate rows:          15 / 15
promotable cells:                 0
quarantined low-floor cells:     15
precision-blocked cells:          0
underpowered cells:               0
minimum games per cell:          24
max CI width:                     0.5544426220774892
worst conservative LCB:           0.014445355627922152
best conservative LCB:            0.29827953478001323
```

The important result is negative but stronger than rev0071: every tested pooling cut has enough games under the preregistered threshold, uses exact 2-row mixed-security math, and still fails on conservative security floor rather than on precision.  The weakest cut is `size_axis_only=counter60_vs_threat60`, with conservative pure-security LCB about 0.0144.

Primary artifacts:

```text
scripts/run_rev0073_pool_robustness.py
data/rev0073_population_pool_robustness_summary.json
data/rev0073_population_pool_robustness_gate.csv
data/rev0073_population_pool_robustness_security.csv
data/rev0073_population_pool_robustness_pooled_arm_summary.csv
```
