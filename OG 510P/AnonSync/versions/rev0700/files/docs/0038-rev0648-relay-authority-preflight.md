# rev0648 — relay transition-authority preflight before claim/downstream

## Risk addressed

Rev0647 hardened the local downstream journal, but relay execution still loaded the transition signer and trust profile **after** claiming outbox work and applying/touching downstream. A bad private key, wrong `kid`, expired trust profile, or trust digest error could therefore create an external/local downstream effect before the relay proved it could produce a terminal signed transition for the ledger.

That was the next most dangerous local seam because it turned operator misconfiguration into an effect-before-evidence failure.

## Code change

Rev0648 adds `RelayTransitionAuthority` and `load_and_preflight_relay_transition_authority(...)` in `sqlite_replay_ledger.cpp`.

Before the relay claims work or opens the downstream store, it now:

1. parses the configured private signing key;
2. reads and digest-pins the transition trust profile;
3. creates a dummy signed terminal-transition intent using the same terminal state, signer `kid`, and relay timestamp window that the real claim would use;
4. verifies that dummy intent against the trust profile.

Only after that preflight succeeds does the relay perform downstream symlink-family rejection, claim outbox work, touch downstream, and create the real signed terminal transition.

## Behavioral guarantee added

A bad relay signer/trust configuration now fails before:

- outbox claim mutation;
- downstream SQLite creation/open/touch;
- downstream effect row insertion or observation-count increment.

The valid signer path still claims, touches downstream, and terminally closes the effect.

## Refactor/audit slice

The signer/trust load and proof-of-authority logic moved out of the hot relay execution path into a named transition-authority helper. Relay reports now disclose `transition_authority_preflight_verified` when the helper succeeded before mutation.

## Validation added

`tools/validate_rev0648_relay_authority_preflight.py` retains the rev0647 downstream provenance/recovery checks and adds a bad-authority regression:

- seed one prepared outbox row;
- configure a private key that does not match the trusted signer JWK;
- run the handle-bound relay;
- require rejection with no downstream store created/touched and outbox counters still `(reserved=1, inflight=0, terminal=0)`;
- rerun with a valid signer/trust pair and require the same work to close terminally.

## Remaining ceiling

This is still local key custody and a local SQLite downstream harness. It does not provide HSM-backed signing, a signed relay control plane, real remote delivery attestation, distributed exactly-once semantics, or a deployed TLS/mTLS/DPoP ingress boundary.
