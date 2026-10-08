# Branch cache sharing probe

Synthetic RKSC/ASKS-style probe. It generates multi-branch reasoning prefixes with hidden summaries and true KV caches, then tests whether cosine-based sharing saves cache computation without corrupting attention outputs.

Run:

```bash
python experiments/branch_cache_sharing/branch_cache_sharing_probe.py --out artifacts/probe-results/REV0006_BRANCH_CACHE_SHARING_SMOKE
```
