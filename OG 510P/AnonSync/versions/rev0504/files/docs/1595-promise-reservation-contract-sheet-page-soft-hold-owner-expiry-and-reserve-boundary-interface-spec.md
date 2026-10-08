# Promise reservation contract sheet page: soft hold owner, expiry, and reserve boundary interface spec

## Purpose

After promise authority and honest headroom are both established, the operator still needs one page that answers:

> is any of this future room already spoken for, who owns that hold, what promise class or scope does it cover, when does it expire, and what stronger promise remains blocked while this reservation exists?

## Core decision

AnonSync must expose one first-class **Promise reservation contract sheet** whenever future promise room is being held, tentatively spoken for, or protected from other admission even before a final outward promise exists.

## Fixed page order

1. **Reservation header**
2. **Hold-basis card**
3. **Reserved-scope card**
4. **Expiry and release card**
5. **Reserve-boundary card**
6. **Reservation sentence**

### 1) Reservation header

Show:

- reservation object id
- linked issuer or lane id
- linked capacity object id
- hold owner
- hold class
- current reservation status
- current reserved scope class
- current expiry posture
- current reserve interaction posture
- latest strongest allowed sentence

Supported `hold_class` values:

- `soft-hold`
- `hard-reservation`
- `protected-reserve-lock`
- `provisional-option`
- `renewal-pending`
- `reclaim-pending`

Supported `reservation_status` values:

- `open`
- `active`
- `conditionally-active`
- `expired-awaiting-reclaim`
- `released`
- `reclaimed`

Hard rule:

The header may not render reservation as a side note under capacity.
Reservation is its own object with its own owner and expiry.

### 2) Hold-basis card

Required rows:

- reason this room is being held
- evidence that justifies holding room now
- weakest future promise class this hold protects
- strongest blocked alternative promise
- whether this is tied to named future work or generic reserve posture
- strongest fact weakening the hold
- strongest fact strengthening the hold

Supported `hold_basis_class` values:

- `named-upcoming-promise`
- `critical-recovery-contingency`
- `scheduled-window-protection`
- `co-sign-pending-option`
- `issuer-self-protection`
- `legacy-or-uncertain`

Hard rule:

`We might need room later` is invalid unless mapped to a named basis class and blocking effect.

### 3) Reserved-scope card

Required rows:

- promise class protected by the hold
- scope breadth protected by the hold
- audience or dependency boundary
- amount of future room reserved
- whether the room is exclusive or shared
- whether other weaker admissions may still pass
- what exact stronger promise remains blocked

Supported `reserved_scope_class` values:

- `single-narrow-promise`
- `single-broad-promise`
- `checkpoint-only-slot`
- `deadline-class-slot`
- `critical-recovery-slot`
- `fractional-shared-slot`

Hard rules:

- protected scope must be named.
- a reservation may not claim more room than the linked capacity object can honestly defend.

### 4) Expiry and release card

Required rows:

- hold opened at
- hold expires at or on condition
- renewal rule
- automatic expiry rule
- release trigger
- reclaim owner
- next moment this hold must be reviewed

Supported `expiry_posture` values:

- `hard-expiry`
- `soft-expiry-with-renewal`
- `condition-bound-expiry`
- `review-gated-no-fixed-time`
- `already-expired`

Hard rules:

- every open reservation needs either a clock expiry or a condition-bound review gate.
- open-ended holds without review are invalid.

### 5) Reserve-boundary card

Required rows:

- whether this hold consumes ordinary headroom or protected reserve
- whether it may invade protected reserve
- whether critical rescue may preempt this hold
- whether co-sign can override this hold
- whether this hold blocks only peers of same class or broader classes too
- whether ghost-hold risk is active
- next allowed stronger move if the hold is released

Supported `reserve_interaction_posture` values:

- `ordinary-headroom-only`
- `touches-soft-reserve`
- `locks-hard-reserve`
- `subordinate-to-critical-rescue`
- `override-possible-with-co-sign`
- `ghost-hold-risk-active`

Hard rule:

The page must say whether the hold is spending ordinary room, protected reserve, or both.

### 6) Reservation sentence

The page must end with one strongest allowed sentence in this form:

- who holds the room
- what future promise class or scope is being protected
- when or how the hold ends
- what stronger promise stays blocked while the hold persists

Examples of supported sentence shapes:

- `This lane is holding one narrowed hard-commitment slot for the named recovery follow-up until Wednesday 18:00 or explicit release, and no second deadline-class promise may be issued from the same reserve while that hold remains active.`
- `This is only a soft hold for a possible checkpoint-class commitment; it expires at the next review gate and does not justify blocking protected reserve beyond that time.`
