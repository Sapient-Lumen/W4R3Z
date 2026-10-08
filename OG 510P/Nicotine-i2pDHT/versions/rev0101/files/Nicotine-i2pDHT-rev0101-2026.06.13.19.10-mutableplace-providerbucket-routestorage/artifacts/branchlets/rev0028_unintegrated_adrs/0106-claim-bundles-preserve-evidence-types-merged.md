# ADR 0101 — Claim bundles preserve evidence types

Status: accepted for rev0026 prototype.

Garden and peer evidence bundles are useful for latency, but bundles must not flatten evidence into generic proof. Provider truth, tombstones, custody proofs, forks, and revocations remain typed observations. Mixed scopes, live tombstone plus positive availability, and same-sequence conflicts are quarantine pressure.
