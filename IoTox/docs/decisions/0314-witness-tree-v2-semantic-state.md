# ADR 0314: Witness tree-v2 semantic state

- Status: accepted and implemented for the opt-in tree-v2 state lane
- Date: 2026-09-02

## Context

ADR 0312 externally anchors the four single-writer synchronization roots, but correctly refused
`tree-v2`: multiwriter truth lives in a set of signed branch pointers, a signed workspace exchange
journal, and signed maintenance pins and terminal writer cutoffs. Restoring that complete set to an
older internally valid snapshot could resurrect an old frontier, forget a cutoff, or move the
writable projection backward even while the complete namespace-policy tree remained current.

The new commitment must retain tree-v2's existing independently advancing writer branches and
crash-forward workspace protocol. It must not turn immutable history or object presence into a false
backup claim, serialize unrelated namespaces into one global lane, or let an unconfigured Agent path
silently fall back to local-only state.

## Decision

Add one separately enrolled `tree-v2-state` witness record for each tree-v2 namespace. Its 128-bit
service domain is derived from a distinct fixed domain tag, the configured base domain, stable device
public key, and length-bound namespace ID. The ordinary epoch and lane 10 complete the selector, so
it cannot collide semantically with lane 9's four-root record for the same namespace name.

The semantic digest binds the namespace ID, normalized root, tree-v2 engine, every quota, and:

- the canonical writer-sorted live branch frontier as exact writer, generation, and complete signed
  branch-record digest tuples;
- the exact stable-device-signed maintenance state, including mutation chain, pins, and terminal
  writer cutoffs, or canonical absence; and
- the exact stable-device-signed workspace state, including stable/pending phase, active and pending
  manifests/frontiers, worktree identity, and generation, or canonical absence.

Each live branch record transitively commits its signed head and manifest. Object bytes, immutable
history presence, incoming transfers, quarantine, health, replay caches, source evidence, worktree
bytes, and projection-marker/current-pointer state are deliberately outside the freshness digest.
Their integrity and availability rules remain separate.

`iotox witness-sync-guarded-enrollment --config PATH NAMESPACE` now selects this lane when the
externally verified frozen policy says the namespace is tree-v2. It acquires the namespace
transaction and emits a device-signed no-replace record at position 1 for the exact quiescent state.
The prerequisite `sync-policy` lane freezes the full namespace population and immutable storage
identity; every namespace must be explicitly enrolled before selected startup. Live namespace
addition/removal remains refused while per-namespace witnessing is enabled.

A compact stable-device-signed `IOTXTVG1` guard retains the current and optional successor semantic
digests. Under the existing namespace transaction, each authoritative branch, workspace, or
maintenance mutation executes:

1. reconcile the exact local state/guard with the authenticated externally committed head;
2. durably sign and write the local pending successor;
3. durably commit exactly one authoritative local root;
4. compare-and-swap the external predecessor to its pending successor;
5. durably finish the local guard at that successor; and
6. compare-and-swap the external pending record to committed successor.

The branch-pointer retirement move used by a writer cutoff fsyncs both source and retired
directories inside step 3, before external advance. Every ordinary branch acceptance/publication,
workspace initialize/begin/finish, maintenance pin/unpin/cutoff, checkpoint, forward restore, pull,
automation, service offer, time-machine operation, and GC reachability path uses the witness-aware
store or verifies the cached authenticated semantic head while holding the namespace transaction.
Missing Agent registry entries are errors, never legacy fallback.

Recovery clears a pending guard only for local-old/external-old, advances external state for
local-new/external-old, and completes the exact successor for local-new/external-pending or
local-committed/external-pending. A third local head, old local state beside an external pending or
committed successor, same-position fork, wrong selector, malformed guard, missing enrollment, or
unavailable service refuses. Startup reconciles every frozen namespace before RuntimeTree.

## Consequences

Thirteen owned checks bring the direct registry to 817. They cover 64-way namespace separation plus
base-domain/device separation, storage identity and all three semantic-root classes, branch,
workspace, pin and unpin advancement, root-landed and root-not-landed recovery, every supported
local/external pending join, lost replies on both remote CAS steps, old complete-state replay,
selector/digest/pending/third-head forks, guard signature/link metadata, stale early-return refusal,
and a concurrent reader held behind the namespace transaction until external commit.

The retained two-guest gate now enrolls 11 authenticated records including one existing tree-v2
namespace. It advances that namespace, restores its complete older local tree state while lane 10
remains current, observes startup refusal before RuntimeTree, restores exact-current state, and
restarts. Both guests still share one construction host and administrator.

This closes the accepted tree-v2 frontier/workspace/maintenance freshness slice. It does not certify
content availability, complete custody, backup, health freshness, worktree correctness, safe
permanent deletion, service independence, or a continuously renewed single-active lease. An
independently running clone can advance the service after this process's last authenticated
startup/mutation query; continuous clone fencing requires a separately designed expiring lease.
