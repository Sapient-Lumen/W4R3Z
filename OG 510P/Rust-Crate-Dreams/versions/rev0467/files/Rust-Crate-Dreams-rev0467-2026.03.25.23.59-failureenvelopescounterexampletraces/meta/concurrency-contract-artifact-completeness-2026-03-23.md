# Concurrency Contract Kit artifact completeness — 2026-03-23

This note exists to keep **P-0538 Concurrency Contract Kit** from stopping too early.

The first pass proved that reentrancy, fairness, cancellation, and context boundaries are distinct.
This pass makes two additional completeness requirements explicit:

1. cancellation reports must say **what state was or was not consumed**;
2. recovery reports must say **what happens after panic or failed entry**.

## Artifact completeness checklist

A concurrency-support bundle is not mature enough unless it can answer these questions explicitly.

### A. Wait-cancellation completeness
A `wait-cancellation.report.json` should say:

1. whether queue membership is preserved, lost, or not applicable;
2. whether a message/value/permit/seen-bit was consumed;
3. whether a wake registration or stored permit creates a special caveat;
4. whether the docs call the surface cancel safe, not cancel safe, or only partially specified;
5. whether manual review is still required.

If a report only says “cancel safe” or “not cancel safe”, it is usually too weak.

### B. Failure-recovery completeness
A `failure-recovery.report.json` should say:

1. whether panic poisons the surface;
2. whether poisoning is advisory or mandatory;
3. whether there is a documented escape hatch or force path;
4. whether the surface is explicitly no-poisoning;
5. whether the posture is stable, nightly, or otherwise experimental.

If a report only says “poisoned” or “not poisoned”, it is usually too weak.

## Concrete proving grounds

### Queue withdrawal without message loss
Use:
- Tokio `Notify::notified`
- Tokio `Semaphore::acquire`
- Tokio `Mutex::lock`
- Tokio `RwLock::{read,write}`

These prove that queue-place loss is a real, documented class distinct from data loss.

### True cancel safety with preserved state
Use:
- Tokio `watch::Receiver::changed`
- Tokio `mpsc::Receiver::recv`

These prove that some surfaces can explicitly promise that cancellation does not mark values seen or consume messages.

### Advisory poisoning / escape hatch
Use:
- `std::sync::Mutex`
- `std::sync::RwLock`

These prove that recovery posture includes advisory signals and documented escape routes.

### Explicit no-poisoning
Use:
- `parking_lot::Mutex`
- nightly `std::sync::nonpoison::Mutex`

These prove that “no poisoning” is a meaningful support statement, not just absence of docs.

### C. Mobility / affinity completeness
A `mobility-affinity.report.json` should say:

1. whether the work is movable across threads, same-thread-only, local-context-only, or otherwise affine;
2. whether the spawn site requires a `LocalSet`, `LocalRuntime`, local executor, or comparable context;
3. whether the surface itself is `!Send` / thread-bound / CPU-pinned or merely the spawned work is;
4. whether the docs promise same-thread execution or only local-context legality;
5. whether manual review is still required.

If a report only says “supports `!Send` tasks”, it is usually too weak.

### D. Driver-liveness completeness
A `driver-liveness.report.json` should say:

1. whether progress is background-driven or requires explicit `run`, `tick`, `run_until`, `LocalSet` driving, or `Runtime::block_on`;
2. whether a handle exists that can spawn or block without driving timers / I/O / local tasks;
3. whether local work can become inert after a wrapper future completes;
4. whether blocking bridges are documented as non-cancellable or shutdown-sensitive;
5. whether manual review is still required.

If a report only says “runs on runtime X”, it is usually too weak.

## Bundle completeness rule

A mature bundle for a locking or waiting primitive should normally contain:

- `reentrancy-scope.report.json`
- `progress-fairness.report.json`
- `execution-context-boundary.report.json`

and, when applicable:

- `mobility-affinity.report.json`
- `driver-liveness.report.json`
- `wait-cancellation.report.json`
- `failure-recovery.report.json`

The bundle should never flatten missing optional artifacts into implicit success.

## Claim-ceiling rule

Any report should set a stronger claim ceiling only when the supporting docs are strong enough.

Examples:
- nightly-only `ReentrantLock` or `nonpoison::Mutex` should carry an experimental ceiling;
- `watch::changed` can make a stronger cancellation claim because the docs explicitly guarantee seen-state preservation;
- `Notify::notified` can make a queue-withdrawal claim because the docs explicitly say cancellation loses place in the queue;
- `parking_lot` can make a no-poisoning claim because the docs explicitly state it.

## What to reject

Reject bundle drafts that silently equate:

- queue-place loss with message loss,
- no poisoning with fairness,
- reentrancy with async-context legality,
- local spawn support with movable work,
- handle availability with driver-liveness,
- blocking capability with runtime-safety,
- or experimental/nightly posture with stable support.

## 2026-03-23 addendum — delivery memory and backlog pressure now belong in the completeness story

A concurrency-support bundle is now incomplete if it compares wake/channel surfaces without saying:

- what is remembered when nobody is ready,
- whether memory is a single coalesced wake, a latest-value snapshot, a bounded/unbounded queue, bounded broadcast history, or no memory at all,
- and what happens when producers outrun consumers.

Do not let future passes call a bundle “complete” if it only says cancellation, fairness, or context legality while hiding delivery-memory and pressure posture.


## 2026-03-23 addendum — delivery audience and consumption claim now belong in the completeness story

A concurrency-support bundle is now incomplete if it compares notification/channel surfaces without saying:

- who is actually in the audience for one wake/value/message,
- whether future joiners are included, excluded, or only able to observe later state,
- whether one receiver claiming the unit excludes other receivers,
- and whether the surface is non-consuming wake, exclusive single claim, clone fanout, independent seen-state tracking, or single-use transfer.

Do not let future passes call a bundle “complete” if it only says memory, pressure, fairness, or cancellation while hiding delivery audience and consumption-claim posture.


## 2026-03-23 addendum — delivery acceptance and observation evidence now belong in the completeness story

A concurrency-support bundle is now incomplete if it compares send / notify / publish surfaces without saying:

- what producer-visible success actually means;
- whether success proves endpoint liveness, queue admission, latest-state replacement, wake eligibility, or only audience presence;
- what later evidence exists, if any, that somebody really observed or processed the unit;
- whether close signals or receiver counts are merely weaker hints;
- and whether application-level acknowledgment is still required.

Do not let future passes call a bundle “complete” if it only says memory, pressure, audience, or claim posture while hiding what `Ok` actually certified and what it still failed to prove.

## 2026-03-23 addendum — delivery order and gap visibility now belong in the completeness story

A concurrency-support bundle is now incomplete if it compares message-passing / wake / state-update surfaces without saying:

- what ordered sequence, if any, a receiver is actually promised;
- whether the order is single-consumer FIFO, per-receiver FIFO, latest-snapshot-only, coalesced wake semantics, or selection-level random/bias;
- whether missed or collapsed units are counted, cursor-rebased, silent, or manually reviewable only;
- and whether cross-surface selection changes the story from channel FIFO to ready-operation choice.

Do not let future passes call a bundle “complete” if it only says memory, pressure, audience, claim, or acceptance while hiding sequence and gap posture.


## 2026-03-23 addendum — closure finality and post-close availability now belong in the completeness story

A concurrency-support bundle is now incomplete if it compares message-passing / state-watch / notification surfaces without saying:

- whether closure is immediate terminal, drain-then-terminal, reopenable, or subject to an in-flight race;
- what values, history, or snapshots remain observable after closure;
- whether the consumer must keep draining or probing after close to avoid silently dropping residual state;
- and what terminal signal appears only after the retained tail is exhausted.

Do not let future passes call a bundle “complete” if it only says memory, pressure, audience, claim, acceptance, evidence, or order while hiding what closed actually finalizes.
## 2026-03-23 addendum — late-joiner admission and join-start baseline now belong in the completeness story

A concurrency-support bundle is now incomplete if it compares message-passing / notification / watch surfaces without saying:

- whether a new observer may join after the surface already exists;
- whether the join route is explicit (`subscribe`, `resubscribe`, future creation) or simply absent;
- whether the new observer starts with future sends only, the current snapshot, the current tail, one stored permit, or no applicable baseline at all;
- whether current waiters and future waiters are intentionally treated differently;
- and whether fixed-pair / fixed-cohort channels make late-join stories inapplicable rather than merely undocumented.

Do not let future passes call a bundle “complete” if it only says memory, pressure, audience, claim, acceptance, evidence, order, or closure while hiding observer-entry and join-start posture.


## 2026-03-23 observer cursor / progress isolation addendum

The bundle is still incomplete if it can say who may observe a unit, whether one observer claiming it excludes others, what order/gaps look like, and whether late joiners exist, but **cannot say whether each observer advances its own cursor** or **whether one observer’s slowness changes another observer’s truth**.

Treat the following as first-class completeness requirements for `P-0538`:

- `observer-cursor.report.json`
- `observer-progress-isolation.report.json`
- scenario coverage for independent seen-state, per-receiver lag-rebase, shared competitive work pools, fixed single-consumer posture, and wake-only no-cursor surfaces

Do not flatten these into audience, claim, or order artifacts; those answer adjacent questions, not cursor ownership or observer-local progress fate.
