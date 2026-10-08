# Rev0866 next work

## P0: authenticated SQLite-to-wire vertical slice

Implement one file/tombstone operation through the real product path rather
than broadening the in-memory oracle again.

1. Define an authenticated canonical envelope containing protocol version,
   folder/object identity, actor key and epoch, membership epoch, unique dot,
   exact parent IDs, payload commitment, operation value, and all resource
   limits. Publish independent byte-level test vectors.
2. Select and document actor authorization: enrollment, signing or MAC key
   possession, rotation, revocation, recovery, and the policy for evidence
   signed before and after a trust change. A caller-provided device string is
   not authority.
3. Add immutable SQLite evidence and parent-edge tables plus local actor state,
   exact head state, and outbox intent. In one transaction reserve the next
   counter, freeze/sign bytes, insert evidence and edges, replace heads, and
   append retry intent.
4. Inject failure and process-crash cutpoints at every statement boundary and at
   ambiguous commit outcomes. Restore must reconstruct from immutable evidence
   and trust state, never trust a cached active verdict, and match the pure
   projector exactly.
5. Exchange heads and missing nodes over a real authenticated two-process
   channel. Apply envelope, parent fan-in, unresolved-dependency, peer-memory,
   disk, retry, traversal-work, frame, wire-byte, and time budgets before
   amplification.
6. Bind chunk requests, chunk bytes, final file digest, staging, rename, and
   tombstone publication to the operation ID and payload commitment. Preserve
   every concurrent nonprimary value until explicit policy cleanup.

## P0: hostile-fork and trust semantics

The current same-dot rule is deterministic but unauthenticated. Specify whether
unauthorized evidence is discarded, retained separately, or participates in an
accountability log. Define how key compromise, revocation, membership changes,
and recovered devices reclassify descendants without allowing a cheap forged
fork to suppress honest history. Differentially test every trust transition
against a pure reference state machine.

## P1: incremental projector

Keep `SyncReplicaEvidenceProjection` as the global oracle. Add indexes for dot,
parents, children, unresolved dependencies, actor maxima, heads, and affected
paths. On admission or trust change, recompute only the reachable affected
subgraph. Compare every incremental verdict and digest with a fresh global
projection over deterministic random graphs, fork insertion orders, restore,
and deletion-free compaction candidates.

## P1: bounded anti-entropy and storage

Replace full-set broadcast with head/Merkle summaries and dependency pull.
Separate authenticated admission from storage quotas so a valid member cannot
exhaust the replica. Define acknowledgements or causal-stability frontiers
before deleting tombstones, fork evidence, payloads, or operation nodes. Verify
that a long-disconnected authorized replica can still catch up and that deleted
values cannot resurrect.

## P1: SQLite operational gate

The cube bundles SQLite 3.53.3, which is newer than the 3.51.3 fix for the 2026
WAL-reset corruption bug. Production should still assert the linked runtime
source ID, pin and verify the amalgamation, document journal/synchronous and
checkpoint policy, keep database/WAL/SHM state together, bound WAL growth, and
run concurrent writer/checkpointer plus power-loss simulations at the real
operation transaction.

## P2: privacy threat model

State which observers matter: direct peers, relays, discovery services, local
network observers, global passive observers, malicious folder members, seized
devices, or compromised keys. Inventory exposed identifiers, folder membership,
path and size metadata, timing, traffic volume, peer graph, and recovery state.
Only then evaluate private discovery, relays/onion routing, padding, cover
traffic, unlinkable credentials, forward secrecy, and post-compromise recovery.

## Work to avoid

Do not treat hashes as authentication, vector summaries as possession, a
passing lexical audit as semantic proof, a deterministic winner as convergence,
or retained unbounded evidence as safe merely because it is immutable. Do not
add compaction before causal stability or optimize away the pure projector
before an incremental implementation has a differential corpus.
