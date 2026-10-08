# CELL-174: LRKV Head-Diversity Capacity Probe

Priority: P0

Status: runnable

Idea: IDEA-0173

Source: SRC-0097

Cheap first run: experiments/lrkv_head_diversity/lrkv_head_diversity.cpp emits REV0014_LRKV_HEAD_DIVERSITY_SMOKE.json.

Metrics:
- MSE
- bytes ratio
- score
- rank frontier

Baselines:
- full MHA
- shared KV
- GQA
- K=V proxy
- LRKV rank r

Stop condition: If low-rank residuals do not help specialist heads, demote.
