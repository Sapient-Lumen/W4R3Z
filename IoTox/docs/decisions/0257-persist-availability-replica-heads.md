# ADR 0257: Persist availability-only replica HEADs

Status: accepted, 2026-08-30

## Context

ADR 0256 qualified failure and explicit recovery after one selected content-v2 source disappeared.
The secondary source held complementary immutable objects for a HEAD signed by the primary source.
Putting that foreign-writer record in `published-heads/` was correctly rejected at cold start: a
publication record means the local device authored it. The construction therefore had to withhold
the record during restart and inject it again after readiness. That preserved the authority boundary
but was not a production restart design.

A partial source needs durable knowledge of the exact graph it can serve. That knowledge must not
become HEAD acceptance, activation, local publication, or remote writer authority.

## Decision

Add an owner-local `sync-replica-import NAMESPACE SIGNED_HEAD_PATH` operation. Local-control v1.42
allocates operation 89 to its canonical namespace-plus-296-byte-SignedHead payload.

An import is admitted only when:

- the namespace is content-v2 and the original signed HEAD verifies under its current writer set;
- the original writer is not the local device;
- the complete root/page manifest graph is already verified in local CAS, although artifact chunks
  may be absent;
- the first local replica has any valid generation, while every later nonduplicate import has the
  same writer and is one exact parent-linked bounded advance; and
- the local device can sign a fixed `IOTXRPH1` custody envelope over its principal and the complete
  original signed record.

Store that envelope as the private fixed-size
`ROOT/replica-heads/NAMESPACE.replica-head`. Never copy it to `published-heads`, `accepted-heads`, or
activation state. Publisher services prefer a legitimate local publication and use the replica only
when publication is absent. A subscriber still accepts its primary HEAD only from the authenticated
writer; a replica can answer exact availability and immutable-object requests for an already frozen
record, but cannot originate or replace that authority.

Content reachability treats the verified replica manifest graph and every locally present named
chunk as live. Missing replica-only chunks are expected rather than corruption. A missing/corrupt
root or manifest page makes traversal incomplete and disables GC classification. Whole-artifact CAS
is not required for a partial replica.

The Sandwurm selected-source-loss gate must now import the foreign HEAD exactly once, prove no
foreign publication file exists, stop the selected source after positive work, cold-start it without
post-start injection, obtain a consistent zero-candidate GC plan from the partial store, reconnect at
a higher authenticated epoch, and converge only through a distinct explicit atomic pull.

## Consequences

The stored record is authenticated twice for two different claims: the remote writer signature says
which revision exists, and the local device signature says which exact revision it is willing to
cache and serve. Neither signature grants activation. Current namespace policy can revoke the remote
writer and thereby make the replica unloadable.

This is one replica HEAD per namespace and one writer chain. Writer changes require an explicit
future operation rather than implicit replacement. Filesystem rollback of this cache can reduce
availability but cannot make the replica the subscriber's primary writer or activate content.
Coordinated rollback of policy, device custody, and the true writer remains outside software-only
rollback resistance; hardware counters or an independent owner witness are still separate work.

This decision does not add network replica discovery, automatic replication, source continuation
inside a failed job, forced-TCP qualification, multiple replica writers, or garbage purge.

## Evidence

The direct-UDP Sandwurm proof `pair.w_ws202c` passed in raw and compact form. It cold-started the
partial source with no published HEAD and no post-start injection, reported a complete consistent
zero-candidate GC plan, advanced the same authenticated source from epoch 1 to epoch 2, and converged
only through a distinct recovery job. Exact bindings and nonclaims are retained in
`evidence/2026-08-30-sandwurm-sync-content-replica-restart.md`.
