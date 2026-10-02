# ADR 0296: Add tree-v2 exact-probe multi-source recovery

- Status: accepted and implemented
- Date: 2026-09-02

## Context

ADR 0295 made tree-v2 content custody sparse, so an authorized source can know the complete signed
graph while legitimately lacking an unselected file object. A one-source pull therefore failed when
its chosen publisher returned the existing authenticated `absent` or `unavailable` disposition even
if another authorized node held the exact immutable digest. Adding a new availability bitmap would
have changed the frozen tree-v2 peer framing before evidence showed it was necessary.

## Decision

Reuse the existing exact tree-v2 object request/result as the availability contract. The primary
source alone supplies the signed frontier. `sync-pull-multi PRIMARY NAMESPACE SOURCE [SOURCE...]`
atomically authenticates and registers every primary-carrier source before releasing that frontier
request. `sync-source-add JOB FRIEND` may add another source to an active content-v2 or tree-v2 job.
The historical local-control operation names and values remain unchanged; no peer frame, feature bit,
or authority capability changes.

For each locally missing branch record, manifest, or selected file object, the subscriber probes the
registered sources in stable primary-first order. `offered` advances the existing exact FileId-bound
receive. `absent` and `unavailable` are content-free authenticated availability evidence and advance
the same object to the next untried online source. `denied`, a changed authority snapshot, a changed
digest/size/FileId binding, or exhaustion of every source fails the job closed. All bytes remain
digest-verified before CAS commit. Additional sources can supply immutable bytes but cannot replace
the primary frontier, choose paths, activate a revision, or author a branch.

The source population is bounded by the namespace peer quota. Duplicate primary sessions are
idempotent only with the same frozen authority; the ordinary command rejects duplicate friend
selectors. Routed/auxiliary tree-v2 sources remain unsupported. If an unselected source goes offline
it is removed from consideration. If the active source goes offline after frontier admission, the
exact object is reassigned to another registered online source; loss of the primary before its
frontier result fails the job.

Tree pull status exposes source count, exact-probe request/result/absence/unavailable totals, and one
content-free row per source with principal, online state, requests, dispositions, commits, and bytes.
`state=complete custody=partial` continues to mean the complete selected closure—not complete backup
custody.

## Consequences

Sparse nodes can cooperate as complementary stores without another wire revision. The first
implementation favors a simple serial correctness path over up-front bitmaps or striping: in the
worst case it performs one bounded exact probe per source per missing object. Range transfer,
auxiliary carriers, parallel tree lanes, and an aggregate availability summary are performance work,
not correctness prerequisites.

The deterministic service proof constructs a primary with a valid two-file signed frontier, removes
one referenced object from its CAS, gives a second authorized source only that exact digest, then
shows one primary `absent`, one complementary verified commit, and complete receiver projection. It
also rejects same-epoch authority drift and proves a second job fails closed after both sources lose
the object. It does not claim independent-machine, routed-provider, soak, or backup qualification.
