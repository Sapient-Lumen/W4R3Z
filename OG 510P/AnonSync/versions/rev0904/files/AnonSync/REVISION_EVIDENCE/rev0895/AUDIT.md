# AnonSync rev0895 audit

## Heart of the mission

AnonSync is an authority-preserving convergence engine. Exact authorized history and live, owned capabilities must remain the sole source of identity, payload availability, causal selection, attempt, retry, receipt, and visible filesystem effect. Digests, counters, indexes, logs, metrics, and test summaries are subordinate evidence; they may accelerate or explain authority but may not manufacture it.

## Highest-severity correction

Before this revision, the strongest causal SQLite, durable payload, mutual-TLS, receiver-effect, and terminal-receipt owners existed mainly as separately tested islands. The shipped `anonsync_core` executable was a diagnostic/self-test surface, not a composition of those owners. Rev0895 adds a production TLS client and a separate `anonsync_replica` executable that can enqueue content, publish anchored membership, send one delivery, or serve one delivery without linking self-test implementation libraries.

The outbound authority order is now explicit: numeric socket connect, TLS 1.3 handshake, peer certificate/SPKI verification, actor authorization, and payload preflight all precede the SQLite claim. Only after authentication may the guarded request-prefix frontier consume an outbox claim. Failures after that frontier preserve ambiguity rather than incorrectly releasing authority.

## Process proof and defects it exposed

A registered two-process test now composes two databases, durable payload storage, anchored membership, real TCP, mutual TLS/SPKI identity, guarded dispatch, receiver filesystem publication, exact receipt settlement, and close-notify. It exposed and corrected three integration failures hidden by in-process tests: impossible fresh membership genesis, a guessed request-frame budget smaller than the protocol evidence envelope, and an executable that could never lease work because the default container clock correctly reported synchronization authority as unknown.

The receiver's refusal to invent parent directories remains intentional. Directory creation, tombstones, rename/type conflicts, symlink policy, and metadata convergence need causal operations rather than convenience side effects.

## Waste and drift

The project had an assurance/product inversion: rigorous owners and thousands of checks accumulated without a shipped vertical path. The CMake graph remains fragmented (88 textual `add_library` calls, 102 executables, 185 link declarations, and 214 registered tests), and giant legacy units still dominate change/build cost. Two synchronization architectures coexist, the public state vocabulary is oversized, and the evidence tree has become a second product. These are not reasons to weaken correctness; they are reasons to consolidate targets, isolate legacy surfaces, make the product spine the default integration point, and measure evidence retention.

## Missing work, ordered

P0 is acquisition and exact verification of SQLite 3.53.4; this tree still contains 3.53.3 and makes no upgrade claim. P1 is a durable bounded peer loop with status, recovery, shutdown, rotation, scheduling, backoff, and real restart tests. Other P1 work is causal directory/deletion/rename semantics, reachability and crash-safe garbage collection, and a separately owned indexed catalog continuously checked against the full-scan oracle. P2 is a published privacy threat model, capability-private partial synchronization and overlap discovery, key evolution/compromise recovery, and external artifact-bound provenance.

## Claim boundary

This revision proves a bounded one-shot composition, not a daemon or mature sync product. It does not claim discovery, NAT traversal, scheduler fairness, directory/tombstone/rename convergence, chunking/resume, reachability, garbage collection, indexed performance, exactly-once network delivery, cross-resource atomicity, at-rest encryption, anonymity, unlinkability, endpoint hiding, traffic-analysis resistance, hostile same-UID/privileged-writer resistance, universal network-filesystem semantics, Windows runtime coverage, external signed provenance, or formal proof.
