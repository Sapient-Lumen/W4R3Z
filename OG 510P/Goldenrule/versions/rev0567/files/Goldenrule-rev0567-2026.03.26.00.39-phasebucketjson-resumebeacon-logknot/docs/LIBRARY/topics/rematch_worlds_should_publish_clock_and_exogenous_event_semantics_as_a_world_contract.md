# Rematch worlds should publish clock and exogenous-event semantics as a world contract

Once a benchmark or rematch world runs asynchronously, outcomes depend not only on payoffs and policies but also on **when the environment moves on its own**, **how long actions take**, **when observations arrive**, and **what counts as a timeout or missed opportunity**.
If those timing semantics are hidden in scheduler code, an inheritor can mistake a change in world clocking for a change in reciprocity, competence, or institutional quality.

Recent external work sharpens this point.
`RS-GR-046` evaluates agents in dynamic asynchronous environments where the environment evolves independently of agent actions and where temporal constraints materially change what is being measured.
For Concord, the compact lesson is that once time and exogenous events are part of the world, the clock itself becomes part of the institution/world contract.

## Minimum contract

If a world evolves asynchronously or under exogenous events, publish at least:

1. the **clock model** (turn-based, wall-clock, event-driven, batched, or equivalent),
2. the **action timing rule** (instant, delayed, interruptible, queued, overlapping, or equivalent),
3. the **observation / message latency rule** and whether agents act on stale or synchronized views,
4. the **timeout / expiry semantics** for offers, sanctions, restorations, monitoring tests, or pending commitments,
5. and the **exogenous-event process** (what can happen without agent action, how often, and whether it is observable before or after it lands).

## Implementor consequence

Do not compare two rematch worlds as if they share one institution when one changes the event cadence, action latency, timeout rule, or observability lag.
That is a world-contract change, not just an implementation detail.

## Archive consequence

Keep this compact.
Prefer one retained timing-contract note or receipt field over another bulky asynchronous-behavior report pair.
