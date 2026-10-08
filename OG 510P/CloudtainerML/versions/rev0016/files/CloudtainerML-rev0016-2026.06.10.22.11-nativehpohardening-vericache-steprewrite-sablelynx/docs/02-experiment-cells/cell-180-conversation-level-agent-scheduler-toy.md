# CELL-180: Conversation-Level Agent Scheduler Toy

Priority: P1

Status: candidate

Idea: IDEA-0179

Source: SRC-0215

Cheap first run: No runnable probe yet; multi-turn prefill/decode placement cost model.

Metrics:
- TTFET proxy
- energy proxy
- KV transfer volume
- scheduler regret

Baselines:
- per-turn predictor
- conversation observation
- oracle

Stop condition: If observation only wins under smooth traces, demote.
