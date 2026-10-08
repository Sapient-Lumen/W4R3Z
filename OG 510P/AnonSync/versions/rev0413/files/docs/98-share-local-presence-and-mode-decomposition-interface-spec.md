# Share-local presence and mode decomposition interface spec

The archive already has incoming-share announcement/claim separation, file-availability surfaces, target-custody review, standing-approval guardrails, and same-host derivation review.
This document answers the narrower practical question those abstractions still leave too loose:

> what must a real operator surface literally show when one seat describes a share as `here`, so AnonSync never collapses announcement, claim, bind, bytes, and future-arrival automation back into one convenient mode label?

This is the local-presence companion to `95-announcement-inbox-and-local-claim-separation-spec.md`, the path-provenance companion to `81-target-custody-and-exclusive-bind-review-spec.md`, the file-byte companion to `92-file-availability-and-materialization-interface-spec.md`, and the future-arrival-policy companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`.

## Why this needs its own spec

Resilio's current docs still make this seam unusually clear.
`Sync Private Identity & Linking My Devices`, `Folder Types and Management`, and `Sync functionality in detail` still present `Disconnected`, `Selective Sync`, and `Synced` as the main linked-device local-state answer.
`How to manually set the location of the folders synced across linked devices` and `Folders are duplicating with an index (i) in their name.` then show that those same labels are also deciding what happens to later arrivals, whether a default path is used, when the operator gets to choose a custom location, and how same-name collisions are handled.
`Settings on mobile platforms` adds the same pattern on mobile: simple/default placement puts new shares in the default folder and same-name collisions gain `(1)`.

That is useful product behavior.
It is not yet one trustworthy local-state contract.

The practical consequence is that one friendly `mode` label can still blur together several different questions:

- has this seat merely been told the share exists, or has it claimed the share locally
- does this seat have a real bind/path for the share, and who chose that path
- does this seat have names only, placeholders, some bytes, or full bytes
- what will this seat do with later arrivals by default
- did the current path come from review, a template, a collision adjustment, or a reconnect ritual

If the operator still has to remember that a device in `Selective Sync` is both a current-share byte posture and a future-arrival default with path implications, the interface is not explicit enough.

## Core rule

AnonSync should treat local share presence as a **bundle of five independently inspectable facts**, not one mode bit:

- **announcement posture** — is the subject merely visible here, hidden locally, or withdrawn by wider authority
- **claim posture** — has this seat not claimed, suggested a claim, or actually claimed the subject
- **bind posture** — is there no path, a reviewed path, a template-derived path, a collision-adjusted path, or a blocked path question
- **byte posture** — names only, placeholders, partial local bytes, or full local bytes
- **future-arrival policy** — what this seat will do with later arrivals in a reviewed scope

The product may compress low-risk cases.
It may not let `mode`, `sync state`, `connected`, or `selective` imply all five facts unless they really line up that way.

## Vocabulary

### Share-local presence

The current truth for one share on one seat: announcement, claim, bind, path provenance, and byte posture.

### Arrival-default policy

A seat-scoped rule describing what later arrivals in a reviewed scope should do by default.
Examples: `announce-only`, `review-required`, `claim-suggested`, `reviewed-auto-claim`.

### Path provenance

The explicit source of the current bind choice.
Examples: `reviewed`, `operator-picked`, `template-derived`, `collision-adjusted`, `restored`.

### Mode-decomposition review

A reviewed case where the operator changes current share posture, future-arrival policy, or both and needs the product to say which scope is actually changing.

### Presence receipt

A durable record proving whether a change touched current-share posture, future defaults, or both, and what path/byte/provenance truth was in force.

## Fixed review order

Every non-trivial local-presence or future-arrival case should render the same sections in the same order:

1. **Current posture now**
2. **Future-arrival policy**
3. **Path provenance and collision posture**
4. **Byte posture and fetch policy**
5. **Admissible transitions**
6. **Receipt promise**

### 1) Current posture now

This section should show:

- which share and which seat are in scope
- whether the share is announced, claimed, hidden locally, or withdrawn wider
- whether a local bind/path already exists
- whether the current change would touch the current share at all

The operator must be able to answer: **what is true for this share on this seat right now?**

### 2) Future-arrival policy

This section should show:

- what later arrivals in the reviewed scope will do by default
- whether the default is `announce-only`, `review-required`, `claim-suggested`, or stronger reviewed automation
- whether a path template or default root is part of that policy
- whether changing this policy will leave existing shares untouched

The operator must be able to answer: **what will this seat do next time, and does this action change only that?**

### 3) Path provenance and collision posture

This section should show:

- whether a bind/path exists for the current share
- who or what chose that path
- whether the path came from review, operator choice, template derivation, reconnect, or collision handling
- whether any current or future collision rule could create suffixing, relocation, or review blocking

The operator must be able to answer: **where did this path come from, and what will happen if the name/path collides later?**

### 4) Byte posture and fetch policy

This section should show:

- whether the current share has names only, placeholders, partial bytes, or full bytes
- whether the current action changes byte posture now or only future defaults
- whether future-arrival policy implies any initial byte posture suggestion
- whether fetch, evict, or full-materialize behavior remains separately reviewable

The operator must be able to answer: **what bytes are here now, and what bytes will later arrivals start with by default?**

### 5) Admissible transitions

This section should show:

- change current share to `announce only here`
- suggest claim without bind
- bind to reviewed path
- change current byte posture
- change future-arrival default without touching the current share
- open stronger automation review
- reject because requested change would blur current state and future defaults

The operator must be able to answer: **what safe state change is actually available here?**

### 6) Receipt promise

This section should show:

- which presence receipt will exist after apply or reject
- whether the receipt proves a current-share change, a future-default change, or both
- which path provenance, collision rule, and byte posture facts were reviewed
- what later audit survives after the current screen is gone

The operator must be able to answer: **what later evidence will prove what changed here, and what did not?**

## Row and card contract

A truthful compact row or card should keep these facts in stable order:

1. subject
2. claim/bind phrase
3. path provenance phrase
4. byte posture phrase
5. next honest action

Examples:

```text
Photos-2026   Claimed • Bound at /srv/family/Photos-2026   Reviewed path   Full local bytes   Review
Scans-2026    Announced only • No local bind               None yet         No local bytes     Suggest claim
Videos-2026   Claimed • Bound at /srv/media/Videos-2026    Template-derived Placeholders      Materialize review
```

A separate seat-default card should keep these facts in stable order:

1. seat + scope
2. future-arrival default
3. path template / collision rule
4. current-share impact line
5. next honest action

Example:

```text
Home-NAS / family arrivals   announce-only   no path auto-bind   existing shares untouched   Review
```

The product should not collapse those two cards into one `Mode: Selective` label.

## What must never be implied

The interface must never imply that:

- changing future-arrival policy automatically rewrites the current share
- changing the current share automatically rewrites future-arrival defaults
- a template-derived path is equivalent to a reviewed current bind choice
- placeholder posture for the current share is the same fact as a default placeholder suggestion for later arrivals
- collision-adjusted suffixing is an unimportant cosmetic detail rather than path provenance

## Dense/mobile rule

Dense/mobile clients may compress wording, but they must still preserve separate cues for:

- current-share posture here now
- future-arrival policy here later
- path provenance
- byte posture
- next honest action

A small client may shorten `future arrivals queue announce-only` to `future: announce`, but it may not merge it into the same chip that says `current: placeholders`.

## Why this matters

Resilio still proves that linked-device convenience, selective materialization, and per-seat defaults are useful.
The lesson is not to reject those features.
The lesson is to stop one friendly `mode` label from quietly carrying the current share, the next share, the chosen path, and the byte story all at once.
