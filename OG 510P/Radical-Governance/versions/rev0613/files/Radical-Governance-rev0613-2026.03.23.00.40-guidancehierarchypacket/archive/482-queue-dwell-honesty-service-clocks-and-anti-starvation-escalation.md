# 482 — Queue dwell honesty, service clocks, and anti-starvation escalation

## One-line thesis

Rights-bearing requests, reviews, appeals, exceptions, and incident items should expose when their clock started, what service window or expectation applies, whether they are merely queued or actively worked, what is blocking progress, and how escalation happens when dwell exceeds thresholds, so “under review” cannot launder starvation.

## Why this matters

The archive already distinguishes request, review, approval, readiness, and live states. It also covers macrostate honesty, deadline contexts, durable case status, and basis-locked pending states. What it still lacked was one note focused on the temporal truth of the queue itself.

That gap matters because many consequential harms are not clean denials. They are long waits disguised as process. A case looks active because the portal says “in review,” but nobody has touched it for weeks. An appeal clock appears paused, but the user cannot tell why or whether the institution is waiting on them or on an internal reviewer. A service advertises quick handling in principle, yet the live queue hides whether the item is accepted, incomplete, stalled behind missing evidence, assigned but untouched, or breached against the stated service window.

Delay can be substantive even when no final merits decision has been issued. A benefits request can miss rent. An appeal can lapse into practical futility. A safety incident can remain live while the public surface still looks calm. Queue opacity is therefore not only an operations issue. In rights-bearing systems it is a fairness, recourse, and trust issue.

The archive should force the waiting layer to become governable.

## Pattern pack

### 1. Preserve a visible receipt time and queue-entry event

Each rights-bearing item should preserve at least:

- when it was received,
- when it became complete enough to enter the live queue,
- what channel submitted it,
- and which clock began at each stage.

A service cannot be honest about delay if it cannot say when the institution actually became responsible for acting.

### 2. Separate submitted, accepted, queued, actively worked, paused, and completed

These are different states.

- **Submitted** means the request arrived.
- **Accepted** means the institution considers it valid enough to enter process.
- **Queued** means waiting for substantive work.
- **Actively worked** means a reviewer or operator is currently processing it.
- **Paused** means progress is stopped for a named reason.
- **Completed** means the current phase ended.

One status label like “under review” often hides several of these realities at once.

### 3. Show both the governing service window and live dwell

Where a service standard, legal deadline, policy target, or expected handling window exists, the queue surface should show:

- the relevant standard or clock class,
- whether the item is inside, approaching, or beyond it,
- and the actual elapsed dwell time.

Historical processing averages are not a substitute for the live clock on this item.

### 4. Name blockers and pause causes in typed form

If progress is not happening, the current blocker should be visible in typed terms such as:

- waiting for requester evidence,
- waiting for institution review,
- queued behind capacity constraint,
- integrity check unresolved,
- legal hold,
- supplier dependency outage,
- duplicate-merge review,
- or priority escalation in progress.

Delay without cause visibility turns waiting into folklore.

### 5. Preserve queue ownership and touch honesty

A queue should distinguish:

- owner of the queue,
- owner of the specific item,
- last substantive touch,
- and mere status refresh or automated polling.

A decorative timestamp should not impersonate actual case movement.

### 6. Define anti-starvation escalation

When dwell crosses defined age bands or service thresholds, the system should escalate in a typed way, such as:

- supervisor review,
- public-case warning,
- temporary reprioritization,
- manual callback or outreach,
- or transfer to a protected fallback lane.

Escalation should not depend on whether the affected person knows how to chase effectively.

### 7. Prevent queue-jumping from becoming hidden policy

The archive should make visible what can and cannot legitimately alter order, such as:

- legal urgency,
- public harm risk,
- vulnerability markers,
- statutory deadlines,
- or incident-response priority.

It should resist ad hoc advancement by insider knowledge, repeated chasing, channel privilege, or staff familiarity unless those routes are explicitly governed.

### 8. Keep status history and service promises inspectable

A rights-bearing queue surface should preserve:

- status transitions,
- pause and restart events,
- service-standard class,
- escalation steps,
- and communications sent to the person waiting.

Otherwise institutions can overstate fairness by showing only the current state and hiding the path that got there.

## Guardrails

- Do not let “in review” cover both untouched queue dwell and active substantive work.
- Do not use historical averages as if they explain the status of a live case.
- Do not refresh timestamps in ways that imply progress where none occurred.
- Do not hide pause causes, service-standard class, or escalation posture from the waiting person where disclosure is appropriate.
- Do not let queue order drift into private exception culture.

## Failure modes

- **review-laundering**: an item looks actively reviewed when it is only sitting in backlog.
- **clock opacity**: nobody can tell which timer is running or when responsibility actually began.
- **touch theater**: status refreshes or automated checks masquerade as substantive work.
- **queue privilege**: certain actors learn unofficial ways to skip the line.
- **silent starvation**: a rights-bearing item exceeds meaningful dwell thresholds without escalation or visible warning.

## Practical tests

A queue-dwell honesty discipline passes when it can answer yes to all of the following:

1. Can the institution show when the item was received, accepted, and placed into the live queue?
2. Can users tell whether the item is queued, actively worked, paused, or completed?
3. Are service-standard windows or deadline classes visible alongside actual dwell?
4. Are current blockers, pause causes, and substantive last-touch events visible in typed form?
5. Does the queue have defined anti-starvation escalation that does not depend on user sophistication or insider access?

## Compression rule for the archive

If a consequential service can say **your case is under review** but cannot also say **which clock is running, what queue state you are actually in, what is blocking progress, and what happens if the wait breaches threshold**, then it is still letting **delay impersonate process**.
