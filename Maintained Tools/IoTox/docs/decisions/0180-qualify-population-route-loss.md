# ADR 0180: Qualify population route loss without blocking event delivery

Status: accepted over direct UDP and forced TCP, 2026-08-26.

## Context

Gate 3 proved one positively progressing pull can lose an exact auxiliary worker, fence its old
attempt, move one missing immutable object to another signed route, and recover the stopped identity.
Gate 4 then qualified healthy eight-job placement and concurrent cancellation. The remaining
multi-job question was harder: if fixed placement fills two four-job carriers and one disappears,
can every affected two-object job move together without over-admitting the survivor, accepting stale
truth, blocking the local control plane, or starving protected Ratox?

The first genuine forced-TCP attempts found three distinct boundaries.

1. Reassignment scored only one unit of free capacity even when the affected job still required two
   objects. The first object could debit capacity and the second could then fail terminally.
2. A receiver-signed capacity view can briefly lead the publisher's outgoing attempt ledger. The
   publisher correctly returned the existing `unavailable` object-result status, but the subscriber
   incorrectly made every non-offered result terminal.
3. The auxiliary supervisor called receiver-carrier pause/resume service on the same thread that
   alone drained required worker events, while holding its global snapshot mutex. A synchronous
   toxcore owner command could therefore stall event consumption and make `sync-status` wait behind
   the same supervisor lock. This repeated under forced-TCP multi-transfer load.

Increasing the completion timeout, dropping required events, weakening stale-incarnation fencing,
or changing the frozen sync wire would conceal these defects rather than repair them.

## Decision

Route selection now accepts the complete `required_work` for a job and excludes a route unless that
entire amount fits its current signed work budget. Reassignment uses requested objects minus already
committed objects. No partial scheduler debit is allowed to turn an otherwise eligible retry into a
mid-admission capacity failure.

The subscriber treats only a pre-offer `SyncObjectResultStatus::unavailable` as a transient
publisher-capacity observation. It allocates a fresh message ID and FileId, preserves the scheduler
attempt, and retries at most eight times by default. A stale reply to the old identity is ignored.
Unavailable after an offer is a protocol error; denied, absent, stale-generation, and other typed
results retain their terminal meaning. The bound is configurable only in owned construction and is
validated in `1..64`. No frame or enum changes.

The auxiliary supervisor now separates ordered transport-event consumption from periodic
file-carrier service. The carrier worker copies shared worker incarnations under the snapshot mutex,
then releases that mutex before any synchronous toxcore owner operation. Exact sync-frame sends do
the same. A concurrent qualification replacement keeps the old incarnation alive long enough for
the operation to return, but its stopped transport makes stale work fail rather than retarget.
Required events remain bounded and lossless. This is the route-worker counterpart of ADR 0157, not a
second toxcore owner.

Add `sync-tree-route-population-loss`. It starts eight independent two-object pulls under fixed
selection against two four-job bulk routes, requires initial pattern `00001111` and work 16, then
stops one exact worker after at least 65,536 aggregate receive bytes plus a 750 ms hold. The Agent
freezes the exact nonterminal affected job IDs. Acceptance requires four affected jobs, one loss,
four reassignments, at least four stale terminal fences, 12 fixed selections, one exact route
recovery, eight explicit activations, and work 16-to-zero. Recovery waits for every remembered
affected job to become terminal before spending the stopped route's one restart budget. Forty
protected Ratox renders must each remain below 250 ms.

## Consequences

- Gate 4 now has genuine multi-job same-carrier loss evidence on both native carrier classes.
- The scheduler reserves complete remaining job work, so route eligibility and debit use the same
  work-unit count.
- Transient provider capacity skew has a bounded fresh-identity retry instead of false immutable
  object refusal. A repeated or post-offer refusal remains explicit and finite.
- Auxiliary carrier fairness cannot block the only required-event consumer or retain the global
  worker snapshot lock while waiting for toxcore.
- Exact affected-job recovery replaces the old single-reassignment assumption; unrelated terminal
  jobs cannot authorize restart.
- Sync framing, HEAD-last acceptance, activation, route binding, authority, and signed route-set
  formats are unchanged.
- This is a deterministic eight-job/two-route/four-affected row. Random delay distributions, startup
  during fault, larger objects, common-link priority, independent relays, and long-running automatic
  production recovery remain open.

## Qualification

Binary `b401bbbb34259aeeaaa9b0934aadebff22388c6a1e6713957518520330955ed4`
passes strict raw and compact verification in both two-Sandwurm-guest cells.

- Direct UDP `pair.j19_uhjj`: 39,681 ms, fault at 152,181 bytes, four affected jobs, one loss,
  four reassignments, four stale terminals, one recovery, eight activations, and protected Ratox
  p50/p95/max 13.722/19.471/26.792 ms.
- Forced TCP `pair.rfnsjtqb`: 42,322 ms, fault at 122,019 bytes, four affected jobs, one loss,
  four reassignments, eight stale terminals, one recovery, eight activations, and protected Ratox
  p50/p95/max 102.749/143.370/156.251 ms.

Both primary transports record zero required-event backpressure. Both compact exports allocate
245,760 bytes and exclude guest disks, private identities, bootstrap secrets, and mutable runtime
state. The ordinary 30-entry CTest lane, all 45 Clang ASan+UBSan entries, and all 45 GCC
ThreadSanitizer entries pass; the five private-cgroup capability routes are explicit skips in each
applicable lane. Exact proof hashes and the failed-attempt interpretation live in
`evidence/2026-08-26-sandwurm-sync-route-population-loss.md`.
