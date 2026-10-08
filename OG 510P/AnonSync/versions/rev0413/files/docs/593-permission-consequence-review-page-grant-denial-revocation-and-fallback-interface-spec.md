# Permission consequence review page — grant, denial, revocation, and fallback interface spec

## Purpose

Make permission mutation a reviewed action instead of an OS-side surprise.
This page exists to answer:

> if I grant, deny, defer, revoke, or later restore this permission, what exact capability delta follows, what remains true, and what less-invasive fallback still exists?

Current official Resilio docs make this seam concrete because permission meaning is still scattered across permission, settings, interface, and battery-policy articles.
AnonSync should own the consequence review directly.

## Core decision

Any meaningful platform-permission transition must compile to one first-class **Permission consequence review** page before the product treats the result as routine.

The page owns:

- requested permission transition
- affected capability families
- exact degraded or enabled states
- available fallbacks
- receipt and re-entry path

## Fixed page order

1. **Requested transition**
2. **Capability delta**
3. **Still-true fallback paths**
4. **Claim ceiling after apply**
5. **Receipt and re-entry**

### 1) Requested transition

Show:

- current permission state
- requested transition (`grant`, `deny`, `deny-for-now`, `revoke`, `restore`, `settings-handoff`)
- prompting action that led here
- whether the product can complete the transition directly or only hand off to OS settings

The operator must be able to answer:

> what exact permission state change is happening here?

### 2) Capability delta

Show rows for each affected capability family with columns:

- family
- before state
- after state
- strongest changed behavior
- strongest unchanged behavior

Typical rows:

- `qr / local scan claim`
- `arrival materialization`
- `background freshness`
- `startup continuity`
- `request alert delivery`
- `link/support convenience`

The operator must be able to answer:

> what exact product powers get wider or narrower if I apply this?

### 3) Still-true fallback paths

Show only honest substitutes such as:

- `enter key or link manually`
- `keep seat foreground-only`
- `use on-demand open instead of full arrival`
- `open OS settings later`
- `continue without alerts`
- `use another seat for this capability`

The operator must be able to answer:

> what can I still do without accepting the broader platform power?

### 4) Claim ceiling after apply

Show together:

- strongest approved sentence if transition succeeds
- strongest approved sentence if transition is denied or deferred
- stronger forbidden sentence
- blocker or residue that prevents the stronger claim

### 5) Receipt and re-entry

Show:

- receipt class to emit
- whether re-prompt is allowed or OS-settings-only now
- whether denial should be remembered as local preference, seat warning, or hard block
- best return path after OS settings handoff

## Main surface

The compact mutation sheet should never collapse to `Allow camera?` or `Need storage access`.
It should always show:

- the current prompting action
- the capability delta
- one still-true fallback
- the strongest safe sentence afterward

## States

Use a small stable vocabulary:

- `enabled`
- `degraded`
- `blocked`
- `deferred`
- `settings-handoff-required`
- `restored`

## Receipt fields

Suggested durable receipt fields:

- `permission_receipt_id`
- `seat_ref`
- `permission_family`
- `transition_requested`
- `transition_observed`
- `prompting_action_class`
- `capability_deltas[]`
- `fallbacks_presented[]`
- `strongest_safe_sentence`
- `generated_at`

## Success criteria

The page is successful only when an operator can answer:

1. what permission is changing
2. why the product asked for it now
3. what exact capability families get wider or narrower
4. what still works without it
5. what sentence the product is allowed to say afterward
