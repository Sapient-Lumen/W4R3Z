# Hierarchical FadeMem cache toy

Cheap multiscale-cache probe inspired by distance-aware memory consolidation: compress a long history into a fixed budget of intervals and ask whether dense-near / sparse-far summaries preserve recent fine detail plus old coarse anchors better than sliding windows or uniform blocks.

Run:

```bash
python experiments/hierarchical_fademem_cache/fademem_hierarchy_probe.py
```

Outputs:

- `artifacts/probe-results/REV0006_FADEMEM_HIERARCHY_SMOKE.json`
- `artifacts/probe-results/REV0006_FADEMEM_HIERARCHY_SMOKE.csv`
