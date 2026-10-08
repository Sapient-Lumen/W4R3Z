# Reservation shaping review page: soft hold, hard reservation, option, and release routes interface spec

## Purpose

Before future room is treated as spoken for, the operator needs one review that decides:

- whether a tentative need deserves any reservation at all
- whether the room should be held softly or hard-reserved
- whether the right posture is only an option without guarantee
- whether the hold must expire, downgrade, release, or be blocked immediately

## Core decision

AnonSync must expose one **Reservation shaping review** page whenever future room would otherwise be claimed informally.

## Review sections

1. **Candidate hold summary**
2. **Need-versus-proof review**
3. **Reservation-strength review**
4. **Expiry discipline review**
5. **Blocked alternatives review**
6. **Route verdict**

### Candidate hold summary

Show:

- candidate reservation id
- requesting actor
- linked future work object if any
- requested hold class
- requested scope
- requested duration or condition
- current capacity posture
- current strongest blocked alternative

### Need-versus-proof review

Judge whether the request is supported by:

- named future work
- realistic likelihood of issuance
- time sensitivity
- dependency timing
- explicit reserve rule
- evidence that waiting to reserve would create real harm

Supported `need_grade` values:

- `strong-and-time-bound`
- `credible-but-not-yet-ripe`
- `speculative`
- `legacy-carryover`
- `insufficient`

Hard rule:

Speculative future work may not receive a hard reservation merely because the issuer feels busy.

### Reservation-strength review

Decide the weakest truthful class:

- `no-hold`
- `provisional-option`
- `soft-hold`
- `hard-reservation`
- `protected-reserve-lock`

Decision factors:

- certainty of near-term issuance
- cost of being wrong
- cost of blocking others
- availability of later upgrade path
- existence of co-sign or override route

Hard rule:

The review must prefer the weakest truthful hold that still prevents real planning harm.

### Expiry discipline review

Required checks:

- fixed expiry or clear review gate exists
- renewal conditions are explicit
- reclaim owner is assigned
- ghost-hold detection is armed
- stale hold consequences are explicit

Supported `expiry_discipline_grade` values:

- `tight-and-safe`
- `adequate`
- `fragile`
- `unsafe-open-ended`

Hard rule:

Any hold with `unsafe-open-ended` expiry discipline must be blocked or downgraded.

### Blocked alternatives review

Render:

- the best alternative promise currently blocked
- whether weaker alternatives remain open
- whether the hold blocks same-class only or broader classes
- whether reserve intrusion is justified
- whether a later fast release trigger exists

Hard rule:

The review must publish the opportunity cost of the hold.
A hidden blocked alternative is invalid.

### Route verdict

Supported `reservation_route_verdict` values:

- `do-not-hold`
- `grant-option-only`
- `grant-soft-hold`
- `grant-hard-reservation`
- `grant-reserve-lock`
- `grant-with-co-sign`
- `grant-but-shorten-expiry`
- `release-existing-hold`

The page must end with one strongest allowed route sentence, for example:

- `Grant only a soft hold; the future work is credible but not yet near enough to justify exclusive room beyond the next review gate.`
- `Release the existing reservation; its named dependency cleared, its expiry passed, and keeping it would keep the stronger delivery promise blocked without current basis.`
