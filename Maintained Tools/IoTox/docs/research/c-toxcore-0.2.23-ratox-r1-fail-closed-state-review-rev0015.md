# c-toxcore 0.2.23 review for fail-closed Ratox R1 state

**Review date:** 2026-08-16, America/New_York
**Maturity:** upstream release/repository review plus local pure-state implementation; not a new
source-linked or public-network run

## Primary sources

- https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
- https://github.com/TokTok/c-toxcore

## Verified upstream facts

The official v0.2.23 release is marked latest and was published on 2026-06-03. Its release notes say
that it fixes a critical bug found during manual audit, plus additional stability and test work. The
listed fixes include bounds testing while loading saved group peers, allocation-failure handling that
could otherwise double-free loaded DHT state, and a peer-offline use-after-free correction.

The official repository also names multiple static analyzers, Clang AddressSanitizer,
MemorySanitizer, ThreadSanitizer, UndefinedBehaviorSanitizer, AFL++, and ClusterFuzzLite as parts of
its development assurance surface. Those tools do not prove IoTox correct, but they reinforce the
need to treat allocation/failure ordering and state-machine fuzzing as first-class network-library
work rather than optional cleanup.

## Applied IoTox boundary

This review supports four conservative R1 choices:

1. Reserve exact request identity and bounded result storage before a control effect; do not discover
   replay-cache exhaustion after mutation. Remove any convenience API that could insert a result
   only after an effect, and release unused reserved capacity only during allocation-free commit.
2. Keep terminal sessions replay-capable only for already retained or in-progress control IDs; never
   admit a fresh effect after close or failed incarnation.
3. Validate configurable sequence origins, nonce/generation/incarnation exhaustion, output ACK
   application, and directory quotas before publishing state.
4. Exercise the complete attachment/input/output/control lifecycle and device/principal quota
   directory under ASan/UBSan state fuzzing in addition to deterministic boundary tests.

These are IoTox design inferences, not c-toxcore API requirements. R1 remains transport-independent
and feature bit 23 remains unadvertised. No PTY, shell, authority migration, toxcore dispatch, or
network service is claimed by this review.
