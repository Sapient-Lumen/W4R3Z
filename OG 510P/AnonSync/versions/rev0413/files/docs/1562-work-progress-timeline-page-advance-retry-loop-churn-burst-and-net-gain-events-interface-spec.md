# Work progress timeline page: advance, retry loop, churn burst, and net-gain events interface spec

## Purpose

Progress quality changes over time.
The timeline page must answer:

> when did motion first appear, when was real advance last confirmed, when did retries or churn begin to dominate, and when did the system decide that the work was alive but not buying net progress anymore?

## Core timeline rule

AnonSync must treat progress-quality changes as first-class events, not as comments buried inside heartbeat or rescue records.

## Fixed event order

1. **Motion-entered event**
2. **First-net-advance or proxy-motion-only event**
3. **Churn-burst event**
4. **No-net-gain watch event**
5. **Boundary-crossing event**
6. **Reroute / rescue event**
7. **Aftermath event**

## Supported event types

- `motion-observed`
- `first-net-advance-confirmed`
- `proxy-motion-only`
- `rescan-burst`
- `rehash-burst`
- `retry-loop-detected`
- `merge-burst`
- `conflict-created`
- `blocked-transfer-detected`
- `ghost-file-warning`
- `no-net-gain-watch-opened`
- `no-net-gain-watch-aged`
- `no-net-gain-boundary-crossed`
- `reroute-activated`
- `rescue-activated`
- `requalified-after-reroute`
- `closed-without-net-gain`

## Required fields per event

- timestamp
- acting party or observing system
- evidence basis
- resulting progress state
- last confirmed net-advance time if changed
- what stronger sentence became allowed or blocked

## Timeline obligations

### A) Motion and net advance must be separate events

The page may not let `motion-observed` silently stand in for `first-net-advance-confirmed`.
Later readers must see whether activity began before real reduction was proved.

### B) Churn bursts must stay visible even if the work later requalifies

If retries, rescans, merges, or conflicts consumed a real window, the timeline must keep that visible.
Requalification is not allowed to rewrite the old record into clean uninterrupted progress.

### C) New debt creation must survive later cleanup

If conflict artifacts or similar side effects appeared, the timeline must preserve that event even when cleanup later succeeds.
The operator needs to know that motion once increased cleanup debt.

### D) No-net-gain watch and boundary-crossing must be separate events

Opening the watch means progress proof has become thin.
Crossing the boundary means the current route now owes a consequence.
The timeline must not collapse those two moments.

### E) Reroute and requalification must preserve what was lost and regained

If the plan changed because motion stopped buying progress, the page must show the old route, the reroute trigger, and the later requalification basis if one appears.

## Footer sentence

Render exactly one line:

**Current progress consequence:** followed by the live progress posture and next required route.

Hard rule:

A timeline ending in no-net-gain, reroute, or closed-without-progress posture must still state the live consequence now.
