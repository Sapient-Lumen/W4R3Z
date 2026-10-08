# Provider grant page: root proof, picker integrity, and existing target interface spec

The archive already has capture/source/sink pages, mobile storage pages, and target-custody review.
What it still lacked was one ordinary page for the grant question that removable/provider-backed targets make unavoidable:

> did the operator actually grant writable authority to this medium/provider, or did they only walk to a path that still lacks the right root proof and therefore cannot honestly count as an admissible target?

Current Resilio docs still make the seam obvious.
They distinguish disabling Simple Mode from actually granting SD-card root access, distinguish granting provider-root access from selecting the eventual folder location, warn that navigating through the ordinary picker path does not use the API and therefore does not grant access, and say some removable targets require choosing an already existing folder rather than creating one in-product.
That deserves one first-class page.

## Page promise

The Provider grant page should make five answers adjacent:

1. provider/medium in scope now
2. grant proof now
3. picker integrity now
4. target-adoption truth now
5. strongest honest next action

The page exists so the operator no longer has to infer write authority from mere path visibility.

## Fixed page order

Every provider grant page should render the same sections in the same order:

1. **Provider snapshot**
2. **Grant proof and scope**
3. **Picker integrity and path provenance**
4. **Target-adoption verdict**
5. **Admissible actions**
6. **Receipt promise**

### 1) Provider snapshot

This section should show:

- medium/provider class (`SD via provider`, `USB`, `network provider`, `ordinary local FS`)
- host/seat surface in use
- current mode constraints that hide or expose the medium
- whether the product is evaluating a fresh grant, an existing grant, or a suspected stale grant

The operator should be able to answer: **what medium/provider am I trying to use?**

### 2) Grant proof and scope

This section should show:

- whether a provider-root or equivalent capability has been granted
- the scope of that grant (`root`, `folder-limited`, `expired`, `unknown`)
- when and where the grant proof was obtained
- whether the product can still prove the grant is active enough for write access

The operator should be able to answer: **what exact authority has been granted, and how strong is the proof?**

### 3) Picker integrity and path provenance

This section should show:

- whether the currently chosen path came through the authoritative provider flow or through a misleading ordinary picker path
- whether the product is sure that the path belongs to the granted provider root
- whether mode shortcuts hid the correct provider route
- whether the path choice is honest, misleading, or non-authoritative

The operator should be able to answer: **did I reach this target through a trustworthy grant-aware path?**

### 4) Target-adoption verdict

This section should show:

- whether the target folder already exists
- whether in-product creation is allowed here
- whether the target can be safely adopted, needs external creation first, or must be re-picked
- whether the resulting bind would be `new target`, `existing target adopt`, or `blocked because write proof is insufficient`

The operator should be able to answer: **can this specific folder become the target now?**

### 5) Admissible actions

Example actions:

- `Grant provider root`
- `Reopen authoritative picker`
- `Adopt existing folder`
- `Create folder outside product, then return`
- `Switch out of simple mode`
- `Reject non-authoritative path`

The page must not reduce these choices to a generic `Browse` ritual.

### 6) Receipt promise

A provider-grant receipt should preserve:

- medium/provider in scope
- grant proof used
- picker-path provenance
- target-adoption verdict
- chosen action or rejection
- whether a later target bind depends on a still-valid provider grant

The operator should be able to answer: **what later evidence will prove that this target was chosen under a real grant rather than a misleading path?**

## Compact grant row contract

A trustworthy compact grant row should preserve the following order:

1. provider/medium
2. grant phrase
3. picker-provenance phrase
4. strongest blocker
5. next honest action

Example:

```text
ExternalSD   root grant missing   path reached through ordinary picker, not provider flow   blocker: write authority unproven   Review
```

## What this page must never imply

The page must never imply that:

- visible path equals writable authority
- provider-root grant and folder selection are the same action
- `Browse` proves a real storage permission
- existing-target adoption and new-folder creation are equivalent on removable media
- simple-mode convenience preserves the full target set

## Result

This page is how AnonSync borrows Resilio's candor about provider-backed storage without cloning the weaker habit of hiding grant truth inside a mobile peculiarity article and troubleshooting incantations.
