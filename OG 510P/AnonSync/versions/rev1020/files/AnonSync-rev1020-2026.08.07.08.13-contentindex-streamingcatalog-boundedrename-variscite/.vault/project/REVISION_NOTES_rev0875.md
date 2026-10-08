# AnonSync rev0875 revision notes

## Truthful time-namespace capability

The uploaded rev0874 archive built cleanly in this cloudtainer but passed 175 of
176 registered tests. Its Linux clock source treated a kernel release at or after
5.6 as proof that `/proc/thread-self/ns/time` must be observable. This container
runs Linux 6.12.13 but exposes no time-namespace handle, so the source threw before
the owner could durably record why lease authority was unavailable.

Rev0875 replaces that inference with a typed probe classification. Only a
successful `stat` proves a bound calling-thread time namespace. Missing or
permission-hidden identity is retained as explicit unavailable evidence, forces
synchronization quality `Unknown`, and enters sticky durable quarantine. An
unexpected probe error remains fatal. The kernel release is only a diagnostic
feature-generation hint.

A new additive anomaly, `SynchronizationUnknown`, keeps unavailable capability
distinct from a positive kernel report of `Unsynchronized`. Existing anomaly
values and the versioned canonical state codec remain compatible.

## Two-database ambiguity frontier

A new integration test composes two independent `SyncReplicaSqliteOwner`
databases. It sends one canonical operation, commits it at the receiver, models a
sender crash before settlement, blocks an early retry, claims a fresh attempt at
expiry, receives an exact duplicate without receiver rewrite, settles with the
fresh receipt, and rejects replay of the stale first receipt.

This proves the recent owner abstractions compose across independent SQLite
cutpoints under an ambiguous response. It remains a test-level seam: no socket,
transport authentication, payload materialization, filesystem effect, or signed
terminal receipt is claimed.

## Mission finding

The strongest recent causal path is not used by the shipped `anonsync_core`
executable. The newer replica model, outbox, owned clock, and SQLite owner are
linked into a focused test/audit island, while the executable follows the older
sync-domain, peer-ingress, replay-ledger, local-transport, and runner stack. The
next priority is one narrow production service that consumes
`SyncReplicaSqliteOwner` end to end.

## Waste finding

The archive contains roughly 4,473 historical evidence files and 40 MB of
extracted revision evidence before rev0875. CMake exposes 66 libraries, 89
executables, and 179 literal tests while major semantic centers remain giant
translation units. Rev0875 keeps its new evidence compact. Future work should
externalize bulk signed artifacts, simplify repetitive build wiring, split true
semantic monoliths, and distinguish fast authority suites from full legacy
regression gates.

## Focused proof surface

- owned clock runtime: 53 checks;
- pure lease runtime: 37 checks;
- SQLite owner runtime: 198 checks;
- owned clock structural audit: 24/24;
- lease structural audit: 19/19; and
- SQLite owner structural audit: 38/38.

The complete GCC Debug graph built and its final dependency closure was no-work.
One CTest invocation passed 176/176. Clang 17 Release C++ `-Werror` and GCC 14
ASan/UBSan each passed all 288 focused checks; owner stress passed 20/20 and
3,960/3,960 checks. Final projection, manifest, and package-verifier evidence is
recorded in `RELEASE_GATE.json` and `REVISION_EVIDENCE/rev0875/`.

## Deliberate nonclaims

The capability repair does not prove that time namespaces are absent or present
when their identity is unavailable; it proves only that this process cannot bind
the required identity and therefore cannot mint synchronized liveness authority.

The two-database test is not authenticated transport or receiver filesystem
publication. The O(history) owner remains a correctness oracle rather than a
production throughput claim. Anonymity, complete membership/key lifecycle,
compaction, exactly-once effects, trusted time, malicious-host resistance, and
externally signed build provenance remain open.

See `TIME_NAMESPACE_CAPABILITY_AUDIT_rev0875.md` for the full mission analysis,
root cause, architectural split, online research, waste audit, speculative
roadmap, and nonclaims.
