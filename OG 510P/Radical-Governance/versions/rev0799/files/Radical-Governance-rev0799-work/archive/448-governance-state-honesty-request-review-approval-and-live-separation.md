# 448 — Governance-state honesty: request, review, approval, and live separation

## One-line thesis

Consequential public AI should not collapse roster presence, active review request, completed review, approval, queued release, and live operation into one fuzzy status; each state should mean one thing, stay scoped to a named basis, and surface explicit repair when that basis goes stale.

## Why this matters

A recurring governance failure is not that institutions have no review step, but that they compress too many distinct promises into one reassuring badge: “under review,” “approved,” “cleared,” or “live” ends up doing the work of assignment, request, completed check, release authorization, and ongoing validity all at once. That blur lets stale approval masquerade as current approval, lets a historical reviewer roster masquerade as an active challenge process, and lets work drift into production because a queue moved forward without anyone having to say exactly what state changed.

The archive should reject that compression. In consequential public AI, a status is a claim about authority, timing, and scope. If the institution cannot say whether someone is merely named, currently requested, already reviewed, approved on this baseline, queued for release, actually live, or back in rereview because the basis changed, then the governance surface is still lying.

## Pattern pack

### 1. Keep assignment, request, review, approval, release, and live use as distinct states

At minimum, the archive should distinguish:

- **named owner or reviewer**,
- **active request for review or sign-off**,
- **review completed on a named basis**,
- **approval granted on a named basis**,
- **queued or pending release**,
- **actually live in consequential use**,
- and **re-review / reapproval needed** when the governed basis has moved.

A person remaining on a roster is not the same thing as a current request to review. Completed review is not the same thing as approval. Approval is not the same thing as release. Release is not the same thing as live operation.

### 2. Scope each review and approval state to a named basis

Every review-complete or approval state should identify the basis it covers, such as:

- system or model version,
- rule or threshold set,
- prompt or retrieval baseline,
- data-source set,
- user-facing notice package,
- human-review posture,
- and deployment context if it matters to the decision.

The state should answer a precise question: **approved for what exact governed object?**

### 3. Surface stale-basis repair instead of silently carrying old approval forward

When the basis moves after review or approval, the archive should not silently preserve a green state. It should surface an explicit repair condition such as:

- **review stale**,
- **re-review needed**,
- **approval stale**,
- **reapproval needed**,
- **release blocked pending refreshed approval**.

That makes governance drift visible at the moment it begins rather than after harm reveals it.

### 4. Treat queued or pending states as real governance objects

A package can be technically ready, reviewed, approved on paper, and still not yet live. The archive should preserve explicit intermediate states such as:

- pending documentation refresh,
- pending release decision,
- pending public-notice publication,
- pending legal or policy sign-off,
- pending rollback contingency confirmation.

This prevents “almost live” from becoming de facto live through momentum.

### 5. Keep negative and unresolved states legible

Not every transition ends in approval. The archive should preserve compact but visible states such as:

- request declined,
- review incomplete,
- approval withheld,
- approval expired,
- release hold,
- release cancelled,
- returned for revision.

A governance system that records only successful transitions trains itself to forget where caution actually occurred.

### 6. Show what changed the state

Every consequential state transition should leave a small state receipt naming:

- previous state,
- new state,
- actor or role making the change,
- date and effective time,
- governed basis,
- reason or trigger,
- and next required step if the transition is incomplete.

The point is not bureaucratic ornament. The point is to stop future reviewers from having to infer why a status badge changed.

### 7. Separate visibility surfaces from authority surfaces

A dashboard row, reviewer chip, owner name, “in review” marker, or published card can remain visible for continuity even when the current active request or approval is no longer live. The archive should therefore distinguish:

- **historical or roster visibility**, from
- **current authority-bearing state**.

That way continuity does not become a false claim that active oversight is still happening right now.

## Guardrails

- Do not let historical reviewer presence masquerade as a current review request.
- Do not let completed review masquerade as current approval.
- Do not let approval masquerade as release authority or live status.
- Do not preserve green states after the governed basis materially changes.
- Do not hide unresolved or negative states by collapsing them into generic progress labels.

## Failure modes

- **state compression**: one badge tries to mean assignment, review, approval, and live use together.
- **stale-green drift**: approval stays green after the governed basis changes.
- **roster/request confusion**: named reviewers look current even when no active request exists.
- **queue laundering**: pending release work is mistaken for authorized live use.
- **success-only memory**: withheld, expired, or cancelled states disappear from the record.

## Practical tests

A governance-state model passes when it can answer yes to all of the following:

1. Can the institution distinguish named reviewer, active review request, completed review, approval, queued release, and live use?
2. Does each completed review or approval point to a named governed basis?
3. When that basis changes, does the status become explicitly stale rather than silently remaining green?
4. Are pending, withheld, expired, and cancelled states preserved as visible governance outcomes?
5. Can a later reviewer reconstruct who changed the state, when, and why?

## Compression rule for the archive

If a system cannot say **whether it is merely named, actively requested, actually approved on this basis, queued, or live**, then its governance surface is still hiding behind **status compression**.
