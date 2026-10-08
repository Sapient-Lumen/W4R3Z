# Activity metrics page: window, scope, and bottleneck sufficiency interface spec

## Purpose

The archive already had route and queue language.
What it still lacked was one fixed page for the most ordinary telemetry question:

> what exactly is this live graph measuring, over what window, for which scope, and is it sufficient to justify a performance verdict yet?

## Core decision

A performance graph is never self-explanatory.
AnonSync should therefore model every visible graph as a reviewed **activity metrics page** rather than decorative telemetry.

The page must answer five questions directly:

1. what entity scope does this graph cover?
2. what time window and sample basis are in force?
3. which counters are primary versus derived?
4. what bottleneck classes are currently plausible from this evidence?
5. what evidence is still missing before a stronger claim is honest?

## Fixed review order

Every activity-metrics page should render sections in this order:

1. **Scope and window**
2. **Counter contract**
3. **Observed phases**
4. **Current bottleneck candidates**
5. **Missing evidence / next pivot**

## 1) Scope and window

Show:

- subject, seat, or pair scope covered by the page
- whether the graph is global, per subject, per seat, or per peer-pair
- active window length
- sampling cadence and freshness
- whether hidden or background work is included

The operator should be able to answer:

> is this graph about all work, one subject, or one transfer pair, and how far back does it really speak for?

## 2) Counter contract

The page should distinguish:

- raw counters (`bytes_read`, `bytes_written`, `bytes_sent`, `bytes_received`, `ops`, `queue_depth`)
- derived counters (`rate`, `latency trend`, `utilization grade`)
- host-level signals versus Sync-owned signals
- point-in-time values versus rolling averages

Never let a single line imply more than its contract supports.

## 3) Observed phases

Render a concise phase ledger such as:

- discovery / route establishment
- hash / verify
- read / stage
- send / receive
- write / finalize
- idle / quiescent

This keeps `slow` from flattening very different kinds of waiting.

## 4) Current bottleneck candidates

The page must classify the current dominant candidates, for example:

- route / relay penalty likely
- remote-upload ceiling likely
- local-disk pressure likely
- many-small-file overhead likely
- security-software / foreign-writer delay plausible
- insufficient evidence yet

Each candidate needs:

- confidence grade
- supporting counters
- what contradicts it
- best next pivot page

## 5) Missing evidence / next pivot

The page must end with one explicit ladder:

- open peer connection table
- open disk pressure page
- open throughput expectation page
- widen/narrow the observation scope
- wait for a fuller sample window

## Compact-row obligations

A compressed row or status chip may abbreviate, but it must still preserve:

- window length
- entity scope
- dominant candidate
- one-tap pivot to the full page

## Anti-clone rule

Do not clone graph panes that only show motion.
If the product can render a line chart, it must also render the contract that makes the chart interpretable.
