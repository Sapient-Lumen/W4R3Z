# Tensor Cache L1/L2 Probe

A small associative recall simulator for the Tensor Cache idea: recent tokens stay
in an L1 sliding window; evicted tokens are written into an L2 outer-product
memory.  It compares full attention, sliding window, per-token L2 writes,
normalized L2 writes, and an intentionally lossy chunk-mean shortcut.

Run:

```bash
python experiments/tensor_cache_l2/tensor_cache_probe.py --outdir artifacts/probe-results
```
