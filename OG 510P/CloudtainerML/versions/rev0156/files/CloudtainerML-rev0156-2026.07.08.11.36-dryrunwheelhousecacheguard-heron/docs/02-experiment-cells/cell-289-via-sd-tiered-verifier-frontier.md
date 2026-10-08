# CELL-289 — VIA-SD Tiered Verifier Frontier

Priority: **P1**  
Status: **runnable-native**

## Cheap first run
Run via_sd_tiered_verifier.cpp to map direct/slim/full verification thresholds.

## Linked idea
`IDEA-0287`

## Sources
- `SRC-0309`

## Metrics
- expected_cost
- mismatch_rate
- accept_rate
- speedup_proxy
- score

## Stop condition
Demote if slim tier wins only by hiding mismatch cost.

## Rev0027 note
Performance-first cell; security/trust side-wing is not driving this priority.
