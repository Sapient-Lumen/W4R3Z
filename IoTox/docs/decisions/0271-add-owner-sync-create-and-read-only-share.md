# ADR 0271: Add owner sync creation and read-only sharing ceremonies

Status: accepted local construction, 2026-08-31

## Context

ADR 0270 made one-writer synchronization unattended after policy installation, but the ordinary
operator path still required constructing a binary namespace policy, installing it, separately
creating automation, editing subscriber membership, and issuing an authority-ledger grant. Those
pieces are useful expert controls; they are not the product sentence for starting or sharing a sync.

The convenience layer must not hide the fact that namespace membership and signed authority are
independent mandatory checks. It also must not label a pair of `sync.publish` grants "read-write"
while the data model still has one linear writer history and no merge semantics.

## Decision

Add two owner commands:

```text
iotox sync-create NAMESPACE PATH [INTERVAL_SECONDS]
iotox sync-share NAMESPACE FRIEND read-only
```

`sync-create` is local-control v1.45 operation 95. It accepts one canonical absolute existing source,
infers `content-v2` for a regular file or `treepack-v1` for a directory, creates a manual-activation
namespace with the stable local device as its sole writer, and installs periodic publication. The
generated namespace state root is `<sync-policy-root>/data/<namespace>`, created through no-follow
owner-only directory descriptors. Source and state roots may not contain one another. Exact retries
are duplicates; an existing different namespace or automation policy is refused rather than edited.
Default namespace quotas remain explicit product limits, and treepack-v1 remains a whole-directory
archive rather than a per-file delta engine.

`sync-share` reads RecallRoot from standard input. Local-control operation 96 resolves the currently
application-ready friend to the stable device key bound by its exact v3 authority session, verifies
that the reconstructed key is the active local owner, and prepares at most one `sync.subscribe`
grant. A new peer receives the exact `viewer`/`sync.subscribe` grant. An existing active principal
retains its role and every existing capability while `sync.subscribe` is added. The client validates
and signs the prepared body with RecallRoot.

Operation 97 rechecks that the same friend still exposes the same stable device key, commits the
signed grant when needed, then adds only that principal to the namespace subscriber set. It never
adds a writer. If authority commits but namespace mutation must wait for quiescence, the partial state
is safe: a global capability without namespace membership grants no synchronization entrance, and an
exact retry completes membership without another ledger mutation. Existing automatic publication
does not need to be disabled for this subscriber-only change.

`sync-share ... read-write` is a recognized but explicitly refused request. Granting
`sync.publish,sync.subscribe` is only an authority primitive; it does not create a convergent writable
folder. No peer framing or negotiated feature bit changes in this ADR.

## Bidirectional prerequisite

A real read-write share requires a separate multiwriter protocol and product gate:

1. replace whole-tree treepack publication with a signed per-file CAS tree;
2. keep an independent monotonic branch HEAD per stable writer instead of competing for one linear
   namespace HEAD;
3. define parent sets and explicit merge commits so causality never depends on wall-clock order;
4. materialize conflicts with both writer identities and source revisions intact;
5. define signed deletion tombstones, delete-versus-edit conflicts, archive/restore, and retention;
6. create a writable local projection with filesystem observation, rename/metadata rules, ignore
   policy, and feedback-loop suppression;
7. extend reachability and quarantine GC so every live branch, merge parent, conflict, and tombstone
   remains rooted;
8. specify revocation semantics for outstanding branches and offline writes without erasing signed
   provenance; and
9. qualify concurrent offline edits, reconnect, crash/restart at every commit edge, malicious forks,
   bounded conflict storms, and convergence in isolated Sandwurm guests.

Until all nine exist, IoTox supports one authoritative writer and read-only replicas, not a Resilio-
style bidirectionally editable folder.

## Consequences

Starting a local sync is now one command, and granting one connected stable device read access is one
RecallRoot-authenticated command. Expert namespace and authority controls remain available for audit,
custom quotas, local replica roots, and recovery. A recipient still installs its own host-local
namespace policy and grants the writer `sync.publish` before `sync-follow`; a future invitation/
`sync-accept` ceremony may compress that local setup without making remote policy authoritative.
