# AnonSync slim C++ working cube — rev0648

AnonSync is best understood as a **local authorization-and-idempotency evidence kernel**. Its mission is to make an authorization decision reproducible at the point where an external effect may begin, bind that decision to one exact actor/operation/contract context, reserve the effect once, and leave enough durable evidence to recover honestly after interruption.

Rev0648 attacks the next local relay risk after rev0647: a bad transition signer/trust profile could be discovered only after outbox claim and downstream touch. The handle-bound relay now proves the configured signer and trust profile can produce and verify a terminal-transition intent **before** claiming work or opening the downstream store.

## Active invariants

1. **Interpretation:** the same semantic operation is derived from the same bounded, unambiguous input.
2. **Authorization:** the decision binds to verified identity, policy, contract, and operator configuration.
3. **One-time effect:** a durable reservation/outbox identity prevents the same semantic effect from becoming effective twice.
4. **Recovery:** after restart or restore, the system can distinguish prepared, claimed, terminal, rejected, and unknown work without inventing success.

## Rev0648 changes

- Adds relay transition-authority preflight before outbox claim or downstream touch.
- Rejects mismatched signer/private-key/trust-profile configurations without creating or opening the downstream store and without moving the outbox row to inflight.
- Retains rev0646 ledger-integrated sender replay and rev0647 provenance-bound downstream result rows.
- Refactors signer/trust load plus preflight verification into a named `RelayTransitionAuthority` helper.
- Relay reports now disclose `transition_authority_preflight_verified` for successful preflight-before-mutation paths.
- Package validation now includes the bad-authority negative regression and the valid-authority recovery path.

## Validate

```bash
cmake -S cpp/anonsync_core -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -DNDEBUG'
cmake --build build -j4
ctest --test-dir build --output-on-failure -j2
python3 tools/validate_rev0648_relay_authority_preflight.py
```

The packaged release binary was built with Release semantics and `-O0` to keep this large single-translation-unit cube tractable inside the cloudtainer. The release-o0 build and ctest logs are under `audit/logs/`.

## Read first

- `docs/0038-rev0648-relay-authority-preflight.md` — exact relay preflight change, refactor slice, tests, and remaining ceiling.
- `docs/0037-rev0647-downstream-provenance.md` — downstream provenance binding and local store hardening.
- `docs/0036-rev0646-ledger-integrated-replay.md` — replay/ledger transaction integration.
- `docs/0034-rev0644-deep-mission-review.md` — mission, severe failures, missing architecture, waste, speculation, and ordered roadmap.
- `docs/0003-next-risk-register.md` — current priorities after rev0648.
- `audit/rev0648-relay-authority-preflight-package-validator.json` — adversarial package checks.
- `gateway/rev0648-cpp-ledger-backend-capabilities.json` — active exact v42 claims and explicit ceilings.

## Honest ceiling

This is still a local library/CLI and deterministic adapter harness, not a deployed HTTP service, TLS authenticator, DPoP verifier, signed operator control plane, HSM signer, distributed replay authority, independent witness, or proof that a real downstream service performed an effect. Rev0648 prevents a bad local relay signer/trust configuration from causing downstream mutation before terminal-transition authority is proven; it does not provide remote delivery proof.
