# Arrival placement suggestion and collision review interface spec

The archive already separates announcement from claim, claim from bind, current-share posture from future-arrival policy, and target custody from ordinary path picking.
This document answers the narrower seam still left loose after `98-share-local-presence-and-mode-decomposition-interface-spec.md`:

> when a seat has a *suggested* local path for a newly announced or newly claimed share, what must the product show so suggestion, collision handling, and final bind choice do not collapse back into default-location folklore or silent `(1)` duplicates?

This is the placement-intent companion to `81-target-custody-and-exclusive-bind-review-spec.md`, the claim companion to `95-announcement-inbox-and-local-claim-separation-spec.md`, the mode-decomposition companion to `98-share-local-presence-and-mode-decomposition-interface-spec.md`, and the collision companion to `72-conflict-adjudication-and-path-collision-review-spec.md`.

## Why this needs its own spec

Current Resilio documentation still makes this seam unusually clear.
`How to manually set the location of the folders synced across linked devices` says that when `Selective Sync` or `Synced` modes are enabled, new folders go to the default folder, and the operator must switch the device to `Disconnected` and later press `Connect` to pick a custom location.
`Folders are duplicating with an index (i) in their name.` says that when a same-name folder already exists in the default location, Sync creates a newly arrived folder there with an added index and then asks the operator to disconnect/reconnect if they want the right location.
`Synchronization Modes` reinforces that the same mode family is still carrying both current-share materialization posture and the connect-to-path ritual for later arrivals.

That is useful convenience.
It is not yet a trustworthy placement contract.

The practical consequence is that a current product can still blur together several distinct questions:

- what path the product *suggests*
- why that suggestion was made
- whether that path is already occupied, safe, same-lineage, or unrelated
- whether the collision outcome is safe adoption, alternate-path review, or `keep announced only`
- whether any future template/default actually changed as part of the current bind choice

If the operator still has to remember that `change mode`, `disconnect`, or `connect` is really how one chooses a path and unwinds an accidental duplicate, the interface is not explicit enough.

## Core rule

AnonSync should treat path placement as a **reviewed suggestion pipeline**, not a side effect of one mode setting or one arrival event.

That means:

- every candidate local path is a **suggestion object**, not a committed bind
- every collision is a **typed review result**, not a cosmetic suffix fallback
- remembered roots/templates may prefill a suggestion, but may not silently create a bind
- a current-share bind choice and a future template/default change must remain separate acts unless the review explicitly says both are changing
- the receipt must later prove not only which path won, but **why that path was suggested, what collisions were seen, and what default remained unchanged**

## Vocabulary

### Placement suggestion

A draft candidate path for one share on one seat.
It includes the suggestion basis, path candidate, collision posture, and whether stronger review is required.

### Suggestion basis

Why the candidate exists.
Examples:

- `share-name-under-reviewed-root`
- `remembered-seat-preference`
- `scope-template`
- `manual-draft`
- `restored-bind`

### Collision class

The typed reason a candidate cannot be auto-bound.
Examples:

- `clear`
- `occupied-empty`
- `occupied-nonempty-unrelated`
- `occupied-same-lineage-candidate`
- `managed-bind-held`
- `case-fold-collision`
- `portable-target-mismatch`

### Placement review

A reviewed case where the operator confirms one candidate, rejects it, compares with an existing path, chooses an alternate path, or keeps the share only announced/claimed without binding.

### Placement receipt

A durable record proving the suggestion basis, reviewed candidate(s), collision class, chosen bind outcome, and whether future defaults/templates changed.

## Fixed review order

Every non-trivial placement case should render the same sections in the same order:

1. **Subject and current bind truth**
2. **Suggested path and why**
3. **Collision class and evidence**
4. **Admissible placement outcomes**
5. **Future-default impact**
6. **Receipt promise**

### 1) Subject and current bind truth

This section should show:

- which share and which seat are in scope
- whether the share is merely announced, claimed-but-unbound, or already bound elsewhere on this seat
- whether the current action is a first bind, a relocate, a rebind-after-loss, or a compare-and-adopt case
- whether local bytes already exist anywhere relevant on this seat

The operator must be able to answer: **what is true here before I touch the path?**

### 2) Suggested path and why

This section should show:

- the candidate path
- the suggestion basis
- the exact reviewed root/template/default that produced it, if any
- whether the product is proposing one candidate or several ranked candidates
- whether the suggestion is only a convenience draft or already reflects a prior reviewed bind restoration

The operator must be able to answer: **why is this the suggested place?**

### 3) Collision class and evidence

This section should show:

- whether the candidate path is clear, occupied, same-lineage, unrelated, or blocked by another managed bind
- what evidence was used: custody markers, lineage compare, path compare, filesystem profile, or plain occupancy
- whether the product can prove safe adoption or only offer cautious comparison
- whether a suffix fallback would hide a real collision

The operator must be able to answer: **what exactly is wrong or safe about this candidate?**

### 4) Admissible placement outcomes

This section should show only honest next actions, such as:

- `Bind at suggested path`
- `Compare and adopt existing path`
- `Choose alternate path`
- `Keep announced only`
- `Keep claimed but unbound`
- `Tighten future template`
- `Block because custody is already held`

The operator must be able to answer: **what safe placement action is actually available here?**

### 5) Future-default impact

This section should show:

- whether the current choice changes only this share or also changes future placement defaults/templates
- whether the candidate came from remembered defaults that remain unchanged after apply
- whether the operator is about to create/update a template or only consume one suggestion
- whether any future duplicate-avoidance rule is being tightened or left alone

The operator must be able to answer: **does this choice affect only this share or also tomorrow's arrivals?**

### 6) Receipt promise

This section should show:

- which placement receipt will exist after apply or reject
- the candidate path(s) reviewed
- the suggestion basis and collision class recorded
- the chosen outcome and whether future defaults changed
- what later audit survives after the screen is gone

The operator must be able to answer: **what evidence will later prove why this path won?**

## Compact row and card contract

A truthful compact placement row should keep these facts in stable order:

1. subject
2. current bind truth
3. suggested path
4. collision class
5. next honest action

Examples:

```text
Photos-2025   Announced • Unbound          /srv/family/Photos-2025          occupied-unrelated         Review placement
Scans-2025    Claimed • Unbound            /srv/scans/Scans-2025            clear                      Bind here
Music-2025    Claimed • Bound elsewhere    /srv/media/import/Music-2025     restored-bind candidate    Compare and adopt
```

A compact explanation strip should then answer in one sentence:

```text
Suggested from family root template; candidate path is occupied by unrelated local files; safest next step is choose alternate path or keep announced.
```

The product should not reduce that to `Connect`, `Disconnected`, or `Folder exists`.

## What must never be implied

The interface must never imply that:

- a suggested path is already a committed local bind
- a remembered root/template is equivalent to a reviewed bind choice for this share
- a collision-adjusted suffix such as `(1)` is an unimportant cosmetic outcome rather than a lineage and operator-intent question
- rejecting a suggested path automatically means rejecting visibility or future trust
- choosing an alternate path for one share automatically rewrites the seat's future-arrival template
- `compare and adopt` is safe without explicit evidence that the existing path is same-lineage or otherwise admissible

## Dense/mobile rule

Dense/mobile clients may compress wording, but they must still preserve separate cues for:

- current bind truth
- suggested path
- collision class
- next honest action
- future-default impact

A small client may shorten `suggested from family template; future template unchanged` to `template suggestion • defaults unchanged`, but it may not reduce the whole decision to `Connect`.

## Why this matters

Resilio still proves that remembered roots, default paths, and low-friction arrival placement are useful.
The lesson is not to reject those features.
The lesson is to stop path suggestion from masquerading as path commitment, and to stop collision fallback from masquerading as harmless duplicate naming.
