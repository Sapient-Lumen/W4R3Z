# Research notes — 2026-06-06 — rev0048

The research direction for this turn stayed close to publication side effects, local audit evidence, and evidence-retention pressure.

- I2P/SAM remains a likely future non-Java integration surface, but rev0048 keeps transport side effects shadowed.
- Provider/publication records keep teaching the same lesson: a record is a scoped routing/availability hint with freshness and republish pressure, not content truth.
- Transparency-style witness thinking is useful, but the cube keeps witnesses local and typed so they do not become a new authority.
- Evidence cleanup is not boring storage hygiene; cleanup can become authorization if hard negatives disappear.

The code therefore adds a no-network bridge shadow, local audit-quorum evidence, and redress GC pressure before any live transport or mutable-DHT write exists.
