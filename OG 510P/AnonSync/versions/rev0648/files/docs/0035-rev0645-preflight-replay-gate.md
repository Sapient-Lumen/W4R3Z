# Rev0645 preflight replay gate

## Problem

Rev0644 fixed the trusted-context confused-deputy boundary, but left the sender replay cache in front of profile/contract validation. A valid signed request could therefore reserve a nonce, fail profile authorization, append no ledger row, and become unretryable. That was a reliability and accountability failure: the service had consumed proof material without producing a durable authorization decision.

## Change

Rev0645 changes the service path from:

1. load and digest-check operator service configuration;
2. parse request and transport context;
3. verify sender proof and reserve replay nonce;
4. run profile/contract adapter against the real ledger;
5. append a durable reservation when accepted.

To:

1. load and digest-check operator service configuration;
2. parse request and transport context;
3. reject request-body copies of trusted identity;
4. verify sender proof **without replay-cache mutation**;
5. construct the internal profile request;
6. run profile/contract adapter against a private temporary ledger in a private workspace;
7. if preflight rejects, return failure evidence and leave the replay cache unchanged;
8. if preflight accepts, reserve the sender replay nonce;
9. run the same profile/contract adapter against the actual configured ledger.

This is not a complete atomicity solution. It is a risk-reducing ordering change that avoids consuming scarce replay state for requests that are not even authorized by the profile path.

## Refactor slice

The profile-adapter subprocess path is now represented by a shared execution helper instead of duplicated service/CLI plumbing. The helper owns the temporary request/report paths, subprocess invocation, report parsing, accepted/error interpretation, and cleanup. This makes the preflight and actual execution paths use the same parser and acceptance rule.

The refactor is deliberately small. Large files such as `runner.cpp`, `sqlite_replay_ledger.cpp`, and `reporting_selftests.cpp` still need trust-domain splits. Rev0645 prioritized the live seam over broad rearrangement.

## New package regressions

`tools/validate_rev0645_preflight_replay_gate.py` adds two high-signal adversarial checks:

1. **Profile rejection must not burn the nonce.** The validator signs a valid sender proof around a request whose profile kind is invalid. The service must verify the proof, reject during preflight, append no ledger row, reserve no replay-cache row, and allow a retry to fail for the same profile reason rather than duplicate nonce.
2. **Post-preflight seam remains visible.** The validator makes preflight succeed but points the actual ledger path at a directory. The service must disclose that sender replay-cache reservation succeeded before actual ledger append failed, and a retry must reject the duplicate nonce. This keeps the residual hazard explicit until a later revision removes it.

## Evidence fields

Successful and failed reports now expose:

- `profile_preflight_before_sender_replay_reservation: true`
- `profile_rejection_consumes_sender_nonce: false`
- `sender_replay_cache_and_ledger_share_one_transaction: false`
- `post_preflight_crash_or_ledger_failure_can_consume_sender_nonce: true`

The last two are intentionally negative. They keep the cube from overstating exactly-once or crash-atomic behavior.

## Next engineering step

The next P0 is one authoritative ingress transaction/state machine. Proof identity, replay admission, authorization outcome, semantic reservation, and outbox state should be recorded together. When that lands, the rev0645 post-preflight ledger-failure regression should flip from “visible residual seam” to “recoverable committed decision or retryable no-op,” with no consumed nonce lacking a corresponding ledger state.
