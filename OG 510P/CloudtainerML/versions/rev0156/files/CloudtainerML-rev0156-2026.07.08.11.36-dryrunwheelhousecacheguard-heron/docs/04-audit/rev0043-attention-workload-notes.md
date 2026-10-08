# rev0043 attention workload notes

## What changed

`experiments/attention_row_compiler_benchmark/attention_row_compiler_benchmark.py` adds QK-derived rows with dense `softmax(scores) @ V` as the reference output. Sparse compilers now produce their own `softmax(scores[selected]) @ V` output and are scored by output cosine, relative L2 error, mass retained, value reads, QK dot products, and Python selector timing.

## Main finding

Exact Top-K is no longer sufficient evidence. In the current workload, `exact_topk_sparse` has mean Top-K hit rate 1.0, but mean retained dense attention mass is 0.211 and mean relative output L2 error is 2.956.

`top_p_0p95` preserves output much better, with mean mass 0.950 and mean output cosine 0.998, but it selects 758.7 tokens on average out of 1024. That is a quality baseline, not a strong sparse win.

## Consequence

The next viable compiler must be mass-aware or output-aware. GVR-style exact Top-K certification may still be useful, but only as one guard inside a broader attention-output contract.
