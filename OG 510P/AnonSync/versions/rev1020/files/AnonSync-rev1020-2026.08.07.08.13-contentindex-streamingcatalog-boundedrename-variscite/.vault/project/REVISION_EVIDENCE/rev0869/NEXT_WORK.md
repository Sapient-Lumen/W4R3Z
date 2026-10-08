# Next work after AnonSync rev0869

## 1. Authenticate the operation authority

Add a canonical authenticated envelope binding operation bytes to folder epoch,
actor key, actor epoch, membership epoch, and algorithm suite. Specify rotation,
revocation, recovery, old-epoch rejection, compromised-device treatment, and
key-loss behavior. Preserve exact evidence separately from current trust
verdicts so revocation can reproject without rewriting history.

## 2. Turn outbox intent into a bounded sender state machine

Add point-read delivery leasing, in-flight generation, attempt count, bounded
backoff, wake condition, expiry semantics, exact settlement, and restart
recovery. Keep one canonical operation row and lightweight per-destination
state. Differentially compare every point-read result with the current global
restore until equivalence is established.

## 3. Build an incremental projector without weakening restore

Identify affected dependency and path subgraphs, update only changed evidence
states/heads/visible rows, and preserve the global O(history) oracle for tests,
periodic audit, and repair. Add randomized differential tests across reorder,
missing parents, forks, cycles, revocation, and policy changes.

## 4. Exercise two actual replica processes

Create an authenticated two-process vertical slice with bounded head/dependency
exchange and exact operation requests. Crash at sender publication, transfer,
receiver admission, receiver commit, ACK publication, and sender retirement.
Prove restart preserves canonical validity, trust, applicability, retention
availability, and exact sender ownership independently.

## 5. Bind payload materialization

Add chunk identities and final content commitment to the operation envelope.
Verify all bytes before filesystem-visible publication, use the existing atomic
file owner, and prove database/filesystem recovery cannot expose a file without
its exact committed operation or an operation without recoverable payload
ownership.

## 6. Add retention lifecycle authority

Define causal stability/checkpoint certificates, compaction, tombstone
collection, old-replica rejoin, revoked-history service, and reserved recovery
capacity. Age, local visibility, or current heads alone must never authorize
deletion.

## 7. Measure physical resources and deadlines

Semantic byte/count limits are deterministic but not actual usage. Measure and
bound SQLite pages, WAL and checkpoint behavior, snapshots/backups, filesystem
blocks, payload staging, RSS, allocator overhead, CPU, and wall time. Add hard
work ceilings before exposing full restore to arbitrary remote input.

## 8. Add fairness and privacy as first-class protocols

Authenticate identity before expensive work, bound unknown-identity activity,
add per-principal quotas and reserved recovery capacity, and analyze Sybil
pressure. Write an anonymity/metadata threat model covering membership,
operation timing, dependency graph shape, path leakage, pressure responses,
retry timing, padding, session linkage, forward secrecy, and compromise
recovery.
