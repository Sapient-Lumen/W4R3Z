# SQLite authority-boundary contract (rev0769)

1. A raw handle address MUST NOT be sufficient to identify a connection lifetime.
2. Authorizer installation MUST be generation-bound and later replacement/disablement MUST invalidate attestation.
3. Manifest construction MUST be deterministic, bounded, versioned, and fail closed on unknown authority-bearing metadata.
4. Manifest comparison MUST bind the exact database/container identity and recognized cohost metadata.
5. No peer-ingress acknowledgement may precede durable receipt plus successful current-generation attestation.
6. Error paths MUST preserve evidence and distinguish stale generation, alien authorizer, manifest drift, and resource exhaustion.
7. Tests MUST cover pointer/address reuse, authorizer replacement, restored schema cookies, row-order permutation, duplicate metadata, and over-budget input.
