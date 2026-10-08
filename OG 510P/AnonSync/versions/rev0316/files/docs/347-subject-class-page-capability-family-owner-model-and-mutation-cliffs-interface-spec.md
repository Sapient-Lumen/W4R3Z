# Subject class page: capability family, owner model, and mutation cliffs interface spec

The archive already has subject-kind chooser doctrine, authority-mutation doctrine, and capability-artifact doctrine.
What it still lacked was one ordinary page for the question:

> what class of governed subject is this, and what concrete cliffs does that class impose on identity, sharing, mutation, and peer visibility?

Current Resilio docs still make this seam obvious enough to justify a replacement page.
They still distinguish Standard folders from Advanced folders by capability family, identity basis, peer aggregation, mutable rights, and upgrade path.
That is exactly the kind of truth a product should own on one page.

## Page promise

The Subject class page should make five answers adjacent:

1. class family now
2. identity / aggregation model now
3. rights / mutation model now
4. class cliffs now
5. strongest honest next action

The page exists so the operator no longer has to infer subject semantics from absent buttons and remembered folklore.

## Fixed page order

Every subject-class page should render the same sections in the same order:

1. **Subject snapshot**
2. **Class family**
3. **Identity and peer-view model**
4. **Authority and mutation model**
5. **Class cliffs and successor boundaries**
6. **Receipt promise**

### 1) Subject snapshot

This section should show:

- subject label and stable subject ID
- current subject class
- current authority seat and role
- whether this page is describing a live subject, a draft subject, or a proposed successor
- whether the current class was native, imported, or derived from older lineage

The operator should be able to answer: **what thing am I inspecting, and what class is it in right now?**

### 2) Class family

This section should show:

- capability family (`certificate-governed`, `raw-capability governed`, `local derivative`, `snapshot transfer`, etc.)
- whether requester approval is native, optional, impossible, or external
- whether the class has a stable Owner / steward concept
- whether all attached seats are individually addressable or class-flattened

The operator should be able to answer: **what deeper contract does this class use for authority?**

### 3) Identity and peer-view model

This section should show:

- whether remote participants are rendered as user families, individual seats, or anonymous capability holders
- whether one identity can group several descendant seats beneath one person row
- whether the current subject class can prove that grouping or only list devices separately
- what evidence backs each grouping (`certificate family`, `seat lineage`, `manual alias only`, `cannot prove aggregation`)

The operator should be able to answer: **what are the rows in my peer view actually rows of?**

### 4) Authority and mutation model

This section should show:

- strongest rights exposed by this class
- whether live rights mutation is available
- whether revocation can narrow future updates without reclaiming already landed bytes
- whether onward share authority exists and how it is bounded
- whether class change is required before stronger governance can exist

The operator should be able to answer: **what can I honestly change in place, and what requires a new epoch?**

### 5) Class cliffs and successor boundaries

This section should show:

- the concrete class cliffs (`no-owner`, `no-live-mutation`, `device-only peer rows`, `manual reissue required`, `cannot upgrade in place`, `class-specific approval model`)
- whether the proposed next action stays in-class or creates a successor
- whether bytes can stay continuous across the class boundary
- which artifacts, grants, or peer expectations must be retired or reissued

The operator should be able to answer: **what cliff am I about to cross, and is this still the same subject?**

### 6) Receipt promise

A subject-class receipt should preserve:

- subject and current class
- authority model summary
- aggregation model summary
- mutation ceiling summary
- class cliffs in force
- any successor boundary or no-successor guarantee stated during this review

The operator should be able to answer: **what class contract was declared here, and what was explicitly ruled in or out?**

## Compact row contract

A trustworthy compact row should preserve the following order:

1. subject
2. class phrase
3. identity-view phrase
4. mutation phrase
5. strongest next action

Example:

```text
Project Alpha   certificate-governed collaborative subject   peer view groups descendant seats by verified member family   live grant mutation available, owner-style onward share bounded by policy   Inspect class cliffs
```

## What this page must never imply

The page must never imply that:

- two subject classes differ only in cosmetics
- `same bytes` means `same governance epoch`
- missing live-mutation controls are merely UI simplification
- device rows and user-family rows are interchangeable
- per-seat exceptions on a class with broad owner semantics are ordinary local toggles

## Result

This page is how AnonSync borrows Resilio's class honesty without cloning the weaker habit of making operators discover class semantics through absent affordances, side-door how-tos, and peer-list surprises.
