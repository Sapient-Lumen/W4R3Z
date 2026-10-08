# rev0642 sender replay cache and freshness window

## What changed

Rev0642 extends the rev0641 asymmetric sender-possession check with a local replay/freshness gate at the service ingress boundary.

The active service config format is now `anonsync-ingress-service-config-v4-asymmetric-sender-replay-cache`. In addition to the service-pinned caller public RSA JWK from rev0641, the config now owns the sender replay cache and freshness policy:

- `sender_replay_cache_path`
- `sender_replay_window_seconds`
- `sender_replay_future_skew_seconds`
- optional deterministic `sender_replay_now_epoch` for hermetic tests

The request proof format is now `anonsync-ingress-sender-possession-v3-lp-rs256-nonce`. Each request-side proof must carry a printable nonce and issued-at epoch. The service validates the nonce shape, verifies issued-at against the configured freshness/skew policy, verifies the RS256 signature, and then reserves a derived replay key in a service-owned SQLite replay cache before it invokes the profile adapter or appends to the ledger.

## Bound material

The RS256 signature now covers the rev0641 length-prefixed sender tuple plus:

- `sender_nonce`
- `sender_issued_at_epoch`

The replay cache key is a separate length-prefixed tuple with domain `anonsync-ingress-sender-replay-key-v1` over:

- service id
- service config SHA-256
- ingress profile SHA-256
- sender proof key id
- principal
- nonce
- issued-at epoch
- canonical case SHA-256

The cache records the key SHA-256, service id, profile digest, key id, principal, nonce, issued-at epoch, observed-at epoch, expiry epoch, request id, config handle, and case digest.

## Why this matters

Rev0641 proved asymmetric possession but not freshness. A captured valid proof could be submitted again if the caller or embedding layer did not maintain a replay cache. Rev0642 closes that local gap by making replay-cache reservation a first-class service-boundary action before durable ledger append.

This is intentionally local. It reduces replay risk for a single service process/config/cache authority, but it does not solve distributed replay across multiple service instances unless they share the same strongly consistent replay-cache authority or receive externally verifiable nonce challenges.

## Fail-closed coverage

The rev0642 package validator checks successful reservation plus failures before append for:

- duplicate sender nonce replay
- malformed sender nonce
- stale sender issued-at
- future sender issued-at beyond allowed skew
- missing sender replay cache path
- replay-cache symlink family
- service config digest mismatch
- disabled service config
- profile digest drift
- bad RS256 signature
- missing sender proof
- sender case-digest mismatch
- proof algorithm mismatch
- proof key id mismatch
- HMAC regression field in the proof
- unsupported authenticated-context fields
- symmetric caller secret in the service config
- invalid caller public JWK
- request operator-field injection
- request ledger-mode selection
- v36 capability downgrade
- accidental combination of service-bound and direct profile CLI paths

## Refactor note

This revision moves sender replay handling into one service-boundary helper family and uses the same length-prefixed tuple style as the prior sender material. It also rejects cache-path symlink families before SQLite opens the sidecar. The broader file split of `reporting_selftests.cpp` and `sqlite_replay_ledger.cpp` remains necessary, but this cleanup keeps the active ingress/proof path from growing another duplicate parsing/signing branch.

## Residual risk

This is not DPoP, mTLS, certificate-bound access tokens, TLS exporter binding, token `cnf` binding, a gateway listener, or a distributed replay service. The trusted time source is still local/configured. The cache has local pruning but no cluster ownership or multi-region consistency story. Client key rotation, revocation, and key-use constraints remain fixture-level rather than operator-managed production policy.
