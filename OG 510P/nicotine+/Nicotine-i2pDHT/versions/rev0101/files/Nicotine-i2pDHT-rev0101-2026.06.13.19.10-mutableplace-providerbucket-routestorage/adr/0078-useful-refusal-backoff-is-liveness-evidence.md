# ADR 0078 — Useful refusal backoff is liveness evidence

Status: accepted in rev0018.

A useful refusal proves that a node is alive and resource-aware. The caller should slow down or shrink probes rather than punish the node or flood alternate paths blindly.
