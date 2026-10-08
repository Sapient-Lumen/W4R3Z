# Onward share page: current seat shareability and subject-class cliff interface spec

## Purpose

The archive already has strong delegation, grant, and rights-ceiling doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> may this seat share this subject onward, and if the answer changes elsewhere, what exactly is causing the cliff?

## Core decision

Every shareable subject must own one first-class **Onward share** page.
That page is the semantic home of:

- current seat shareability verdict
- source of the current ceiling
- subject-class cliffs
- narrower-vs-equal-vs-broader re-share rules
- mutation and revocation consequences
- recent shareability receipts

The product must not let a present or absent Share button stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. subject-and-seat strip
2. shareability verdict card
3. ceiling-source card
4. allowable re-share envelope card
5. mutation-and-revocation card
6. adjacent-class comparison card
7. recent shareability receipts
8. expert details drawer

### 1) Subject-and-seat strip

Show:

- subject
- current seat
- current seat role
- strongest next-safe action

The strip should answer `who is trying to share what?`

### 2) Shareability verdict card

Show one explicit verdict:

- `may share onward`
- `may share onward only at narrower rights`
- `may not share onward from this seat`
- `shareability blocked by current subject class`
- `shareability blocked by pending review or policy`
- `shareability hidden only because of current surface degradation`

Also show:

- whether the restriction is semantic, policy, or UI-only
- whether another seat in the same family would receive a different answer

This card should answer `is onward share actually allowed from here?`

### 3) Ceiling-source card

Show which layer owns the ceiling:

- subject class
- current grant lineage
- owner-domain policy
- artifact family
- seat exception
- current surface degradation

If more than one ceiling exists, order them by first required fix.
The page must not flatten `you are RO` and `this class never grants onward share` into one vague sentence.

### 4) Allowable re-share envelope card

Show:

- strongest right the seat may grant onward
- whether it may issue equal, narrower, or no downstream grants
- whether approvals, expiry, or budgets differ by lane
- whether the seat may only re-share the exact same artifact family or may choose among several reviewed carriers

This card should answer `what downstream authority could this seat honestly create?`

### 5) Mutation-and-revocation card

Show:

- whether this seat may later edit downstream grants it created
- whether revoke stops future updates only or also withdraws pending claims
- whether descendants remain as residue after revocation
- whether downstream grants survive subject-class migration or family rebase

This card should answer `what later control survives if I issue downstream access from here?`

### 6) Adjacent-class comparison card

Show the nearest cliffs, for example:

- `same seat on richer class would gain onward share`
- `same seat on poorer class would lose grant editability`
- `same seat on linked-family subject behaves differently than on manually granted subject`

This card should answer `is this answer about me, or about the class I am standing in?`

### 7) Recent shareability receipts

Show recent receipts with:

- seat
- subject
- shareability verdict shown at the time
- ceiling source
- downstream envelope shown
- issuance or refusal action taken

### 8) Expert details drawer

Hide low-level grant lineage, carrier parse details, and surface-render diagnostics behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. subject phrase
2. seat-role phrase
3. shareability phrase
4. ceiling-source phrase
5. strongest next action

Example:

```text
Project Atlas   seat role: RW leaf   may share onward only at narrower RO rights   ceiling source: current grant lineage, not browser state   Review downstream envelope
```

## Acceptance criteria

This spec is satisfied when:

- present-but-disabled and semantically-forbidden share states are visibly different answers
- class cliff and seat-role cliff are visibly different answers
- downstream envelope is shown before issuance
- later edit/revoke consequences are shown before issuance
- the product emits receipts for meaningful shareability decisions rather than outsourcing memory to absent buttons or folklore
