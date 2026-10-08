# Proof obligation — rev0038

The local proof obligations added in rev0038:

```text
servicecontinuity must reject active withdrawals
servicecontinuity must reject replayed reports
servicecontinuity must reject duplicate branch reports unless explicitly allowed
servicecontinuity must reject quarantined branch reports
servicecontinuity must hold missing required branches
servicecontinuity must reject catalog/scope/request drift
servicecontinuity must not accept refusal-only or watch-only windows as healthy service
servicecontinuityfold must expose folded branchlet surfaces through code/tests/docs/public pointers/fold registry/surface ledger
```

Open obligations:

```text
persist continuity replay memory after restart
join continuity to real journal/checkpoint lanes
join continuity to SAM-shadow send windows
add catalog succession tests against live key-crisis branch outputs
add profile-GC join tests that use real checkpoint/journal artifacts
build larger repeated-round service continuity sweeps
```
