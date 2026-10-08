# CELL-175: SANTA Stochastic Sparse-Attention Wind Tunnel

Priority: P0

Status: runnable

Idea: IDEA-0174

Source: SRC-0212

Cheap first run: experiments/stochastic_sparse_attention/stochastic_sparse_attention.cpp emits REV0014_STOCHASTIC_SPARSE_ATTENTION_SMOKE.json.

Metrics:
- MSE
- value rows read
- score
- winner counts

Baselines:
- top-k
- post-softmax MC
- stratified MC
- value-aware top-k

Stop condition: If MC is always dominated at equal read count, keep as systems note.
