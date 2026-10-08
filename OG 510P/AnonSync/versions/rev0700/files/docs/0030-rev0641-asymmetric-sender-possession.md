# rev0641 asymmetric sender possession

## What changed

Rev0641 replaces the rev0640 symmetric service-owned caller HMAC secret with an asymmetric sender-possession check at the service ingress boundary.

The active service config format is now `anonsync-ingress-service-config-v3-asymmetric-sender-possession`. A valid service config pins only a caller public RSA JWK:

- `kty: RSA`
- `alg: RS256`
- `kid`
- public modulus `n`
- public exponent `e`

It must not contain `caller_binding_secret_id` or `caller_binding_hmac_sha256_secret`. Those fields now fail closed because a production-shaped service config should not hold the caller's shared secret or private signing material.

The request proof format is now `anonsync-ingress-sender-possession-v2-lp-rs256`. The request still carries `authenticated_context.sender_possession`, but the proof is an RS256 signature rather than an HMAC.

## Bound material

The RS256 signature covers a length-prefixed tuple with these fields:

- service id
- service config SHA-256
- ingress profile SHA-256
- sender proof algorithm
- sender proof key id
- request format and revision id
- request id
- config handle
- transport-authenticated flag
- authenticator
- principal
- canonical case SHA-256

The service verifies the sender signature before it creates the private request workspace, invokes the profile adapter, or appends to SQLite. The reservation report advances to `anonsync-ingress-reservation-report-v4-asymmetric-sender-boundary` and records the verified key id, algorithm, material digest, and OpenSSL verification reason.

## Why this matters

Rev0640 was a useful local boundary, but it still required a symmetric caller secret in the service config. That is a bad production trajectory: the service that verifies the caller should not need a reusable caller secret that can also mint caller proofs. Rev0641 moves the cube closer to real proof-of-possession by letting the service verify possession with public material only.

This is not full DPoP, mTLS, or a deployed gateway. There is still no HTTP method/URI proof, nonce policy, proof replay cache, token cnf binding, client key rotation/revocation plan, or TLS/exporter binding. It is a concrete step from shared-secret possession toward asymmetric caller-key possession.

## Fail-closed coverage

The rev0641 package validator checks successful reservation plus failures before append for:

- bad service config digest
- disabled service config
- profile digest drift
- bad RS256 signature
- missing proof
- case digest mismatch
- proof algorithm mismatch
- proof key id mismatch
- HMAC regression field in the proof
- unsupported authenticated-context fields
- symmetric caller secret in the service config
- invalid caller public JWK
- request operator-field injection
- request ledger-mode selection
- v35 capability downgrade
- accidental combination of service-bound and direct profile CLI paths

## Refactor note

This revision also removes the remaining unused selftest-only base64url wrapper and routes selftest RSA modulus encoding through the production base64url codec. The broader file split of `reporting_selftests.cpp` and `sqlite_replay_ledger.cpp` remains necessary, but this cleanup reduces duplicated crypto-adjacent helper surface immediately adjacent to the sender-proof work.
