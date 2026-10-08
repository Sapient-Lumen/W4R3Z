# AnonSync rev0894 audit

## Heart of the mission

AnonSync is an authority-accounting system. Exact authorized history and live, owned capabilities must govern identity, content availability, causal attempt, retry, receipt, and visible effect. Digests, counters, directory listings, advisory locks, and test summaries are evidence only; none may manufacture authority.

## Highest-severity correction

Rev0893's full-scan payload owner could let two cooperative processes spend the same remaining aggregate byte or entry budget. Rev0894 holds a fail-fast exclusive lease on the exact immutable identity marker from full-scan preflight through publication or exact reconciliation; snapshots hold a shared lease through their complete scan and immutable construction. An independently opened marker must demonstrate opposite-mode exclusion before the lock is trusted.

The protocol is durably fenced by a v2 marker whose exact bytes bind the folder identity and lease protocol. A legacy v1 root is rejected without mutation. This is deliberately incompatible rather than silently sharing a namespace with lock-ignorant writers.

## Severe cursor defect

The rev0893 scanner used `dup()` before `fdopendir()`. The descriptors shared one open file description and therefore one directory offset. A completed traversal could poison the retained root cursor, causing later scans to omit the marker or payload entries. The scanner now independently reopens and re-attests the root before creating its directory stream. Normal scans require the exact move-only lease witness and re-prove that the marker path still names the locked inode after traversal and at public terminal cutpoints.

## Refactor and audit

Atomic publication and the payload store previously carried duplicate privileged descriptor-duplication helpers. They now consume one internal move-only `SyncDirectorySharedOpenDescriptionLease`, whose name and contract explicitly state that `dup()` shares open-file-description state. The repository-wide production inventory found one `fdopendir()` owner; it is now constrained to an independently reopened cursor. Marker validation is shared, the raw scanner is bootstrap-only, and mutation preflight consumes the internal scan result instead of constructing redundant public snapshots and digest projections.

Repeated testing also corrected two test-authority defects: a partially visible start-gate file is now staged, synchronized, closed, and atomically published before workers can observe it; and an absolute TLS accept deadline may truthfully expire before any `accept4()` attempt. These fixes remove false failures without weakening product assertions.

## Remaining architecture gap

The newer causal SQLite, payload, TLS, receiver-effect, and terminal-receipt owners are still not the shipped executable's sole durable authority. That composition gap remains more important than adding more isolated proof vocabulary. The full-scan store is intentionally a correctness oracle, not a scalable production catalog.

## Next work

Build one bounded production sender/listener path around the current owners, then introduce explicit content reachability and garbage collection. Add a separately designed indexed catalog under the same exclusive writer lease and continuously differentially test it against this full-scan oracle. Keep mixed-version migration offline and explicit until its evidence and rollback model are designed.

## Claim boundary

The lease is cooperative and advisory. This revision does not claim defense against noncooperating same-UID or privileged writers, universal NFS/SMB/FUSE semantics, fairness, mandatory locking, production deployment, cross-resource atomicity, exactly-once network delivery, privacy/anonymity, Windows runtime coverage, external provenance, or formal proof.
