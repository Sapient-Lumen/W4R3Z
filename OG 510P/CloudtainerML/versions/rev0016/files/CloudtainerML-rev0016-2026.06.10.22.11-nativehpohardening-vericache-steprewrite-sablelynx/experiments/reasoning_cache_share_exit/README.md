# Reasoning cache sharing + early exit probe

Tiny synthetic test for multi-branch reasoning pipelines. It asks whether hidden
similarity can safely generalize exact prefix cache reuse and whether confidence
or entropy stabilization can stop verification early without trusting near-miss
or high-confidence wrong branches.

Run:

```bash
python experiments/reasoning_cache_share_exit/rksc_probe.py
```
