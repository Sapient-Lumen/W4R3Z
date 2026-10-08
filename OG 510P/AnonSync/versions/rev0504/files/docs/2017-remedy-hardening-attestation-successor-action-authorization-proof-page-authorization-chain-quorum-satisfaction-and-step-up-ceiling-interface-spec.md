# Remedy-hardening-attestation successor action authorization proof page — authorization chain, quorum satisfaction, and step-up ceiling

## Purpose

This page is the proof-facing object for showing whether a named successor-world action was legitimately authorized under the current rulebook.
It exists so the product can preserve the evidence for `who approved`, `under what burden`, and `with what scope ceiling` instead of collapsing everything into one vague `an owner did it` sentence.

## Required proof bundles

Every proof page must preserve these bundles:

### 1. Source-basis bundle

- source successor-controller-roster receipt
- successor world identifier
- governed slice identifier
- authorization rulebook version
- named action identifier and action family

### 2. Actor-chain bundle

- evidence for each actor in the requested actor set
- evidence for each actor's eligibility basis
- evidence for delegated versus direct status
- evidence for any shadow or remembered-authorization exposure

### 3. Quorum bundle

- required quorum rule
- evidence that quorum was or was not met
- evidence for contemporaneous participation rather than stale historical authority
- evidence that emergency exception, if used, actually matched the allowed class

### 4. Step-up bundle

- required freshness or challenge proof
- evidence that proof was supplied in time
- evidence that remembered approval was either allowed or explicitly forbidden
- evidence that authorization expired or remains valid

### 5. Ceiling bundle

- highest justified action-legitimacy sentence
- specific missing fact that blocks stronger standing authorization
- contradictory evidence that would collapse the current action standing

## Proof outputs

The page must output at least:

- action-risk assessment
- actor-eligibility assessment
- quorum-satisfaction assessment
- step-up-satisfaction assessment
- execution-window assessment
- blocked stronger authorization sentence

## Strong proof classes

The page must distinguish at least these proof classes:

- no reliable action-authorization evidence
- actor eligible but quorum unresolved
- quorum satisfied but step-up unresolved
- step-up satisfied for one-shot action only
- emergency containment proof only
- named action legitimately authorized once for named slice only
- repeated standing authorization not proved
- broader family authorization not proved

## Contradiction triggers

The proof page must visibly downgrade if any of these appear:

- any single linked device can approve or admit without the claimed second-controller gate
- remembered approval is doing work where fresh approval was required
- unchecked auto-connect or convenience link behavior bypassed the claimed action burden
- Standard-folder shareability widened action capability beyond the claimed gate
- the action was broader in scope, longer in duration, or more irreversible than the stated authorization window

## Hard rules

The proof page must never let:

- controller membership impersonate action authorization
- stale approval memory impersonate fresh quorum participation
- convenience default settings impersonate explicit high-risk adjudication
- one legitimate action impersonate reusable standing privilege
- successful execution impersonate proof that the authorization burden was correct
