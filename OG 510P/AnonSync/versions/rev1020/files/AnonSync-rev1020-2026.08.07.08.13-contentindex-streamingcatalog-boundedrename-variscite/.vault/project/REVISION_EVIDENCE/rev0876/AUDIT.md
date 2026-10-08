# AnonSync rev0876 evidence audit

## Mission

AnonSync is an authority-accounting system: exact authorized history owns
identity, causality, projection, dispatch, retry, receiver admission, and
visible effect. Summaries and transport state may accelerate or coordinate that
history but may not replace it.

## Revision result

Rev0876 creates the first reusable production-source delivery boundary around
`SyncReplicaSqliteOwner`: a canonical bounded request/receipt protocol, a
service that claims/adopts/receipts/settles exact operation evidence, a
transaction-bound receiver admission cutpoint, and a real mutual TLS 1.3
OpenSSL adapter with exact ALPN, peer-chain verification, actor/SPKI pinning,
RFC 9266 exporter binding, and bounded encrypted records.

Receipts are deliberately named and modeled as **evidence-terminal**. They prove
retention of exact immutable operation evidence by the authenticated receiver;
they do not prove payload availability or a visible filesystem effect.

## Audit/refactor corrections

The implementation audit corrected nine load-bearing defects or waste patterns:

1. Admission and receipt cutpoint are returned from one SQLite write
   transaction, eliminating an admission-to-snapshot race.
2. Wire-envelope limits are independent from aggregate retention policy.
3. Normal service calls no longer restore complete O(history) state merely to
   borrow decoding limits.
4. TLS authentication requires verification mode as well as an OK result.
5. Exact ALPN prevents cross-protocol reuse of an otherwise valid identity.
6. Encrypted I/O accepts only an opaque post-pin channel capability.
7. Every record re-observes the current peer SPKI and exporter, so reusing an
   `SSL` object for a new handshake invalidates stale authority.
8. Frame ceilings are proven capable of carrying worst-case valid requests and
   receipts before any durable claim or admission.
9. Every receipt names a real nonzero receiver generation; unknown dispositions
   fail nonterminal.

The two-database ambiguous-delivery scenario moved from the SQLite-owner test
monolith to the delivery-service boundary where that composition behavior
belongs. A public model-limit validator replaces throwaway model construction.

## Validation authority

The final source state passed one complete 179-test GCC Debug registry, the 54
registered source/audit tests, four focused executables under GCC Debug, Clang
Release `-Werror`, and GCC ASan/UBSan with leak detection and bundled SQLite
instrumentation, plus repeated owner/service/TLS stress. Exact counts and logs
are in `validation/VALIDATION_SUMMARY.json` and this evidence directory.

## Largest remaining gap

The new path remains a production library rather than the shipped executable.
It stops at operation-evidence retention. Payload transfer, receiver effect
intent, atomic visible publication, an effect-terminal durable receipt,
membership/key lifecycle, production-scale incremental ownership,
anti-entropy/compaction, and an explicit privacy model remain future work.

The full analysis, online primary-source research, speculation, and deliberate
nonclaims are in `AUTHENTICATED_EVIDENCE_DELIVERY_AUDIT_rev0876.md`.
