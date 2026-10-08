# Rev0010 audit/refactor notes

## Added refactor tools

- `tools/primary_metric_patcher.py` patches older probe JSON summaries with dashboard-facing `summary.primary_metric` annotations while preserving row data.
- `tools/probe_graph_specs.py` emits graph-plan JSON/CSV/Markdown/HTML so future dashboards know which facets and metrics to plot.

## Added runnable probes

- `experiments/evidence_aligned_ttt/ease_ttt_probe.py`
- `experiments/parametric_kv_memory/parametric_kv_probe.py`
- `experiments/still_compactor/still_compactor_probe.py`
- `experiments/smt_transition_training/smt_transition_probe.py`

## Cleanup queue

- The SMT probe currently has an exact-feature upper-ish supervised updater; next pass should add a harder teacher/noisy-label setting.
- The Still compactor needs a sweep where latent slots are trained/learned rather than deterministic random anchors.
- The parametric-KV toy should separate encode-time and decode-time adapter effects.
- Evidence-aligned adaptation should get adversarial target-noise sweeps.
