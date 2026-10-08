# Tensor Cache L1/L2 probe

Code: `experiments/tensor_cache_l2/tensor_cache_probe.py`

Inspired by L1 sliding-window + L2 outer-product associative memory. The probe asks whether evicted facts can be recovered from a fixed matrix memory and whether chunk-mean writes produce spurious cross-token products.

Run:

```bash
python experiments/tensor_cache_l2/tensor_cache_probe.py \
  --out artifacts/probe-results/REV0005_TENSOR_CACHE_L2_SMOKE.json \
  --csv artifacts/probe-results/REV0005_TENSOR_CACHE_L2_SMOKE.csv
```

Key outputs: retrieval accuracy, cosine/error versus full attention, target rank.
