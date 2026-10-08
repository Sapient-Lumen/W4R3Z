# Incoming share request page: requester proof, auto-approval basis, and response ladder interface spec

The archive already separates offers from claims, remembered approval from fresh approval, and recipient intent from actual redeemer identity.
What it still lacked was one ordinary page for the moment when access is actually being asked for:

> who is requesting access right now, what exact evidence identifies them, and why is this request pending, auto-approved, or auto-blocked?

Current Resilio docs still make this seam obvious enough to justify a replacement page.
They still describe link redemption as sending a locally generated public key, still show approval as a distinct incoming event, and still distinguish remembered-approval reuse from policies that force fresh review for every folder.
That is exactly the kind of truth a product should own on one page.

## Page promise

The Incoming share request page should make five answers adjacent:

1. requester identity now
2. proof and provenance now
3. auto-approval / fresh-review basis now
4. strongest honest response options now
5. durable consequence now

The page exists so `Approve` stops being a magic button.

## Fixed page order

Every incoming-share-request page should render the same sections in the same order:

1. **Request snapshot**
2. **Requester proof**
3. **Policy basis**
4. **Grant consequence preview**
5. **Response ladder**
6. **Receipt promise**

### 1) Request snapshot

This section should show:

- subject requested
- requesting seat or claimant
- arrival carrier and arrival time
- pending / auto-approved / blocked / expired status
- whether this is first contact, remembered-contact reuse, or successor-like ambiguity

The operator should be able to answer: **what exact request is in front of me right now?**

### 2) Requester proof

This section should show:

- requester identity materials actually seen
- fingerprint or equivalent strong identifier
- display-name / alias if present
- what part of the identity was asserted by the requester versus derived locally
- whether the current proof is enough for high-trust approval, low-trust approval, or only further inquiry

The operator should be able to answer: **who is this, and how strongly do I really know that?**

### 3) Policy basis

This section should show:

- whether fresh review is required by current policy
- whether remembered approval, standing exception, or local trust memory would auto-admit
- whether the current request consumed budget from an artifact or only from approval attention
- whether this request is pending because of policy, missing proof, exhausted artifact, or local seat state

The operator should be able to answer: **why did this request land in this state instead of some other state?**

### 4) Grant consequence preview

This section should show:

- right that would be granted on approval
- whether approval also widens remembered trust
- whether onward share becomes possible
- whether the resulting member grant will be editable later
- whether rejection / block is one-request-only, one-artifact-only, or requester-wide

The operator should be able to answer: **what durable thing happens if I approve or refuse this?**

### 5) Response ladder

Example actions:

- `Approve with stated right`
- `Approve once without widening remembered trust`
- `Require stronger proof`
- `Reject this request`
- `Block this artifact`
- `Block this requester on this subject`

The primary action should be the safest truthful action, not the shortest label.

### 6) Receipt promise

An incoming-share-request receipt should preserve:

- requester identity evidence reviewed
- policy basis used
- approval or refusal action
- right granted or denied
- remembered-trust consequence
- any follow-up proof request or block scope

The operator should be able to answer: **why did this claimant end up admitted, refused, or still pending?**

## Compact row contract

A trustworthy compact row should preserve the following order:

1. requester
2. subject
3. proof phrase
4. policy-basis phrase
5. next honest action

Example:

```text
alice@laptop   Project Alpha   proof: key fingerprint seen, display name unverified   pending because this subject forces fresh review even for remembered peers   Review
```

## What this page must never imply

The page must never imply that:

- a friendly display name is sufficient identity proof
- auto-approval means `nothing meaningful happened`
- a remembered requester and a successor-like requester are the same thing
- rejection automatically claws back previously landed bytes
- one click on `Approve` speaks for right, trust scope, and future reuse without saying so

## Result

This page is how AnonSync borrows Resilio's approval candor without cloning the weaker habit of leaving requester proof, remembered-policy reuse, and grant consequence scattered across approval dialogs and support prose.
