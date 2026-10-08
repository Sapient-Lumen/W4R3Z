# Member access page: grant origin, editability, and future-update revocation interface spec

The archive already has strong delegation doctrine, subject-rights doctrine, and revoke/residue doctrine.
What it still lacked was one ordinary page for the question that arrives after sharing:

> what exact grant does this member have, where did it come from, what can I still edit here, and what part of revocation only stops future updates?

Current Resilio docs still make this seam obvious enough to justify a replacement page.
They still say Advanced-folder rights can be changed on the fly, still tie onward sharing to Owner, and still say `Disconnect` revokes future updates while leaving already synchronized files in place.
That is exactly the kind of truth a product should own on one page.

## Page promise

The Member access page should make five answers adjacent:

1. current grant now
2. grant origin now
3. editability ceiling now
4. revoke consequence now
5. strongest honest next action

The page exists so member management stops collapsing into a peer list plus a `Disconnect` verb.

## Fixed page order

Every member-access page should render the same sections in the same order:

1. **Member snapshot**
2. **Current grant and origin**
3. **Editability and subject-kind fence**
4. **Revocation consequence**
5. **Action ladder**
6. **Receipt promise**

### 1) Member snapshot

This section should show:

- member identity
- subject and subject kind
- current right
- whether the member is direct, descendant, auto-admitted, or inherited through some wider family
- whether the current page is editing a live grant or reviewing a frozen historical grant

The operator should be able to answer: **whose access am I looking at, to what, and in what way?**

### 2) Current grant and origin

This section should show:

- right currently in force
- source of that right (`direct issuance`, `remembered approval reuse`, `owner inheritance`, `constellation rule`, etc.)
- whether the member can onward-share
- which artifact or approval event originally created the access
- whether later role changes narrowed or widened it

The operator should be able to answer: **how did this member get this power?**

### 3) Editability and subject-kind fence

This section should show:

- whether the grant is editable from this seat
- whether subject kind narrows role choices or forbids edits entirely
- whether the operator can change right, revoke, pause future arrivals, or only inspect
- whether editability depends on the operator's own role or on a subject-class fence

The operator should be able to answer: **what exactly am I still allowed to change here?**

### 4) Revocation consequence

This section should show:

- what future updates would stop
- what already-landed bytes would remain
- whether descendants or onward-shared branches remain in scope
- whether local landed copies become stale, frozen, or actively reclaimed
- whether additional cleanup or recall work is available but separate

The operator should be able to answer: **what exactly does `remove` or `disconnect` mean here?**

### 5) Action ladder

Example actions:

- `Narrow to read-only`
- `Widen to read-write`
- `Grant onward-share`
- `Freeze future updates`
- `Revoke direct access`
- `Open retained-copy / recall review`

The primary action should be the safest truthful action, not the shortest label.

### 6) Receipt promise

A member-access receipt should preserve:

- member and subject reviewed
- prior right
- new right or revocation action
- grant-origin basis
- editability fence encountered
- future-update consequence declared
- any residual-copy follow-up opened

The operator should be able to answer: **what changed in this member's grant, and what remained outside the scope of that change?**

## Compact row contract

A trustworthy compact row should preserve the following order:

1. member
2. current right
3. origin phrase
4. revoke/editability phrase
5. next honest action

Example:

```text
alice@laptop   RW, no onward share   origin: direct approved claim on 2026-03-20   editable here; revoke stops future updates only, landed bytes remain   Manage
```

## What this page must never imply

The page must never imply that:

- every subject kind supports the same grant-editing story
- revoking a grant automatically reclaims already-landed bytes
- `owner`, `read-write`, and `can onward-share` are always interchangeable facts
- current right explains origin by itself
- a peer row alone is sufficient member-management UI

## Result

This page is how AnonSync borrows Resilio's mutable-grant candor without cloning the weaker habit of leaving editability fences and revoke consequences scattered across peer lists, subject-type caveats, and support prose.
