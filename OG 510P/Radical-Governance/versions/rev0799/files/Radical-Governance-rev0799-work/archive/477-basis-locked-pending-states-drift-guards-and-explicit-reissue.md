# 477 — Basis-locked pending states, drift guards, and explicit reissue

## One-line thesis

Consequential public-AI requests, reviews, approvals, queue entries, and ready states should stay locked to the exact basis they were issued against, and should fall back to stale-or-reissue-needed rather than silently following later drift, retargeting, or rebuild.

## Why this matters

The archive already distinguishes request, review, approval, queued release, and live operation. It also requires named bases, version pinning, material-change refresh, and approval freshness. What it still lacked was one sharper rule for the **pending state itself**.

A review is requested on one packet, but the packet is amended before the review occurs. A release is queued on one approved disclosure head, but the governing public notice changes while the item waits. An approval was granted on one model baseline, but the dependency graph or merge basis changed without any visible retarget step. A caseworker says a matter is "ready" because it was ready yesterday, even though the active artifact head or governing route has moved since then.

These failures are dangerous because the status can remain grammatically true while becoming substantively false. The institution still shows "requested," "approved," or "queued," but the state has slipped free of the object or basis that originally justified it.

## Pattern pack

### 1. Lock each pending state to an exact basis

For each consequential pending or pre-live state, preserve the exact basis it refers to, such as:

- case or packet head,
- model or rule baseline,
- review packet version,
- disclosure head,
- dependency set,
- target route,
- or queue group / release bundle.

A pending state without basis identity is only half a governance fact.

### 2. Separate current state from stale historical intent

If the basis changes after the state was issued, preserve two facts at once:

- the historical request, approval, or queue entry did happen,
- but it no longer binds the current basis without explicit reissue, rereview, or reattachment.

Do not force users to choose between silent inheritance and silent disappearance.

### 3. Surface stale-basis repair explicitly

When basis drift occurs, the archive should surface the repair path plainly, for example:

- rereview required,
- reapproval required,
- requeue required,
- retarget required,
- or explicit abandonment of the earlier pending state.

The correct response to drift is not a vague gray status. It is a named repair state.

### 4. Refuse automatic rebinding across retarget or rebuild

A request or approval aimed at one target should not automatically move to a later target merely because the names still look similar. Examples include:

- a queued release following a new bundle,
- an approval following a changed dependency set,
- a review request following a materially changed packet,
- or a human-signoff badge staying green after the governance basis moved.

### 5. Keep queue truth distinct from mere readiness

Once an item enters a release or execution queue, the archive should say whether:

- the queue entry is still live,
- the queued basis is still current,
- validation on the queued basis is pending, passed, or stale,
- or the item dropped back to ready-but-not-queued.

Historical queue participation should not impersonate present queue truth.

### 6. Preserve explicit reissue as a new act

When a stale request or approval is renewed on a new basis, record it as a new act with a link to the prior stale state rather than overwriting the earlier record. That is how the archive preserves continuity without pretending nothing changed.

### 7. Treat drift guards as governance controls, not only engineering controls

Compare-and-set style guards, expected-head checks, queue-basis checks, and stale-approval dismissal are not only software niceties. In consequential governance they are part of how the institution prevents old intent from being laundered onto new reality.

## Guardrails

- Do not let old approval follow a changed basis by silence.
- Do not erase historical requests merely because they no longer bind the current target.
- Do not let ready or queued badges outlive the object they were about.
- Do not retarget consequential pending work without explicit reissue.
- Do not flatten queue truth into one timeless ready state.

## Failure modes

- **sticky approval drift**: an approval survives after the reviewed basis changed.
- **ghost queue truth**: an item still looks queued because it once entered the queue.
- **silent retarget**: a pending state quietly rebinds to a newer target.
- **stale-green badge**: the UI stays reassuring while the basis underneath has moved.
- **repairless invalidation**: the old state disappears with no named path to recover it honestly.

## Practical tests

A basis-lock discipline passes when it can answer yes to all of the following:

1. Does each consequential pending state identify the exact basis it covers?
2. If the basis changes, does the system preserve both the historical act and the fact that it is now stale?
3. Are rereview, reapproval, requeue, or retarget steps surfaced explicitly rather than implied?
4. Can queue membership be distinguished from plain readiness and from stale historical queue entry?
5. When a stale state is renewed, is the reissue preserved as a new act linked to the old one?

## Compression rule for the archive

If a consequential system can say **requested, approved, ready, or queued** but cannot also say **for which exact current basis, whether that basis drifted, and what explicit reissue repaired the drift**, then it is still letting **old intent impersonate current authority**.
