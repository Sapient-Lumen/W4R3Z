# CELL-279 — Triple-Latent Recall Failure Split

- priority: P1
- status: future-probe
- idea: IDEA-0278
- sources: SRC-0299

## Cheap first run

Separate generic sequence compression gains from exact associative recall failures.

## Metrics

- bits_per_byte_proxy
- recall_accuracy
- state_bytes
- score

## Required baselines

- Transformer
- linear_attention
- triple_latent
- triple_hybrid

## Stop condition

Promote only if it wins a non-recall regime and reveals a crisp recall failure boundary.
