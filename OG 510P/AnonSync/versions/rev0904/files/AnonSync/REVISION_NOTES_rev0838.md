# AnonSync rev0838

## Mission increment

A safe heartbeat is not a JSON file that parsed successfully. It is a canonical lifecycle observation whose arithmetic and internal relationships are coherent, and whose claimed identity and owner generation are independently bound by the consuming domain before any takeover or status decision.

## Delivered

- New typed `sync_daemon_heartbeat_document` leaf with validating decode and encode paths.
- Exact JSON integer, stale-horizon, owner geometry, release/finality, and lockless-residue checks.
- Exact durable owner-generation binding at daemon preflight.
- Service-instance digest recomputation from session/daemon/worker/restart material.
- Non-final retained-owner evidence when release fails.
- Operator-status parity with daemon preflight.
- Focused 39-check adversarial corpus and 26-check source audit.
- Refactored sync-domain fixture audit from a brittle exact-count assertion to exact declaration/definition parity.

## Validation

- CTest: **129/129**
- Focused repeat: **390/390**
- Clang 17 `-Werror`: **39/39**
- GCC 14 ASan+UBSan, leak detection enabled: **39/39**
- Source patch replay: **PASS** across 224 active files
- Parent: directory **21/21**, ZIP **25/25**

## Scope limits

No standalone heartbeat authenticity, process-incarnation binding, distributed failure-detector correctness, complete crash/power-loss proof, Windows runtime result, full-project sanitizer result, convergence proof, confidentiality, anonymity, metadata hiding, key lifecycle, or secure erasure is claimed.
