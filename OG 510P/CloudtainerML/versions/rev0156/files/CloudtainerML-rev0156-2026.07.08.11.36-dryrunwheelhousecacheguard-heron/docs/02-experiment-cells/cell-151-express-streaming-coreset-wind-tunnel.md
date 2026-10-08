# CELL-151 — Express Streaming Coreset Wind Tunnel

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Question

Can a streaming weighted coreset approximate causal attention better than recency/uniform retention at equal cache size?

## Cheap first run

Runnable C++ smoke test emits REV0013_EXPRESS_STREAMING_CORESET_SMOKE.json.

## Metrics

- mean MSE to full attention
- target retention
- runtime
- regime failure count

## Stop condition

If the coreset surrogate loses to recency/uniform on most non-oracle regimes, demote until a better halving kernel exists.
