# 473 — Deadline contexts, timeout causes, and no substantive decision by timeout

## One-line thesis

Deadlines, disconnects, timeouts, and cancellations in consequential public-AI workflows should be treated as typed coordination states with explicit causes and cleanup rules, not as silent substantive denials or hidden orphan work.

## Why this matters

The archive already distinguishes review, approval, release, and live use. It already distinguishes blocked action from route failure. But it still lacked one dedicated note for the coordination layer that surrounds consequential work: the request context, the deadline, the disconnect, the retry, the timeout, and the cancellation.

A claimant starts an appeal upload and their session expires. An operator requests a packet build, closes the tab, and the job continues in the background with unclear authority. A reviewer sees a request marked timed out and assumes the matter was denied. A supplier handoff is cancelled by an upstream service, but the downstream queue continues to process stale work. In each case, coordination state begins to impersonate substantive outcome.

That impersonation is dangerous because a timeout is not automatically a denial, a disconnect is not automatically abandonment, and a cancellation signal is not automatically proof that every coupled action stopped. Governance needs typed coordination truth, not folklore around whatever the platform happened to do.

## Pattern pack

### 1. Separate coordination outcome from substantive outcome

At minimum, distinguish:

- request completed,
- request cancelled,
- request timed out,
- client disconnected,
- upstream dependency failed,
- worker exhausted budget,
- and substantive decision reached.

A workflow should not let timeout or cancellation prose masquerade as a merits outcome.

### 2. Preserve a stable request or context identifier

Each consequential coordination attempt should have a durable identifier that can connect:

- the original request,
- retries,
- operator interventions,
- downstream jobs,
- and any final substantive case state.

Otherwise timeout disputes collapse into guesswork.

### 3. Record timeout and cancellation causes in typed form

Causes might include:

- user inactivity,
- network loss,
- dependency outage,
- explicit user cancellation,
- staff cancellation,
- expired authority lease,
- or budget exhaustion.

Cause codes are part of accountability because they determine what fallback, replay, or remedy should exist.

### 4. Stop or quarantine orphan work

If work intentionally should not survive a disconnect, timeout, or cancelled request context, the system should halt it. If work is allowed to outlive the originating context, it should move onto a fresh, explicitly authorized background context with named ownership and limits.

Zombie work should not continue by accident.

### 5. Say what happened to partial work

For a timed-out or cancelled workflow, the archive should say whether partial work was:

- discarded,
- preserved as draft,
- preserved as evidence only,
- or continued under fresh authorization.

This matters because draft state, evidentiary state, and operative state are not interchangeable.

### 6. Preserve manual fallback and resubmission rights

When a coordination path fails, the archive should preserve a route for manual completion or resubmission that does not silently convert transport trouble into loss of rights. The system should say whether the original clock is preserved, tolled, or restarted.

### 7. Treat timeout and cancellation patterns as governance telemetry

Repeated timeouts, disconnects, retries, and stale orphan jobs can reveal:

- inaccessible workflows,
- hidden capacity problems,
- misleading progress surfaces,
- or dependency failures masquerading as user non-response.

These are governance signals, not only engineering noise.

## Guardrails

- Do not let timeout language stand in for substantive denial.
- Do not let background work inherit indefinite authority from a dead request context.
- Do not let partial work quietly become final work.
- Do not drop cancellation or disconnect causes from the record.
- Do not force users to absorb route failure as forfeited rights.

## Failure modes

- **timeout-as-denial**: a coordination failure is read as a merits outcome.
- **orphan continuation**: stale work keeps running under dead authority.
- **cause collapse**: user cancellation, network failure, and staff abort all look the same.
- **partial-work laundering**: unfinished work quietly becomes authoritative.
- **retry amnesia**: repeated failed attempts disappear because there is no durable context identity.

## Practical tests

A deadline-aware workflow passes when it can answer yes to all of the following:

1. Can users and reviewers distinguish coordination state from substantive decision state?
2. Does each timeout or cancellation carry a durable request identity and typed cause?
3. Is it clear whether partial work was discarded, preserved, or continued under fresh authority?
4. Do dead request contexts stop work unless explicit reauthorization occurs?
5. When coordination fails, is there a fallback or resubmission route with explicit clock treatment?

## Compression rule for the archive

If a consequential workflow can say **the request timed out** but cannot also say **what timed out, why, what partial work exists, whether any work continued, and what rights remain**, then the archive is still letting **coordination failure impersonate substantive governance**.
