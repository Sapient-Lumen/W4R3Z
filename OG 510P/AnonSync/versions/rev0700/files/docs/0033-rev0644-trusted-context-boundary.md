# rev0644 trusted-context boundary and replay-cache hardening

## Problem corrected

Rev0643 accepted a JSON member named `authenticated_context` containing `transport_authenticated`, `authenticator`, `principal`, and sender proof. That object arrived through the same untrusted request channel as the case to authorize. Signing the object proved possession of a configured key, but it did not prove that the asserted principal or authenticator came from TLS, a gateway, or any other trusted transport. The report nevertheless used authentication language.

The public C++ config object also exposed security switches such as whether caller binding was required. A direct library caller could construct policy rather than merely select an operator-owned policy.

## New API shape

Rev0644 replaces the mutable public service config with:

```cpp
struct IngressReservationServiceHandle {
    std::string service_config_path;
    std::string service_config_sha256;
};

struct IngressTransportContext {
    bool transport_authenticated = false;
    std::string authenticator;
    std::string principal;
};
```

`reserve_ingress_request_json(handle, context, request_text)` reloads the digest-pinned service configuration internally. Request JSON is allowlisted and rejects all trusted-identity spellings before signature verification. The CLI similarly requires a separate `--ingress-transport-context` operand.

This is structural separation, not deployed authentication. A production adapter must ensure only the listener or verified proxy boundary can construct `IngressTransportContext`.

## Replay-cache changes

- Format advanced to `anonsync-ingress-sender-replay-cache-v4-sqlite-trusted-context-nonce-window-unique`.
- Unique identity is `(sender_proof_kid, nonce)` while the row remains retained.
- Proof and replay-key material bind the service config digest, ingress profile digest, cache instance id, trusted principal/authenticator, request identity, nonce, timestamp, and case digest.
- Cache files open with `SQLITE_OPEN_NOFOLLOW | SQLITE_OPEN_FULLMUTEX`.
- `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=FULL` are queried and verified rather than merely requested.
- Busy timeout is 5000 ms; selected SQLite limits are lowered.
- `trusted_schema=OFF` is set.
- Cache `created_at_epoch` and `last_seen_epoch` are validated; `last_seen_epoch` is updated with `max(previous, now)` so a tolerated clock rollback cannot move it backward.
- Reports say `retained-replay-window`; they do not claim permanent nonce uniqueness after pruning.

## Parser and crypto boundary changes

The review found a separate undefined-behavior risk: the Base64url decoder repeatedly left-shifted a signed `int`. Long attacker-controlled strings could overflow it. The accumulator is now `std::uint32_t`, and a long-input regression is part of the parser selftest.

Other changes:

- JSON whitespace is limited to space, horizontal tab, carriage return, and line feed.
- Raw string bytes must form valid UTF-8 and may not encode surrogates, overlong sequences, or values above U+10FFFF.
- Number parsing uses locale-independent `std::from_chars` with full consumption and finite checks.
- Integer access rejects fractions and values outside ±(2^53−1).
- Canonical numeric output uses the classic locale.
- RSA JWK `n` and `e` must be canonical nonempty Base64urlUInt values; leading-zero encodings are rejected.
- RSA key strength must be at least 2048 bits and 112 security bits.
- Service config, context, and request reads are bounded before parsing or cryptography.
- Failure to restrict a private workspace to owner permissions aborts the request.

## Deliberately exposed residual seam

The sender replay cache and reservation ledger do not share one transaction. The current order is:

1. parse outer request and verify sender proof;
2. commit replay nonce in the cache database;
3. load/validate the selected profile and run authorization;
4. append reservation/outbox in the ledger transaction.

A failure in steps 3–4 leaves a consumed nonce with no reservation. The rev0644 package validator creates exactly that case, confirms zero ledger rows, confirms the report discloses the consumed nonce, and confirms a retry is rejected as replay.

The correct next change is not another Boolean capability. It is one authoritative transaction/state machine after all possible non-mutating validation, with explicit terminal outcomes for accepted, denied, malformed-after-authentication, and unknown work.
