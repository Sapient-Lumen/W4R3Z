# Share capability page: artifact family, approval model, and rights ceiling interface spec

The archive already has strong portable-offer doctrine, approval-memory doctrine, and subject-kind doctrine.
What it still lacked was one ordinary page for the question that usually comes first:

> what exact capability artifact am I issuing here, what approval model comes with it, and what strongest right can this artifact ever create?

Current Resilio docs still make this seam obvious enough to justify a replacement page.
They still distinguish Standard-folder keys from Advanced-folder link/QR sharing, they still make approval part of the link story, and they still bind Owner capability to particular folder classes rather than all shares uniformly.
That is exactly the kind of truth a product should own on one page.

## Page promise

The Share capability page should make five answers adjacent:

1. artifact family now
2. carrier family now
3. approval model now
4. rights ceiling now
5. strongest honest next action

The page exists so the operator no longer has to infer capability semantics from a pile of toggles.

## Fixed page order

Every share-capability page should render the same sections in the same order:

1. **Subject snapshot**
2. **Artifact family and carrier**
3. **Approval and requester model**
4. **Rights ceiling and downstream mutability**
5. **Issued-artifact inventory**
6. **Receipt promise**

### 1) Subject snapshot

This section should show:

- subject kind
- current seat role
- whether the subject is shareable from this seat at all
- any subject-class fence that narrows the artifact menu
- whether the page is evaluating a fresh issuance or an already-issued family

The operator should be able to answer: **what thing am I trying to grant from what authority position?**

### 2) Artifact family and carrier

This section should show separately:

- authority-bearing artifact family (`reviewed claim artifact`, `raw capability string`, `local-only announcement`, `one-way send`, etc.)
- delivery carrier (`copied text`, `QR`, `local handoff`, `browser wrapper`, `message draft`)
- whether multiple carriers are equivalent views of one artifact or genuinely different authority objects
- whether the current carrier hides, truncates, or merely previews the full capability

The operator should be able to answer: **what exactly carries authority here, and what is only a wrapper?**

### 3) Approval and requester model

This section should show:

- whether the artifact is claim-only, approval-gated, or auto-admitted under remembered policy
- whether redemption creates a pending request, immediate bind, or local-only parse
- whether requester identity is expected before capability activation
- which policy layer can cause automatic admission and which one can still force fresh review

The operator should be able to answer: **what human or policy gate stands between possession of the artifact and live access?**

### 4) Rights ceiling and downstream mutability

This section should show:

- strongest right the artifact can produce
- whether onward sharing is possible
- whether the resulting grant can be edited later
- whether edit/revoke works only for some subject kinds
- whether future updates, local landed bytes, and onward-granted descendants have different revocation boundaries

The operator should be able to answer: **how much power can this artifact create, and what later control survives?**

### 5) Issued-artifact inventory

This section should show:

- still-live artifact variants for this subject
- expiry / budget / reissue posture
- which artifacts are superseded, revoked, or exhausted
- whether carriers differ only cosmetically or represent separate issuance events

The operator should be able to answer: **what is already out there, and which exact artifact would I be adding or replacing?**

### 6) Receipt promise

A share-capability receipt should preserve:

- subject and issuing seat
- artifact family
- carrier family
- approval posture in force
- rights ceiling offered
- later mutability ceiling
- issuance action taken

The operator should be able to answer: **what exact capability did I issue, and with what declared governance story?**

## Compact row contract

A trustworthy compact row should preserve the following order:

1. subject
2. artifact phrase
3. approval phrase
4. rights phrase
5. next honest action

Example:

```text
Project Alpha   approval-gated claim link (QR and copied text are same artifact)   fresh review for new peers, remembered policy may auto-admit known peers   ceiling: RW, no onward share from this seat   Issue
```

## What this page must never imply

The page must never imply that:

- `QR` and `link` are always separate capabilities
- `copied text` is automatically the same thing as `raw capability string`
- `can share` means `can later edit or revoke every grant`
- possession of an artifact proves the requester already passed identity review
- one folder class and another folder class have the same rights ceiling or mutability story by default

## Result

This page is how AnonSync borrows Resilio's artifact candor without cloning the weaker habit of making operators reconstruct capability semantics from share-dialog toggles, key architecture notes, and mobile carrier tips.
