# Remedy-hardening-attestation successor action authorization timeline page — request, challenge, approve, execute, and expire action-gate events

## Purpose

This page is the time-ordered event view for how a named successor-world action moved from request to approval, execution, expiry, or downgrade.
It exists so the product can separate `controller existed`, `action was requested`, `quorum was satisfied`, `execution occurred`, and `standing privilege later expired or was revoked`.

## Required event types

The timeline must preserve at least these event types:

- action request opened
- action family and risk class assigned
- purpose basis attached
- requested actor set recorded
- second-controller request sent
- second-controller challenge or objection raised
- step-up proof requested
- step-up proof supplied
- remembered approval rejected as insufficient
- emergency exception invoked
- action authorized for one execution
- action execution started
- action execution completed
- authorization expired unused
- authorization downgraded after contradiction
- standing authorization refused
- standing authorization revoked or narrowed

## Mandatory timeline questions

The page must answer in order:

1. **When was the action first requested?**
2. **When was its risk class fixed and by whom?**
3. **When were quorum and step-up obligations satisfied, if ever?**
4. **Was the action authorized once, for a window, or not at all?**
5. **When did execution occur relative to the authorization window?**
6. **When, if ever, did the authorization expire, get contradicted, or get revoked for future reuse?**

## Event rendering rules

- Every event must show whether it broadens, narrows, or preserves action legitimacy.
- Every event must show whether it affects the named action only or a broader family.
- Every event must show whether it is direct, delegated, remembered, emergency, or manual-review in effect.
- Contradiction and downgrade events must remain visible even after successful execution.

## Hard rules

The timeline must never let:

- a controller-designation event impersonate an action-approval event
- one satisfied action gate erase later expiry
- emergency exception erase the absence of normal quorum
- execution success erase earlier burden defects
- an old approval event silently authorize a future action without a fresh link to that action
