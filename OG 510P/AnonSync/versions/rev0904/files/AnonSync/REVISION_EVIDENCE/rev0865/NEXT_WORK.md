# Rev0865 next work

## P0: bind one immutable event through SQLite and transport

Implement one narrow production vertical slice for a single file/tombstone
operation:

1. Define canonical operation-envelope bytes containing version, folder/object
   identity, actor/key epoch, unique counter/dot, predecessor heads or hashes,
   file/tombstone value, payload digest, and membership epoch.
2. Add authenticated provenance. Choose and document the signing/MAC and key
   ownership model before treating `device_id` as authority.
3. In one SQLite transaction, reserve the next local event, persist exact
   envelope bytes and authentication, update causal heads, and insert an outbox
   row. The transaction must be replay-safe and crash-testable.
4. Add an inbox/evidence table that stores immutable nodes independently of
   activation state. Preserve conflicting fork evidence rather than discarding
   whichever branch arrives second.
5. Implement a deterministic validator/projection that classifies nodes as
   active, pending dependency, forked/quarantined, revoked, or malformed solely
   from the shared evidence and membership state.
6. Exchange heads and missing operation nodes over a real authenticated
   two-process transport. Enforce count, semantic/wire byte, frame, dependency,
   retry, and time budgets before amplification.
7. Bind chunk requests and final filesystem publication to the operation ID and
   exact content digest. Keep concurrent loser files until explicit policy
   cleanup.
8. Differentially compare operation-set and visible-state results with
   `SyncReplicaModel` across deterministic schedules and crash cutpoints.

## P0: resolve the model's honest-operation limitation

Extend the reference semantics so same-dot forks and missing predecessors are
retained as evidence and classified deterministically after all relevant nodes
arrive. The same evidence set must produce the same active/quarantined set
regardless of arrival order. Add exhaustive small-state permutations before
claiming Byzantine resilience.

## P1: anti-entropy and causal stability

Replace full-history exchange with bounded head/Merkle summaries and dependency
pull. Define acknowledgements or stable frontiers before compaction, tombstone
GC, or conflict-evidence cleanup. Prove that deletion cannot resurrect a value
or prevent a disconnected authorized replica from catching up.

## P1: identity and membership lifecycle

Specify enrollment, device/key rotation, epoch creation after lost counter
state, revocation, folder membership changes, recovery, and compromised-key
handling. A numeric caller-provided epoch is not sufficient production
authority.

## P1: move testing from oracle-only to implementation differential

Inject SQLite busy/failure/crash cutpoints, process termination, truncated or
replayed frames, partial payloads, reconnects, duplicate outbox sends, and
reordered dependencies. Compare the durable implementation after every restart
with the pure semantic oracle.

## P2: privacy and anonymity threat model

State which observers and compromises matter: direct peers, relays, local
network, global passive observers, directory services, seized devices, or
malicious members. Then evaluate metadata-minimizing identifiers, private
membership discovery, relay/onion topology, traffic padding or cover traffic,
and key unlinkability. Do not equate TLS or Noise with anonymity.

## Work to avoid

Do not resume a long sequence of unrelated local authority wrappers while the
operation protocol remains absent. Do not add compaction before causal stability
exists. Do not treat a hash as authentication, a version vector as a unique
write ID, a deterministic winner as proof of valid history, or a passing lexical
audit as a distributed-semantics proof.
