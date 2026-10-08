# Probe: value-outlier eviction

Runnable: `experiments/value_outlier_eviction/value_outlier_probe.py`

Question: can value-norm protection plus diversity sampling retain critical low-attention tokens better than attention top-k?

Policies:

- `attention_topk`
- `value_norm_topk`
- `stochastic_attention`
- `diverse_segment_topk`
- `vase_toy`
- `critical_oracle`

Primary metrics: critical retention rate and critical segment coverage.

Escalation: instrument tiny transformer V activations and ablate/prune actual value outliers.
