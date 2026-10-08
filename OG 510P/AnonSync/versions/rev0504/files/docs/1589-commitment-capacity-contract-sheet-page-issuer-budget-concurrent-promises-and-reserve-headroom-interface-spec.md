# Commitment capacity contract sheet page: issuer budget, concurrent promises, and reserve headroom interface spec

## Purpose

After authority to promise again is restored, the operator still needs one page that answers:

> how much promise load is already admitted here, what capacity remains, what reserve must stay protected, what classes of work compete for the same budget, and whether the next promise should be admitted, narrowed, deferred, or blocked?

## Core decision

AnonSync must expose one first-class **Commitment capacity contract sheet** whenever an actor, service, team, or execution lane can publish more than one live promise or deadline-bearing obligation.

## Fixed page order

1. **Capacity header**
2. **Budget-basis card**
3. **Concurrent-promise load card**
4. **Reserve and protection card**
5. **Admission posture card**
6. **Capacity sentence**

### 1) Capacity header

Show:

- capacity object id
- linked issuer or service id
- linked authority object id
- current budget class
- current admitted promise count
- current protected reserve posture
- current headroom class
- current overcommitment risk
- current admission posture
- latest strongest allowed sentence

Supported `budget_class` values:

- `single-promise-only`
- `narrow-multi-promise`
- `steady-state-multi-promise`
- `surge-capable`
- `shared-with-critical-background-load`
- `unknown-or-not-reviewed`

Hard rule:

The header may not treat restored promise authority as proof that spare capacity exists.
Capacity is its own object.

### 2) Budget-basis card

Required rows:

- performance evidence window considered
- queue and disk pressure considered
- background-work classes considered
- scheduler or throttle lanes considered
- discovery or rescan lag considered
- current protected commitments considered
- strongest fact expanding capacity
- strongest fact constraining capacity

Supported `capacity_basis_class` values:

- `recent-stable-low-pressure`
- `recent-stable-moderate-pressure`
- `background-heavy-but-bounded`
- `pause-window-or-throttle-distorted`
- `forecast-uncertain`
- `insufficient-basis`

Hard rule:

`looks fast right now` is invalid unless mapped to explicit basis facts and evidence windows.

### 3) Concurrent-promise load card

Required rows:

- current live promises consuming this budget
- load share per promise class
- protected obligations that cannot be displaced casually
- watch-only or checkpoint obligations that still consume some budget
- promised work not yet started but still reserved
- competing diagnostic or recovery work using same capacity
- strongest blocked additional promise

Supported `load_posture` values:

- `empty`
- `light`
- `moderate`
- `near-cap`
- `at-cap`
- `oversubscribed`

Hard rules:

- dormant promises must still count if reserve is held for them.
- a watch lane may be lighter than an active delivery lane, but it is not free by default.

### 4) Reserve and protection card

Required rows:

- protected reserve percentage or class
- work classes allowed to consume reserve
- work classes that may not consume reserve
- whether rescue, breach recovery, or critical repairs preempt reserve
- whether co-sign can unlock reserve use
- next event that releases meaningful headroom
- whether reserve is currently being violated

Supported `reserve_posture` values:

- `no-reserve-policy`
- `soft-reserve`
- `hard-reserve`
- `critical-incident-reserve`
- `deadline-reserve`
- `breach-recovery-reserve`

Hard rule:

Reserve may not be rendered as an aesthetic confidence indicator.
It must say what it actually protects.

### 5) Admission posture card

Required rows:

- whether the next promise is admitted
- whether only narrower scope is admitted
- whether only weaker promise classes are admitted
- whether deferral is required
- whether co-sign is required
- whether admission is blocked pending release of capacity
- strongest safer alternative now allowed

Supported `admission_posture` values:

- `admit-as-requested`
- `admit-narrower-scope`
- `admit-weaker-class-only`
- `admit-only-with-co-sign`
- `defer-until-release-trigger`
- `blocked-for-overcommitment-risk`

Hard rule:

`someone can probably fit it in` is invalid.
The page must render one explicit admission posture.

### 6) Capacity sentence

The page must end with one strongest allowed sentence in this form:

- who the issuer is
- what class of additional promise is currently allowed
- what scope or reserve condition applies
- what stronger promise is blocked by current load

Examples of supported sentence shapes:

- `This service may admit one more checkpoint-class promise of narrowed scope, but hard commitments remain blocked until the current recovery window clears and reserve headroom returns to green.`
- `No additional delivery commitment may be published from this lane now; only observation and triage checkpoints are allowed until queue pressure, hidden merge work, and protected breach-recovery reserve all fall below the current threshold.`
