# rev0643 sender replay-cache instance binding

Rev0642 added a local sender replay cache with nonce and issued-at freshness checks, but the cache was still treated mainly as a path. That left an important operator/deployment footgun: a service could accidentally be pointed at a cache created for another service/profile/caller boundary, or a copied cache could be reused without any local identity evidence.

Rev0643 narrows that seam by making the replay cache an explicitly identified local authority rather than just a SQLite filename.

## Active formats

- Service config: `anonsync-ingress-service-config-v5-asymmetric-sender-replay-cache-bound`
- Service report: `anonsync-ingress-reservation-report-v6-asymmetric-sender-cache-boundary`
- Sender proof material: `anonsync-ingress-sender-possession-v4-lp-rs256-nonce-cache`
- Sender replay cache: `anonsync-ingress-sender-replay-cache-v2-sqlite-bound-instance`
- Sender replay key material: `anonsync-ingress-sender-replay-key-v2-cache-instance`
- Capability manifest: exact v38

## What changed

The service config now owns a printable `sender_replay_cache_instance_id`. That id is included in the RS256 sender-possession signing material and in the replay-key derivation. Before inserting a nonce reservation, the service opens the SQLite replay cache inside a transaction and verifies or initializes `sender_replay_meta` with:

- cache format
- replay-cache instance id
- service id
- service config SHA-256
- ingress profile SHA-256
- caller public JWK kid
- created-at epoch
- last-seen epoch

If any identity metadata already exists and does not match the service config, reservation fails before the profile adapter is invoked and before the durable ledger is appended.

## Risk reduced

This prevents silent reuse of a replay cache created for another local service/profile/caller boundary. It also gives a concrete local audit point for cache identity and makes sender signatures depend on the replay authority identity that will enforce nonce uniqueness.

## Still not solved

This is still local SQLite replay state. It is not a distributed nonce authority, DPoP nonce service, TLS exporter binding, mTLS token `cnf` verifier, signed operator control plane, or independent witness. A byte-for-byte clone of a service config plus replay cache still carries the same local identity. Detecting that requires external control-plane state, remote attestation, signed deployment inventory, or a distributed replay service.

## Validation

The rev0643 package validator exercises:

- successful reservation with replay-cache identity metadata
- duplicate nonce rejection
- malformed nonce rejection
- stale and future issued-at rejection
- missing cache path rejection
- symlinked cache path rejection
- missing replay-cache instance id rejection
- replay-cache identity mismatch rejection
- bad RS256 signature, bad kid/alg, and case digest mismatch rejection
- symmetric-secret regression rejection
- v37 downgrade rejection
