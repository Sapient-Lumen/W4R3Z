# Probe: dormant-token sponsorship

Runnable: `experiments/dormant_sponsorship/dormant_sponsorship_probe.py`

Question: can score-only cache retention preserve values that are structurally important but attention-dormant until the final query?

Policies:

- `attention_topk`
- `recency_topk`
- `anchor_only`
- `semantic_sponsor`
- `oracle_target`

Primary metric: target value retention rate.

Escalation: train a tiny copy/retrieval transformer with anchor/value pairs and prune actual KV cache during pseudo-decode.
