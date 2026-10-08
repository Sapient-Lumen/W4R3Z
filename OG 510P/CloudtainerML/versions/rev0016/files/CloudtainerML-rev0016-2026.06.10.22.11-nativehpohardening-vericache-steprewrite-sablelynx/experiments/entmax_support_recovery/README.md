# Entmax Support-Recovery Probe

A tensor-only page-selection simulator inspired by EntmaxKV.  It uses sparsemax
as the simplest exact-zero attention family and evaluates whether page-selection
policies recover the true support before loading all pages.

Run:

```bash
python experiments/entmax_support_recovery/entmax_support_probe.py --outdir artifacts/probe-results
```
