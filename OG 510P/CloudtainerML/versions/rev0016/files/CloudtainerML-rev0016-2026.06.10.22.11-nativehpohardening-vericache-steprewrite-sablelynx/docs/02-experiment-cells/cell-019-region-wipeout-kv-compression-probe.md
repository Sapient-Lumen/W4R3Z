# CELL-019 — Region-Wipeout KV Compression Probe

Priority: **P0**
Status: `candidate`

## Cheapest first run

Generate traces with vital contiguous blocks and distractor high-attention spikes; sweep budget and retention policy.

## Baselines

- random or identity baseline
- strong simple heuristic
- matched-budget architecture baseline

## Metrics

- accuracy/exact match
- loss/error
- memory bytes
- runtime
- failure mode count
- seed variance

## Stop condition

If segment quotas do not help under any synthetic region-wipeout setting, merge into generic eviction tests.

## Source ids

SRC-0061
