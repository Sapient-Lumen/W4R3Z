# CELL-032 — L1 Sliding Window + L2 Tensor Cache Toy

Priority: **P0**  
Status: `candidate`  
Idea: `IDEA-0032`  
Sources: SRC-0078, SRC-0007

## Question

Can evicted local-cache tokens be summarized into an outer-product memory that rescues retrieval without growing linearly?

## Cheap first run

Modify spectral associative recall to evict old keys from L1 and write them into outer-product L2 memory.

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
- L1_L2_gate_sweep
- capacity_boundary

## Stop condition

If L2 only wins with near-full-rank memory, keep as diagnostic.


## Runnable rev0005 scaffold

- Script: `experiments/tensor_cache_l2/tensor_cache_probe.py`
- Smoke output: `artifacts/probe-results/REV0005_TENSOR_CACHE_L2_SMOKE.json`
