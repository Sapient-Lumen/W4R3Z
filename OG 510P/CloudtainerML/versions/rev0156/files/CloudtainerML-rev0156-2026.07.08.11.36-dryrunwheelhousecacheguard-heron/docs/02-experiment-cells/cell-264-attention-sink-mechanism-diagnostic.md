# CELL-264 — Attention Sink Mechanism Diagnostic

Priority: **P1**  
Status: `runnable-native`  
Sources: SRC-0291

## Question

Can a tiny diagnostic distinguish NOP/trash-can sinks from broadcast sinks before choosing gates or registers?

## Cheap first run

Run `experiments/attention_sink_mechanism/attention_sink_probe.cpp` and compare gate/register interventions under NOP-vs-broadcast mechanisms.

## Metrics

- `score`
- `diagnostic_f1`
- `task_error`
- `overhead`

## Required baselines

- `no_intervention`
- `sink_gate_only`
- `register_tokens_only`
- `gate_plus_register`
- `oracle_mechanism_switch`

## Stop condition

Keep if diagnostics pick different interventions for NOP and broadcast regimes.
