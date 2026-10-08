# Rev0646 ledger-integrated sender replay

## Problem

Rev0645 prevented the easiest nonce-burn case by verifying sender possession and preflighting profile/contract acceptance before replay-cache mutation. The remaining seam was still high risk: after preflight succeeded, the service wrote the sender replay cache and then asked the actual ledger to append the prepared decision/outbox row. A crash or actual-ledger failure between those writes could consume the sender nonce without recording a durable authorization decision.

## Change

Rev0646 removes the service-side replay-cache write from the service path. The sequence is now:

1. load and digest-check operator service configuration;
2. validate the separately supplied trusted transport context;
3. parse the untrusted request and reject body-side trusted identity/operator fields;
4. verify sender RS256 possession without mutation;
5. compute sender replay evidence from trusted service config, profile digest, cache instance id, proof kid, principal, nonce, observed time, and replay window;
6. run the profile adapter against a private temporary ledger as preflight;
7. if preflight rejects, return failure evidence and consume no nonce;
8. if preflight accepts, inject trusted `ingress_sender_replay` evidence into the internal case only after request sanitization;
9. let the SQLite/WAL ledger insert the sender replay row, prepared ledger entry, and effect outbox reservation in one `BEGIN IMMEDIATE` transaction.

A duplicate nonce now fails closed from the ledger-integrated replay table. If the duplicate is exact, older replay identities such as JWT `jti` may also fail closed first; the package validator separately exercises a same-nonce/different-valid-proof path so the replay table is proven, not merely inferred.

## Refactor/audit slice

The rev0646 audit focused on the ingress execution boundary instead of capability registry expansion:

- `execute_ingress_profile_adapter` now receives optional trusted replay evidence and injects it only after `sanitized_ingress_case` has rejected caller-supplied replay evidence.
- `normalizer_envelopes.cpp` carries the service-injected replay object through normalization to the ledger stage.
- `sqlite_replay_ledger.cpp` owns replay evidence validation, duplicate lookup, retention-window pruning, replay row insertion, and rollback with the ledger/outbox transaction.
- The service reports now claim `sender_replay_cache_and_ledger_share_one_transaction: true` and `post_preflight_crash_or_ledger_failure_can_consume_sender_nonce: false` for the local SQLite service path.

This is still not a broad architecture split. `runner.cpp`, `sqlite_replay_ledger.cpp`, and `reporting_selftests.cpp` remain too large. Rev0646 deliberately spends the revision on the live atomicity seam.

## New package regressions

`tools/validate_rev0646_ledger_integrated_replay.py` checks:

1. successful service reservation inserts exactly one ledger entry and exactly one ledger-integrated sender replay row;
2. the old external sender replay cache is not created by the service path;
3. exact duplicate requests fail closed without changing ledger or replay-row counts;
4. a same-nonce/different-valid-proof request is rejected by replay semantics without appending;
5. profile preflight rejection verifies the proof but consumes no nonce;
6. post-preflight actual-ledger failure does not consume the nonce and creates no old external replay cache;
7. caller-supplied `case.ingress_sender_replay` is rejected after proof verification;
8. trusted-context, ASCII-casefold, numeric, RSA-size, symlink, request-size, missing-context, and capability-downgrade boundaries remain intact.

## Validation note

Release-O0 CTest and the rev0646 adversarial package validator passed. An ASAN/UBSAN debug build was attempted twice but terminated while compiling large translation units before sanitizer CTest could run; rev0646 keeps those incomplete logs as evidence and does not claim sanitizer coverage.

## Remaining ceiling

Rev0646 closes the local SQLite service-path dual-write seam. It does **not** prove:

- distributed replay uniqueness across multiple service nodes;
- behavior after backup/restore/failover of a fleet-level nonce authority;
- a real TLS/mTLS/DPoP authenticator that alone can construct `IngressTransportContext`;
- a real downstream adapter with remote idempotency, unknown-result reconciliation, and terminal-state mapping;
- an authenticated operator control plane for profiles, contracts, capabilities, trust roots, and key rotations.

## Next engineering step

The next P0 is no longer the local replay/ledger dual-write seam. It is deploying one real ingress authenticator and one real downstream adapter, then crash-testing the full authorization-to-effect path across remote unknown outcomes. The local CLI context-file and SQLite downstream journal should stay marked as harnesses.
