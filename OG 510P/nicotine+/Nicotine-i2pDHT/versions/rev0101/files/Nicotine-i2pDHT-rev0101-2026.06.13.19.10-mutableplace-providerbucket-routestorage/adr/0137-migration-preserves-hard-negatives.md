# ADR 0137 — migration preserves hard negatives

Status: accepted in rev0033.

Migration is a protocol boundary. Tombstones, revocations, key-crisis notices, provider-false evidence, and fork evidence must survive migration unless a future explicit repair process handles them.
