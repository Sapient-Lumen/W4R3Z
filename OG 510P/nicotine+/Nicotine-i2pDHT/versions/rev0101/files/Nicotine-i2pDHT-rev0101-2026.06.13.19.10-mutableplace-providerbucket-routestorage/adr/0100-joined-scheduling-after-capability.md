# ADR 0100 — joined scheduling after capability

Decision: capability/admission success is not a queue success.

Reason: garden nodes have scarce control-plane capacity. Bulk work, refusal spam, or otherwise valid requests must not starve mutable heads, witnesses, seed-gate work, or tombstone repair.

Consequence: `schedjoin.py` joins capgate and queueforge and treats useful refusals as evidence, not completed work.
