# Promise load review page: admit, defer, throttle, and capacity-reservation routes interface spec

## Purpose

This review page decides whether a proposed new promise can be admitted into the current capacity envelope without bluffing.

## Core decision

AnonSync must expose one first-class **Promise load review** whenever a proposed promise would share execution budget with existing commitments, recovery work, background work, or protected reserve.

## Review questions

The page must force explicit answers to these questions in order:

1. **What exact promise class and scope is being proposed?**
2. **Which current obligations consume the same effective capacity?**
3. **Is the present evidence window good enough to claim spare headroom?**
4. **Would admitting this promise violate protected reserve or force unsafe preemption?**
5. **If not admitted as requested, what is the strongest safer alternative?**

## Fixed page order

1. **Proposal card**
2. **Competing-load card**
3. **Reserve-consumption card**
4. **Safer-alternative card**
5. **Decision strip**

### 1) Proposal card

Show:

- requested promise class
- requested scope
- desired deadline window or checkpoint cadence
- proposing actor
- whether co-sign is already attached
- whether this is customer-visible or internal-only

Hard rule:

The card must not let a vague `small ask` stand in for explicit scope.

### 2) Competing-load card

Show:

- currently admitted promises sharing this lane
- active recovery or rescue work sharing this lane
- hidden background-work burden likely to compete
- paused-but-not-free work still reserving capacity
- strongest current load that most tightly constrains the new ask

Supported `competition_posture` values:

- `mostly-independent`
- `shared-lane-manageable`
- `shared-lane-tight`
- `shared-lane-critical`
- `unknown`

Hard rule:

Merely different labels are insufficient.
The page must say whether the work actually competes for the same budget.

### 3) Reserve-consumption card

Show:

- whether admission would consume reserve
- whether reserve use is allowed for this class
- whether reserve use requires co-sign or emergency posture
- whether admission would starve existing protected work
- whether the reserve violation is temporary, structural, or unknown

Supported `reserve_use_verdict` values:

- `no-reserve-use`
- `allowed-soft-reserve-use`
- `requires-approved-hard-reserve-use`
- `would-violate-protected-reserve`
- `cannot-tell`

Hard rule:

A page may not silently spend reserve because the promise feels important.

### 4) Safer-alternative card

Show:

- narrower scope option
- weaker promise-class option
- later start / defer option
- co-sign-required option
- observation-only option
- strongest claim preserved under the safer alternative

Supported `safer_alternative_class` values:

- `none-needed`
- `narrow-scope`
- `weaker-class`
- `later-window`
- `checkpoint-only`
- `diagnostic-only`

Hard rule:

If the requested promise is rejected or narrowed, the page must publish the best still-honest alternative instead of just saying `no`.

### 5) Decision strip

Supported `load_review_verdict` values:

- `admit`
- `admit-narrowed`
- `admit-weaker-class`
- `admit-with-co-sign`
- `defer`
- `block`

The strip must also show:

- strongest admitted sentence
- strongest blocked stronger sentence
- next event that could change the verdict

Hard rule:

The final strip must preserve what changed because of capacity rather than because of trust, authority, or evidence quality.
