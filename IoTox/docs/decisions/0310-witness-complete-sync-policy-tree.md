# ADR 0310: Witness the complete synchronization policy tree

- Status: accepted and implemented for the opt-in sync-policy lane
- Date: 2026-09-02

## Context

IoTox synchronization separates authority, owner-local namespace policy, signed automation policy,
and the per-namespace data/state machines. The authority ledger decides which principals may
publish or subscribe, but it does not stop a storage attacker from restoring an older valid local
namespace membership, projection rule, source set, source path, or automatic-effect schedule.
The existing stable-device signatures on automation records prove authorship and integrity, not
freshness; namespace policy records are owner-private canonical records rather than signed records.

Witnessing only one file or one current namespace would leave coordinated whole-tree rollback
available. Conversely, folding content-addressed objects, accepted heads, workspaces, maintenance,
and rollback guards into the same low-frequency policy lane would couple policy administration to
high-churn data transfer and destroy the existing per-namespace transaction boundaries.

## Decision

Add a separately enrolled `sync-policy` witness lane. Its exact semantic tree contains every
strictly loaded namespace policy and every stable-device-signed automation policy beneath one
configured policy root. Records are sorted by namespace identifier, duplicates are rejected, each
canonical record is length-bound, and the complete value is hashed in the closed
`iotox-sync-policy-tree-v1` domain. Namespace roots, source paths, membership, projection rules,
quotas, engines, activation rules, automation modes, intervals, source principals, generations, and
signatures are therefore committed. The remote witness stores only the digest and position.

`iotox witness-sync-policy-enrollment --config PATH` creates the device-signed no-replace
enrollment for the current exact tree. Witnessed mode requires an already initialized strict policy
store, which may be empty, plus `--enable-sync`, `--sync-policy-root`, and the complete authenticated
witness-service selection.

At startup, `--witness-sync-policy` loads and hashes the complete tree, reconciles it against the
external committed head, rereads it to reject a concurrent change, and freezes that exact snapshot
before RuntimeTree, networking, or synchronization automation exists. Namespace and automation
lookups use the frozen snapshot for the lifetime of that Agent.

Every Agent-mediated namespace or automation mutation is serialized across both policy classes.
The candidate records become durable first, the exact candidate tree advances through the generic
signed-intent and authenticated pending/committed CAS, and only then is the frozen runtime snapshot
replaced and the live namespace registry or automation scheduler reloaded. If that transition is
unavailable or disagrees, the new disk records remain uncommitted and unusable. Retrying the same
operation can finish the transition safely.

An offline administrator must stop the Agent, make the reviewed edit, run
`iotox witness-sync-policy-commit --config PATH`, and restart. The commit command rereads the exact
tree after CAS and reports a concurrent change as uncommitted. A running Agent deliberately does
not adopt a policy committed by a second process; restart is the activation boundary.

The default signed checkpoint is a sibling of the policy root,
`SYNC_POLICY_ROOT.sync-policy-witness-checkpoint`, with `.intent` appended for its durable intent.
Both are included in protected-state closure. They cannot live inside the strict policy root because
that root admits only the reviewed namespace, automation, and managed-data structure. Diagnostic
structural commitment v7 exposes only whether this lane is required.

## Consequences

One owned check brings the direct registry to 783. It proves stable empty, namespace-only, and
namespace-plus-automation commitments and duplicate refusal. The retained generic policy-witness
suite covers exact advancement, interrupted-CAS joins, and old tree/checkpoint refusal. The
two-guest source-linked service gate enrolls an empty tree, performs a live `sync-create` whose
namespace and automation each advance the lane, then restores the complete enrolled-empty policy
view and matching local checkpoint while the remote witness stays current. Startup refuses before
RuntimeTree.

This lane prevents rollback of the configuration that decides what synchronization may do. It does
not witness accepted/published heads, pins, rollback guards, branches, cutoffs, workspace or
maintenance state, object inventories, content, projections, or current pointers. Those remain the
separate per-namespace guarded-state freshness gate. It also does not make the same-host VM witness
independent, protect an unlocked live kernel, certify filesystem content, or provide backup.
