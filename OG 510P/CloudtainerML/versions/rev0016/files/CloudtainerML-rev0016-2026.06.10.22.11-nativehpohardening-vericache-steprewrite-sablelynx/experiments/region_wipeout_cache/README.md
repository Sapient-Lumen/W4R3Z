# Region-wipeout cache retention probe

Symbolic/tensor proxy for cache compression policies that compete token-by-token versus policies that allocate budget by reasoning region.

Run:

```bash
python experiments/region_wipeout_cache/region_wipeout_probe.py --quick --out artifacts/probe-results/REV0004_REGION_WIPEOUT_SMOKE.json --csv artifacts/probe-results/REV0004_REGION_WIPEOUT_SMOKE.csv
```

Success means every required region retained at least one vital token. This is not a real LLM cache implementation; it is a cheap falsifier for the geometry of the failure mode.
