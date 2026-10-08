# Return-delta contract sheet page: accepted successor delta, expiry, and owner interface spec

## Purpose

After the archive learned how to bring protection back truthfully, it still needed one ordinary page for the next operator question:

> this return is active, but what exactly is still different from the old protected state, who owns that difference, and when does the tolerance expire?

## Core decision

AnonSync must expose one first-class **Return-delta contract sheet** whenever activity or protection comes back in a changed-but-accepted state.

## Fixed page order

1. **Return-delta header**
2. **Accepted-delta card**
3. **Parity-debt card**
4. **Expiry and owner card**
5. **Promotion-or-restore card**
6. **Decision sentence**

### 1) Return-delta header

Show:

- return-delta id
- linked return id
- linked suspension id
- linked control / case / rollout id
- current delta status
- owner
- created time
- next rereview time
- current strongest safe sentence

Supported `current_delta_status` values:

- `newly-accepted`
- `temporary-accepted`
- `temporary-accepted-expiring-soon`
- `candidate-successor-baseline`
- `awaiting-exact-restore`
- `promoted-to-new-baseline`
- `reopened`
- `retired-after-exact-restore`

Hard rule:

A changed return may not disappear into normal state merely because the system is active again.

### 2) Accepted-delta card

This card states exactly what changed.
Required rows:

- previous intended protected state
- current active state
- accepted delta class
- exact difference summary
- why the difference is currently tolerated
- whether the delta is temporary or successor-candidate

Supported `accepted_delta_class` values:

- `path-successor`
- `mode-successor`
- `placeholder-successor`
- `merge-successor`
- `permission-successor`
- `topology-successor`
- `name-plane-successor`
- `multi-delta`

Hard rule:

The page must describe the difference in operator language, not only as machine diff fields.

### 3) Parity-debt card

This card records what claim remains blocked because of the delta.
Required rows:

- blocked stronger sentence
- weaker still-safe sentence
- missing proof to remove debt
- hidden survivor risk
- reversibility class
- consequence if left unresolved

Supported `reversibility_class` values:

- `easy-reverse`
- `planned-maintenance-reverse`
- `requires-merge-reconciliation`
- `requires-rights-or-policy-change`
- `cannot-return-exactly`

Hard rule:

`working` is not allowed to erase the blocked stronger sentence.

### 4) Expiry and owner card

This card makes tolerated drift concrete.
Required rows:

- owner
- expiry type
- expiry time
- rereview cadence
- automatic downgrade on miss?
- reopen trigger class

Supported `expiry_type` values:

- `fixed-time-expiry`
- `next-maintenance-window`
- `next-proof-window`
- `until-exact-restore-completes`
- `until-successor-promotion-decision`

Supported `reopen_trigger_class` values:

- `same-delta-persists-past-expiry`
- `delta-worsens`
- `same-cause-recurrence`
- `scope-expands`
- `owner-missing`
- `required-proof-missed`

Hard rule:

A tolerated delta without owner and expiry is not an accepted state; it is unmanaged drift.

### 5) Promotion-or-restore card

This card states the next honest branch.
Required rows:

- planned next branch
- preconditions
- proof required
- who decides
- what stronger sentence could return if branch succeeds
- what happens if branch fails

Supported `planned_next_branch` values:

- `exact-restore`
- `keep-temporary-and-rereview`
- `promote-successor-baseline`
- `split-state-and-narrow-claim`
- `reopen-linked-case`

Hard rule:

The branch must be explicit even if the answer is `keep temporary and rereview`.

### 6) Decision sentence

Format:

> `This subject is active in a [accepted_delta_class] return state owned by [owner] until [expiry_time]. It is safe to say [weaker still-safe sentence], but not safe to say [blocked stronger sentence] until [missing proof / branch].`

## Required interactions

### A) `Accept temporarily`

Creates a return-delta object with owner, expiry, and blocked stronger sentence.

### B) `Promote as successor candidate`

Does not promote immediately.
It only marks the delta as eligible for baseline decision.

### C) `Schedule exact restore`

Attaches maintenance window or proof window.

### D) `Reopen now`

Moves the state from tolerated delta to active problem.

## Explicit anti-goals

Do not:

- collapse `temporary accepted` and `promoted baseline`
- hide accepted delta inside generic healthy status
- allow missing owner or missing expiry
- allow `same visible folder name` to stand in for parity

## Why this page exists

Because a changed return is often operationally acceptable for a while, but that does not make it the new intended state.
The product must remember the difference so operators do not normalize drift by accident.
