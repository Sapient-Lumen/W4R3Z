# ADR 0273: Enable pairwise tree-v2 bidirectional synchronization

Status: accepted and Sandwurm-qualified on the founding host, 2026-08-31

## Context

ADR 0272 froze the local multiwriter data model but intentionally advertised no feature and exposed
no read-write command. Enabling it requires more than sending manifests: a receiver must acquire the
complete signed causal proof graph, commit bytes and metadata in the right order, bind every action
to current v3 authority, and preserve recipient control of its local path.

The first operator surface also needs a narrow topology. The branch format supports a bounded writer
set, but an unattended scheduler that opportunistically selects any writable peer would make route,
revocation, and partial-membership behavior ambiguous before those policies are qualified.

## Decision

Enable feature bit 30 as `state-sync-tree-v2` when synchronization services are active, and reserve
lossless message types 32 through 35 for bounded inventory request/result and object request/result
frames. Tree-v2 initially uses only the primary authenticated Tox carrier and one exact object
transfer at a time.

The publisher authorizes `sync.subscribe` against current namespace membership and the exact
authority/session epoch. Replay entries bind request bytes, authority head, stable principal,
capabilities, friend, and online epoch. A conflicting message ID, changed authority, or exhausted
replay bound fails closed.

The subscriber authorizes the peer's `sync.publish`, requires negotiated tree-v2 on the primary
lane, and walks the complete predecessor and observation closure from the advertised frontier. It
fetches and verifies branch records, manifests, and file objects under namespace quotas. File CAS
objects commit first. Branches become current only after their complete dependency closure is
durable and topologically acceptable. Writable reconciliation is the final effect. Offline peers,
authority changes, malformed results, and transfer failures close the job and remove its exact
staging lane. Terminal jobs are pruned before admitting later bounded work; restart removes only
canonical crash-left receive-part names.

Expose the ordinary pairwise ceremony:

```text
sync-create NAMESPACE ABSOLUTE_DIRECTORY read-write [INTERVAL_SECONDS]
sync-share NAMESPACE FRIEND read-write
```

`sync-create` installs engine 4, the local stable device as writer, signed `writable` automation, and
an initial local branch. `sync-share` is an owner prepare/sign/commit transaction. It resolves the
current exact-v3 stable peer principal, grants both `sync.subscribe` and `sync.publish`, adds that
principal to subscriber and writer membership, and converts the existing local writable automation
to `bidirectional` bound to that exact principal. Existing lawful roles/capabilities are preserved
when their ceiling permits. A different peer cannot replace the automation binding implicitly.

Both devices must independently create a namespace at a locally chosen path and run the share
ceremony. There is no remote path selection and no implicit invitation acceptance. The scheduler
reconciles local changes before every pull, then requests the peer frontier. This preserves offline
edit causality even if remote inventory arrives immediately after reconnect.

`sync-publish`, `sync-pull`, `sync-status`, and `sync-repair` understand tree-v2. Repair verifies the
signed frontier and every unique referenced CAS digest with checked byte accounting.

## Consequences

IoTox now has an operator-visible pairwise editable-directory protocol whose conflict behavior is
defined by signed causal history rather than arrival order. The same stable identity and owner
ledger govern connectivity, publication, subscription, and local automation; no second sync trust
root is introduced.

The first surface is intentionally narrower than the format. Automatic topology is one exact remote
principal per namespace, inventory advertises at most the wire-format writer bound, and file objects
do not yet use content-v2 ranges or auxiliary-route striping. Each scan and changed projection may
touch the complete tree. Symlinks, rich metadata, ignores, archive/restore, permanent purge,
multi-branch GC, revoked-writer cutoff, conflict-storm bounds, and independent-host qualification
remain open.

The `sync-bidirectional` Sandwurm cell is the acceptance gate. Two isolated guests perform reciprocal
RecallRoot ceremonies, converge two writer branches, stop both daemons, edit the same path
independently, restart, require the same canonical projection and retained losing value, resolve with
a later causal edit, propagate a deletion and zero-byte file, and pass repair without manual
publish/pull after setup.

That gate passes over observed direct UDP in compact proof `pair.ms5zsk9l`. The independent verifier
binds two simultaneous source-linked VM chains, the exact shared binary, both content-free receipts,
one restart per role, conflict and resolution observations, and the final empty-file digest. The
retained evidence and exact nonclaims are recorded in
`../evidence/2026-08-31-sandwurm-sync-bidirectional.md`.
