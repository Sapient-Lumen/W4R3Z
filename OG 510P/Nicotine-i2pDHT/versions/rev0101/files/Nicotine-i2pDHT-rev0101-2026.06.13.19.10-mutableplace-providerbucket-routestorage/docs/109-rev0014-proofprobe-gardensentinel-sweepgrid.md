# rev0014 — proofprobe / gardensentinel / sweepgrid

rev0014 keeps the cube in generic DHT-over-I2P design space and continues the risk-first instruction. The theme is joining earlier isolated pressure surfaces into larger local judgment loops.

## New risky joins

1. **Private-ish provider probing + provider proof handshakes** now meet in `proofprobe.py`. A provider proof is not evaluated alone; it is evaluated against the probe plan that caused it, including decoys, family caps, and raw-key exposure budget.
2. **Garden witness/proof evidence + local autocuration** now meet in `gardensentinel.py`. A garden can be useful, contradictory, overloaded, truthful, or semantically false; the sentinel score remains private and local.
3. **Adversarial pressure sweeps** now live in `sweepgrid.py`. It varies captured-family share, false-provider share, stale-head share, and latency advantage so we can see where optimistic policies should continue instead of accept.
4. **Family-diversity refactor** now lives in `familydiversity.py`. The helper is deliberately modest: it caps same-family evidence and counts monoculture pressure. It does not prove independence.
5. **Historical supersession audit** now lives in `HISTORICAL_SUPERSESSION.json` and `supersession.py`. Duplicate ADR/doc numbering is no longer just an audit warning; known historical duplicates are mapped explicitly.

## Strongest guess

```text
Provider truth, garden usefulness, and lookup freshness are coupled.
A DHT client should not accept any one of them in isolation.
```

A valid provider proof can leak interest. A useful refusal can prove liveness without proving availability. A witness receipt can preserve evidence without becoming quorum. A fast lookup window can look successful while being captured. rev0014 starts testing those joins instead of polishing any single subsystem.

## Nonclaim

This is still not a live DHT, not an I2P/SAM transport, not private retrieval, not a production provider proof protocol, not global reputation, and not a Sybil solution. It is a local-pressure design lab.
