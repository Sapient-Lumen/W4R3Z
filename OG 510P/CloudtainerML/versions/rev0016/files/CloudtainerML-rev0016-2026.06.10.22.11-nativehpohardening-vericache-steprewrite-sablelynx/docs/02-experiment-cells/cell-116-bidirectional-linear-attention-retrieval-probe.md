# CELL-116: Bidirectional Linear Attention Retrieval Probe

Priority: **P1**
Idea: `IDEA-0115`
Status: **candidate**

## Cheap first run

Tensor recurrence for bidirectional long-history retrieval with two-sided cues.

## Required baselines

- bidirectional softmax
- causal linear
- bidirectional linear
- gated bidirectional linear

## Metrics

- retrieval accuracy
- state size
- support error

## Stop / demote condition

If gated linear fails trivial bidirectional lookup, postpone.
