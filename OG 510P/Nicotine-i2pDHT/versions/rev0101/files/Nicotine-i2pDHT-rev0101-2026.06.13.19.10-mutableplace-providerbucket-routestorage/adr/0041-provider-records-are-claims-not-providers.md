# ADR 0041 — Provider records are claims, not providers

## Decision

A provider record is not accepted as semantic provider truth merely because its signature validates.

## Rationale

Provider records are easy to poison with reachable-looking but false providers. Retrieval must distinguish valid signature, unprobed hint, semantic proof, graceful refusal, and semantic lie.

## Consequence

Provider lookup needs probes, family diversity, and continued pressure under contradictions. Storage admission stays direct-provider-first until delegated reprovide is explicitly validated.
