# Standing arrival-template and default-root review interface spec

The archive already separates announcement from claim, claim from bind, current-share posture from future-arrival policy, and one-share placement review from broader defaults.
This document answers the narrower standing-policy seam that still remains after `98-share-local-presence-and-mode-decomposition-interface-spec.md` and `99-arrival-placement-suggestion-and-collision-review-interface-spec.md`:

> how should AnonSync let an operator edit the **standing seat template** that governs later arrivals, without turning one-share placement, reconnect ritual, or mobile `Simple mode` folklore back into the hidden source of future behavior?

This is the governance companion to `58-policy-origin-defaults-and-precedence-spec.md`, the per-seat posture companion to `98-share-local-presence-and-mode-decomposition-interface-spec.md`, and the per-arrival placement companion to `99-arrival-placement-suggestion-and-collision-review-interface-spec.md`.

## Why this needs its own spec

Resilio's current docs still make this seam unusually concrete.
`Sync Private Identity & Linking My Devices`, `Synchronization Modes`, `How to manually set the location of the folders synced across linked devices?`, `Folders are duplicating with an index (i) in their name.`, and `Settings on mobile platforms` still show that a seat's standing defaults are carried by a mix of `Disconnected / Selective Sync / Synced`, default folder location, and Android `Simple mode`.
That means the same knobs still decide, in one place or another:

- whether later arrivals announce only or connect immediately
- whether a default root/path is drafted before per-arrival review
- whether mobile shares auto-land in one default location
- whether same-name collisions fall back to indexed duplicates
- whether changing one seat's convenience setting will later surprise the operator when unrelated arrivals behave differently

Those are useful conveniences.
They are not yet one truthful **standing policy contract**.

The practical consequence is that the operator can still change a device default and only later discover that they also changed:

- how future arrivals are admitted
- where future binds are drafted
- which open arrivals inherit the new template
- whether duplicate fallback remains possible
- whether any current bound shares were supposed to stay untouched

AnonSync should therefore promote the standing arrival template into an explicit reviewed object rather than letting it hide behind connect/disconnect ritual, default-folder toggles, or `Simple mode`.

## Core rule

A **standing seat template** is a durable policy object.
It is not the same thing as:

- the current share's local posture
- the current share's committed bind
- a one-share placement review
- a one-time collision override

Every serious edit to that template should therefore render as its own reviewed change with explicit effect buckets.

## Vocabulary

### Standing seat template

A durable policy object governing later arrivals for one reviewed seat and one reviewed scope.

Suggested fields:

- arrival admission posture (`announce-only`, `review-required`, `claim-suggested`, `reviewed-auto-claim`)
- path-template or default-root draft
- collision default (`always-review`, `allow-same-lineage-adopt-suggestion`, `propose-alternate`, never silent suffix)
- initial byte suggestion (`names-only`, `placeholders`, `materialize-after-review`)
- scope (`family-arrivals`, `camera-backup`, `trusted-contact:Maya`, etc.)
- precedence / policy origin

### Template-governance review

A reviewed change to a standing seat template, including effect preview for future unseen arrivals and for already-visible but still-uncommitted arrivals.

### Effect bucket

A stable preview class saying what the template change will and will not touch.

Required buckets:

- **future unseen arrivals**
- **currently announced but unclaimed arrivals**
- **currently claimed but unbound arrivals**
- **currently bound shares**

### Template receipt

A durable record proving which standing template changed, what scope it governs, what effect buckets were reviewed, and whether any currently visible drafts were refreshed.

## Fixed review order

Every standing-template change should render the same sections in the same order:

1. **Reviewed seat and governed scope**
2. **Current standing template**
3. **Proposed standing template**
4. **Effect buckets**
5. **Exceptions and pinned subjects**
6. **Admissible actions**
7. **Receipt promise**

### 1) Reviewed seat and governed scope

This section should show:

- which seat is being changed
- what reviewed scope is governed
- which policy origin currently supplies the template
- whether the scope is seat-wide, share-class-wide, contact-scoped, or more limited

The operator must be able to answer: **which future arrivals am I actually governing here?**

### 2) Current standing template

This section should show the current values for:

- arrival admission posture
- path-template / default-root
- collision default
- initial byte suggestion
- provenance / origin

The operator must be able to answer: **what exactly is this seat currently set to do next time?**

### 3) Proposed standing template

This section should show the proposed replacement or delta.
It should preserve unchanged fields explicitly instead of making the operator infer them.

The operator must be able to answer: **what future behavior changes, and what stays the same?**

### 4) Effect buckets

This section should show a stable four-bucket preview.

#### Future unseen arrivals

Always show the new default behavior.

#### Currently announced but unclaimed arrivals

The product may offer two explicit policies:

- `refresh suggestion drafts to new template`
- `leave existing drafts unchanged`

The default should be conservative: **leave existing drafts unchanged unless the operator explicitly refreshes them**.

#### Currently claimed but unbound arrivals

These should ordinarily remain unchanged.
If the product ever allows draft-path refresh here, it must require a stronger review and explicit subject list.

#### Currently bound shares

These must remain unchanged by standing-template edits.
A standing-template review must never silently relocate or dematerialize already bound shares.

The operator must be able to answer: **what future and draft subjects change, and which real subjects definitely do not?**

### 5) Exceptions and pinned subjects

This section should show:

- subjects pinned away from inheritance
- per-share template overrides
- old drafts that would remain under prior template values
- any conflict with policy precedence or safety policy

The operator must be able to answer: **what will not follow this new template even though it seems in scope?**

### 6) Admissible actions

This section should allow verbs such as:

- `Change standing template for future arrivals`
- `Also refresh unclaimed drafts`
- `Keep current template`
- `Open narrower scope review`
- `Pin one subject away from inheritance`

It must not collapse these into `Save defaults` or `Change mode` when that wording would hide scope/effect differences.

### 7) Receipt promise

This section should show:

- acting seat and governed scope
- old template summary and new template summary
- which effect buckets were reviewed
- whether existing drafts were refreshed
- which subject classes were guaranteed unchanged

The operator must be able to answer: **what later evidence will prove that I changed standing policy rather than current share state?**

## Row and card contract

A truthful compact row should keep these facts in stable order:

1. seat + scope
2. admission posture
3. path-template/default-root
4. draft-refresh posture
5. next honest action

Example:

```text
Home-NAS / family arrivals   announce-only   /tank/family/{{share_name}}   drafts unchanged   Review template
```

A details card should also surface pinned exceptions and currently bound-share non-effects.

## What must never be implied

The interface must never imply that:

- changing the standing template relocates already bound shares
- changing the default root automatically refreshes all open arrivals
- `Simple mode`-style convenience is harmless enough to skip an effect preview
- silent duplicate suffixing is an acceptable collision default for future arrivals
- a per-arrival placement decision has rewritten the standing template unless the receipt says so

## Dense/mobile rule

Dense/mobile clients may compress wording, but they must still preserve separate cues for:

- governed seat/scope
- admission posture
- path template / default root
- whether existing drafts refresh
- which subjects stay untouched

A small client may shorten `currently bound shares unchanged` to `bound shares unchanged`, but it may not omit that guarantee entirely.

## CLI contract

Minimal commands:

```text
anonsync arrival-template list --seat self
anonsync arrival-template show --seat self --scope family-arrivals
anonsync arrival-template review prepare --seat self --scope family-arrivals   --admission announce-only   --path-template /tank/family/{{share_name}}   --collision-default always-review   --draft-refresh unchanged   --plan
anonsync arrival-template review show atr_01J...
anonsync arrival-template apply atr_01J...
anonsync arrival-template receipt show atc_01J...
```

## Why this matters

A weaker product shape would let per-seat defaults hide in a mode selector, a default-folder field, or a mobile simplification toggle and then ask the operator to remember what future arrivals will now do.
This spec rejects that shape.

The rule is:

> standing convenience must be its own reviewed object, with explicit effect buckets, so future-arrival behavior can improve without silently rewriting current share truth.
