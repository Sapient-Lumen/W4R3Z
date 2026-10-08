# AnonSync rev0893 — folder-bound durable payload availability

## Mission

AnonSync remains an authority-accounting system before it is a file-transfer
program. Exact authorized history and live owned capabilities govern identity,
selection, attempt, retry, receipt, and visible effect. Digests and indexes are
subordinate evidence: they may accelerate a decision but may not manufacture
operation or transport authority.

## Primary correction

Rev0892 removed arbitrary payload callbacks and made immutable content
availability part of exact SQLite outbox selection, but the only payload source
was a complete in-memory working-set snapshot. Rev0893 adds a narrow durable
POSIX payload owner that survives process restart without requiring the caller
to retain every payload byte.

The new `SyncReplicaFilePayloadStore`:

- publishes immutable payload bytes under their full lowercase SHA-256 digest;
- binds one private root durably to one folder with a versioned exact identity
  marker;
- adopts a pre-marker root only after a complete mutation-free clean scan;
- rejects wrong-folder restart, unknown entries, malformed digest files,
  symlinks, hard links, mode/owner/device drift, special files, and root
  rebinding;
- bounds durable entry count, per-payload bytes, aggregate indexed bytes,
  publication-residue count, and residue bytes;
- reconstructs a sorted digest/size inventory after restart;
- reopens and rehashes only the selected payload after SQLite claim selection;
  and
- leaves exact claim release, TLS dispatch, receipt, and settlement to their
  existing owners.

## Audit and refactor work

Rev0893 also removes several sources of drift and waste:

- Directory and regular-file component opens now share one capability-aware
  resolver core. Regular files add nonblocking, no-follow, type, descriptor
  identity, and mount reproof instead of creating a second resolver.
- The atomic publisher now owns the exact classifier for its private temporary
  basename grammar. The store no longer copies that private naming policy.
- A failed `fdopendir()` retains RAII ownership of the duplicated descriptor;
  ownership transfers only after the directory stream succeeds.
- In-memory and durable payload sources use one compile-time service template,
  one exact claim/release frontier, and one TLS forwarding path. No
  `std::function` or caller callback is introduced while claim or channel
  authority is live.
- Five older lexical audits were updated to follow semantic ownership after the
  shared-template and resolver refactors rather than requiring retired source
  spellings.

## Validation

Final source validation completed:

- GCC 14.2 Debug focused authority graph: **2,203/2,203 assertions**.
- Clang 17 Release C++ `-Werror`: **2,203/2,203 assertions**.
- GCC 14 ASan/UBSan with leak detection and bundled SQLite instrumentation:
  **2,203/2,203 assertions**.
- Complete GCC Debug registry: **213/213 tests**.
- Audit/policy registry selection: **84/84 tests**.
- Repeated Debug payload-store/service/real-TLS boundary: **10/10 runs,
  21,420/21,420 assertions**.
- Repeated sanitizer boundary: **3/3 runs, 6,426/6,426 assertions**.
- Selected source audits: **347/347 checks across 11 audit files**.
- Package-path policy: **14/14**; verifier policy: **13/13**.
- Exact parent rev0892 ZIP: **26/26 package checks**.
- Final all-target dependency closure: `ninja: no work to do`.

One earlier serial audit-selection invocation was externally terminated while
its scheduler-policy test was outstanding. That same test passed in the full
registry and the final two-worker audit selection completed 84/84. The event is
retained as an execution-wrapper/scheduling observation, not represented as a
product test failure.

## Explicit nonclaims

Rev0893 does not provide a production daemon, cross-process capacity
serialization, garbage collection, reachability leases, dead-letter ownership,
per-peer fairness, free-space reservation, filesystem encryption, streaming or
chunk trees, hash agility, same-UID/privileged-writer defense, signed local
store provenance, cross-resource atomicity between SQLite and the filesystem,
exactly-once network delivery, formal proof, anonymity, unlinkability, endpoint
hiding, or traffic-analysis resistance.

Every snapshot still performs an O(total indexed bytes) scan and hash. That is
intentional as the current correctness oracle. A later indexed production owner
should be introduced separately and differentially tested against this full-scan
oracle rather than weakening it in place.

## Next high-value milestone

Compose this durable sender byte owner into one bounded production listener and
sender loop that uses the causal SQLite/file/TLS path as the shipped executable's
sole replica authority. Then add explicit payload reachability and garbage
collection, typed retry/dead-letter ownership, and an indexed fast path whose
results are continuously checked against the full-scan oracle.
