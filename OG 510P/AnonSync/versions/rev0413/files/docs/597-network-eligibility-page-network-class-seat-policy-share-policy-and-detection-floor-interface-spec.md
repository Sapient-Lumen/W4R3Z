# Network eligibility page — network class, seat policy, share policy, and detection-floor interface spec

## Purpose

Give the operator one reviewed answer to:

- what network class this seat is currently on
- whether the seat is globally allowed to use that class
- whether this share is additionally narrowed on top of the seat rule
- whether detection, peer connection, transfer, or all three are currently blocked
- what sentence is still true right now

This page is the network-participation companion to route-policy, background-delivery, and platform-permission pages.
It should appear whenever a seat/share may be present but not currently eligible to participate on the active network.

## Inputs

- seat identifier
- share identifier
- platform family (`android`, `ios`, `mobile-other`, `desktop-constrained`, `unknown`)
- current network class (`wifi`, `cellular`, `wired`, `offline`, `custom-pinned`, `unknown`)
- seat-wide network policy (`any-network`, `wifi-only`, `mobile-data-disabled`, `custom-seat-policy`, `unknown`)
- share-wide network policy (`inherit-seat`, `any-network`, `wifi-only`, `current-network-only`, `custom`, `unknown`)
- core activity state (`awake`, `sleeping`, `battery-blocked`, `foreground-only`, `unknown`)
- eligibility verdict (`eligible`, `share-policy-blocked`, `seat-policy-blocked`, `sleep-blocked`, `mixed-blocked`, `unknown`)
- detection floor verdict (`detects-and-transfers`, `detects-no-transfer`, `no-detect-no-transfer`, `unknown`)
- strongest safe sentence
- stronger forbidden sentence
- nearest re-entry condition

## Primary questions this page must answer

1. What network class am I on right now?
2. Does the seat itself allow participation on that class?
3. Does this share narrow the seat rule further?
4. Are detection and transfer both available, or is one/both currently blocked?
5. What exact event would make this share eligible again?

## Layout

### A. Eligibility verdict strip

Fields:

- share label
- seat label
- current network class
- current eligibility verdict
- strongest safe sentence

Example verdicts:

- `Current network is cellular; seat allows cellular, this share is Wi‑Fi only, so the share is stopped on this network`
- `Current network is Wi‑Fi; seat and share policies both allow participation`
- `Core is asleep; network policy would allow participation once the core wakes`
- `Global mobile-data setting blocks transfer on current cellular link`

### B. Active network card

Show:

- current network class
- whether the class is metered / constrained if known
- whether the class was operator-selected, system-selected, or policy-pinned
- freshness of the network observation

This card exists so the operator can stop treating `online` as enough evidence.

### C. Seat-policy card

Show:

- seat-wide rule for current network class
- whether cellular/mobile data is globally enabled
- whether the rule came from ordinary settings, advanced policy, or unknown origin
- strongest capability still allowed seat-wide

### D. Share-policy card

Show:

- share-wide allowed-network rule
- whether it inherits the seat rule or narrows it further
- whether this share is pinned to one current network, Wi‑Fi only, or any allowed network
- whether the rule blocks peer connection, detection, transfer, or all of them

### E. Detection / transfer floor card

Show rows for:

- peer visibility
- metadata detection
- transfer eligibility
- local placeholder/materialization actions

Each row should state `available`, `narrowed`, `blocked`, or `unknown`.

### F. Claim-ceiling card

Show three sentences together:

- strongest approved sentence
- stronger forbidden sentence
- blocker basis

Example:

- approved: `This share is present on the device but policy-ineligible on the current cellular network`
- forbidden: `This share is currently syncing normally`
- blocker basis: `share policy is Wi‑Fi only`

### G. Re-entry card

Show:

- nearest event that would restore eligibility
- whether that event is `join Wi‑Fi`, `enable mobile data`, `widen share policy`, `wake core`, `charge device`, or `manual resume`
- whether the product expects automatic resumption or fresh review

## Success criteria

A good page lets an operator answer, without article-hopping:

1. what network class is active
2. which layer is blocking participation
3. whether detection and transfer are both lost or only one is lost
4. what sentence is still honest right now
5. what exact condition will wake the share back into eligibility
