# ADR 0166: Defer full-ledger synchronization offers

Status: accepted at the deterministic construction boundary, 2026-08-25.

## Context

ADR 0165 freezes 32 accepted sends and 32 accepted receives as the qualified ceiling for one Agent.
Incoming Tox offers remain paused until `FileTransferManager::receive_to_path()` admits them, and a
full receive ledger returns `resource_exhausted` without accepting or dropping the offer.

The first synchronization subscriber treated every receive-admission failure as an immutable-object
failure. It removed provisional staging, finished durable active-attempt truth, fenced the scheduler
attempt, and failed the pull. That behavior is correct for an invalid offer, storage failure, route
failure, or provider contradiction. It is wrong when the only fact is temporary exhaustion of the
global Agent receive ledger: the remote offer is still paused and exact, but the subscriber destroyed
the attempt identity needed for bounded excess-work scheduling.

Simply raising the receive limit is rejected by ADR 0165. Busy retry inside the transport callback is
also rejected: it can starve owner work while capacity cannot possibly change.

## Decision

`resource_exhausted` from the final receive-admission seam is a typed deferral. The transfer bridge
removes its provisional private staging file and durable active-attempt record, but retains the exact
scheduler attempt, immutable object, route incarnation, staging-byte reservation, request-selected
FileId, and observed Tox file number. All other errors retain the existing fence-and-fail behavior.

The subscriber records the offer as pending rather than admitted. Agent service revisits paused
incoming FileId offers outside the transport callback. One pass examines at most the shared qualified
single-Agent ceiling of 32 records and advances a cyclic cursor across the complete transfer snapshot;
there is no tight loop and unrelated early records cannot permanently starve later offers. Each retry
revalidates the exact online-epoch authority context, FileId, file number, peer, and byte count before
calling the same admission entrance.

Cancellation becomes terminal before touching transport. It sends at most one cancellation for each
pending offer, then fences the retained scheduler attempt through ordinary close. An offline epoch is
different: toxcore has already purged its unaccepted offers, so the subscriber clears only their local
correlations and does not invent an impossible cancellation effect. Retry and pending counters are
content-free and saturating; `sync-status` exposes both.

## Consequences

- The Agent never accepts a 33rd receive. Excess sync work remains in toxcore's paused-offer state.
- Temporary capacity exhaustion no longer changes object, attempt, FileId, file-number, route, or
  authority identity.
- Provisional files and signed active-attempt entries do not accumulate while an offer waits.
- Staging-byte and scheduler-capacity reservations remain charged, so deferral cannot overbook the
  namespace merely because transport admission is delayed.
- Exact cancellation and offline cleanup remain bounded and do not repeat a possibly effected
  transport control.
- This is a single-route admission prerequisite, not multi-route reassignment. Direct-UDP and
  forced-TCP live pressure qualification is required before the roadmap excess-work box can close;
  route latency remains a separate composable gate rather than a number inferred from VM runtime.

## Verification

Owned tests inject receive-ledger exhaustion before any provider acceptance, require zero live bridge
bindings, zero failed attempts, unchanged scheduler attempt ID and byte reservation, then accept the
same file number into that attempt. Subscriber coverage retries the same FileId to full two-object
convergence and separately cancels a population containing one admitted and one pending offer while
an injected cancellation-send failure proves one-shot cleanup. Range-v1 coverage defers and retries
the exact bundle offer, then proves terminal retry emits no redundant cancellation. Complete GCC
Debug, Clang ASan/UBSan, and GCC TSan suites pass; deep path-sensitive Clang analysis reports zero
diagnostics in the transfer coordinator, subscriber, and Agent units.

The genuine `sync-tree-admission` Sandwurm gate then configured the subscriber for exactly one
accepted receive while pulling a two-object directory. Direct UDP proof `pair.xrl6_7gv` and forced
TCP proof `pair.dqbsp21_` each observed ten retries of the paused second offer, exactly two eventual
admissions, zero pending offers at completion, both verified object commits, accepted HEAD last, and
exact-token activation. Both compact proofs independently verify. The separately accepted 1,000-
sample `bulk-1` cells establish direct-UDP and forced-TCP latency classes; this composition closes the
single-Agent excess-work prerequisite without claiming simultaneous Ratox-under-deferral latency.
