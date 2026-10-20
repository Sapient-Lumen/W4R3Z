# ADR 0312: Witness per-namespace synchronization four-root state

- Status: accepted and implemented for the opt-in non-tree-v2 four-root lane
- Date: 2026-09-02

## Context

ADR 0103 gave every synchronization namespace a stable-device-signed two-head rollback guard over
the published, accepted, activated, and retained roots. It makes an interrupted replacement
recoverable and rejects isolated rollback or a third head. A storage attacker can nevertheless
restore all four roots and the matching guard as one older, internally valid snapshot.

ADR 0310 externally commits the complete namespace and automation policy tree, but deliberately
does not put high-churn namespace state in that low-frequency lane. A per-namespace freshness gate
must not allocate one global lane whose unrelated namespaces block each other, depend on policy
ordering, or imply that tree-v2's different multiwriter frontier is covered.

## Decision

Add a separately enrolled `sync-guarded-state` witness lane for every selected non-tree-v2
namespace. Its 128-bit witness domain is derived from the configured base domain, stable device
public key, and length-bound namespace ID. The ordinary witness epoch and lane 9 complete the
selector. This preserves the existing service wire record while collision-separating up to the
policy limit of 64 namespaces independently of record ordering.

The semantic digest binds the immutable storage identity—namespace ID, normalized root, engine,
and every quota—plus the exact fixed-order `(counter, record-digest)` values for the signed
published, accepted, activated, and retained roots. Membership, activation rules, automation, and
projection policy remain in the prerequisite `sync-policy` lane. `tree-v2` is refused because its
branch frontier, workspace, and maintenance/cutoff state do not mutate these four roots.

`iotox witness-sync-guarded-enrollment --config PATH NAMESPACE` first authenticates and freezes the
complete externally committed sync-policy tree, then acquires the namespace transaction and emits
one device-signed no-replace enrollment at position 1 for the exact quiescent four-root head. It
rereads the policy tree before returning. Every namespace in the frozen tree must have its own
service enrollment before witnessed startup. Live namespace addition or removal is refused; the
bounded workflow is stop Agent, commit the complete policy change, enroll the new namespace if any,
then restart. IDs cannot be silently reused with another storage identity.

The existing signed rollback guard is also the durable local transition intent. Under the one
namespace transaction, a root mutation executes:

1. reconcile the exact local guard/roots with the authenticated externally committed head;
2. write `guard.pending = next` while retaining the exact committed predecessor;
3. atomically replace the one root file;
4. compare-and-swap the external committed predecessor to pending successor;
5. finish the local guard at the successor; and
6. compare-and-swap the external pending record to committed successor.

Ambiguous replies are resolved by authenticated query and exact idempotent retry. Recovery may
clear a pending local guard only when the root and external record both remain at the predecessor;
it advances forward when the root landed, and completes an external pending successor only when it
matches the signed local transition. An unrelated third head, same-position fork, wrong selector,
external advance beside a local predecessor, missing enrollment, or service outage remains closed.

Security startup performs this reconciliation for the complete policy-frozen namespace set before
RuntimeTree or network creation. Root-derived mutation decisions and externally meaningful reads
acquire the same namespace transaction and compare the local semantic head to the Agent's last
authenticated startup/mutation head. Thus another thread cannot expose a successor between local
replacement and external commit. The cached head is not a live lease: an independently running
clone can advance the service after this Agent's last query, and continuous clone fencing would
require bounded remote refresh plus expiry.

## Consequences

Thirteen owned checks bring the direct registry to 800. They cover domain separation and digest
binding, all four root transitions, both landed and non-landed local failures, lost replies on both
external CAS steps, every recoverable local-guard/external join, impossible predecessor/pending
states, forks and wrong selectors, early-return rollback refusal, and transaction-held reader
fencing. The retained two-guest gate enrolls two range-v1 namespaces through the real authenticated
service and restores one namespace's complete older four-root/guard state while its service record
remains current; startup refuses before RuntimeTree. The guests still share one construction host
and administrator.

This lane detects coordinated replay of exactly these four semantic roots relative to a separately
retained service record. It does not prove content correctness, availability, complete custody,
backup, service independence, or live single-active ownership. It does not witness replica heads,
attempts, partials, quarantine/object inventory, projection/current pointers, health records, or
tree-v2 frontier/workspace/maintenance state. It therefore does not make permanent purge safe.
