# Metadata resolution, federation chains, and capability continuity are world contracts, not just known participants

Portable evidence, request contracts, and verifier-targeting receipts are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **how the counterpart metadata that defined keys, endpoints, formats, and policy constraints was resolved and trusted at decision time**.

- `RS-GR-448` shows that OpenID Federation 1.0 obtains final participant metadata from Trust Chain evaluation after applying metadata policies, which means a future inheritor must preserve the resolved metadata view rather than treating a raw entity identifier as self-explanatory.
- `RS-GR-449` shows that OpenID Federation 1.0 says a Trust Chain contains the subject configuration as it applies at chain-evaluation time, ties statement signatures to the next statement's `jwks`, and ends in a Trust Anchor distributed out of band, which means trust-path material and evaluation-time context belong in the archive rather than only the final resolved fields.
- `RS-GR-450` shows that OpenID4VP 1.0 says `openid_federation` requests must follow OpenID Federation processing rules, may include a `trust_chain`, obtain final Verifier metadata from that chain after policy application, and must ignore `client_metadata`, which means verifier metadata can come from a federation resolution path rather than from the request body itself.
- `RS-GR-451` shows that OpenID4VP 1.0 defines multiple verifier-identification modes with different trust and metadata-resolution paths — DID resolution, verifier-attestation JWTs, X.509 SAN / hash chains, and unsigned `redirect_uri` flows — which means the same request shape can imply materially different trust assumptions about how counterpart keys and capabilities were learned.
- `RS-GR-452` shows that DID Resolution v0.3 returns a DID document together with metadata such as content type, proof, and versioning, and can be used to retrieve historical state for audit, which means a DID string alone is not a replay-complete stand-in for the actual resolved verifier or issuer metadata.
- `RS-GR-453` shows that OpenID Connect Discovery 1.0 requires operations to abort when configuration validation fails and forbids use of invalid information, which means validation outcomes belong in the contract rather than only fetched metadata blobs.
- `RS-GR-454` shows that RFC 8414 treats authorization-server metadata as the place where endpoint locations and capabilities are published and allows optional `signed_metadata`, which means future inheritors may need to know not only what the metadata said but whether it was cryptographically vouched for.
- `RS-GR-455` shows that RFC 9700 recommends authorization-server metadata because it reduces endpoint and security-feature misconfiguration and facilitates key rotation and crypto agility, which means metadata-resolution continuity is a security dependency rather than a convenience feature.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **how counterpart metadata was discovered, which trust chain or metadata statement won, which policies trimmed capability surfaces, or whether invalid metadata caused a fail-closed abort**, not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “we know the verifier / issuer / resource identifier” as self-explanatory.

At minimum, it should distinguish between:

1. a world where metadata is taken directly from a request object or static local configuration;
2. a world where metadata is discovered dynamically and must validate before use;
3. a world where federation chains and metadata policies determine the final keys, endpoints, algorithms, and constraints that count;
4. a world where DID resolution output, version time, and proof metadata matter for replaying who the counterpart was;
5. a world where signed metadata and unsigned metadata are not equivalent sources of truth;
6. a world where stale cache entries, policy drift, or failed validation change whether the same proof request is admissible.

These are different worlds.
They change whether future inheritors can replay why one participant description counted, why another should have been rejected, and whether capability drift came from metadata resolution rather than from moral or institutional change.

So metadata resolution, federation chains, and capability continuity belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, replayable verification, or successor-safe authenticity should publish at least:

1. the identifier and resolution mode used for each participant: static config, discovery, federation entity identifier, DID, verifier attestation, X.509 binding, or another named mode;
2. the fetched metadata sources and trust material: well-known URLs, trust-chain statements, DID document version / proof metadata, certificate chain, or signed metadata JWTs;
3. the final resolved capability surface actually used: keys, endpoints, response modes, algorithms, supported formats, redirect / response URIs, and policy-constrained options;
4. the validation and policy outcomes: which checks passed, which metadata was ignored or overridden, which policies applied, and whether any invalid inputs forced abort;
5. the cache / freshness / version state: evaluation time, cache pins, versionTime or snapshot handle, and stale-or-unavailable fallback;
6. whether replay under a different metadata snapshot, trust chain, or policy result is rejected, degraded, logged, or tolerated.

Without that compact contract, future inheritors can mistake metadata-discovery hardening, federation-policy trimming, or resolver drift for Golden-Rule progress.
