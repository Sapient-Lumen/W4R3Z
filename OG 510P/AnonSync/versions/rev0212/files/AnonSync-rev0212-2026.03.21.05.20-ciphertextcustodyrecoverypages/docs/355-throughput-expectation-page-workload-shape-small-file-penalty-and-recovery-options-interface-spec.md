# Throughput expectation page: workload shape, small-file penalty, and recovery options interface spec

## Purpose

The archive already had transfer policy, route proof, and method-choice language.
What it still lacked was one fixed page for another ordinary question:

> what speed should I honestly expect from this workload right now, and what changes are realistically capable of improving it?

Current Resilio docs still explicitly name many-small-file overhead, relay penalties, asymmetric source peers, low-capacity hardware, security software delay, and closed-port / directness issues.
AnonSync should preserve that honesty while tightening the contract.

## Core decision

A throughput claim must always be evaluated against **workload shape**, **route class**, **peer asymmetry**, and **resource ceiling**.
AnonSync should therefore model `speed expectation` as a first-class reviewed page rather than an informal support answer.

## Fixed review order

1. **Current workload shape**
2. **Expected ceiling bands**
3. **Dominant penalties**
4. **Realistic improvement options**
5. **Unrealistic expectations / no-magic warning**

## 1) Current workload shape

Show:

- few-large versus many-small distribution
- file-count overhead level
- route class in force
- source-peer count and upload distribution
- current local-disk state

The operator must be able to answer:

> am I dealing with a network ceiling, a file-shape ceiling, or both?

## 2) Expected ceiling bands

Instead of one optimistic number, show bands such as:

- likely ceiling under current route + workload
- likely ceiling if direct route wins
- likely ceiling if faster source peers join
- likely ceiling if workload is rebatched or staged differently

These are expectation bands, not guarantees.

## 3) Dominant penalties

The page should score penalties like:

- relay penalty
- many-small-file overhead
- slow-source asymmetry
- security software / filter delay
- host hardware ceiling
- disk-priority / disk-pressure penalty

Each penalty needs:

- confidence grade
- likely upside if removed
- preconditions for testing that upside

## 4) Realistic improvement options

Offer ordered options such as:

- improve direct reachability
- prefer same-LAN or predefined-host route
- wait for a stronger source peer
- batch or compress tiny-file workloads externally if policy allows
- reduce filter/AV interference
- adjust explicit priority knobs only if the semantic cost is acceptable

## 5) Unrealistic expectations / no-magic warning

The page must say when no honest quick win exists.
Examples:

- `many small files will not look like one large stream`
- `relay path cannot honestly promise direct-path throughput`
- `the current source peer is the ceiling until another source appears`
- `host disk pressure limits gains even if the route improves`

## Compact rendering obligations

Any compact `slow` or `throughput` card must preserve:

- current dominant penalty
- realistic best next step
- whether the current expectation is fundamentally workload-bounded

## Anti-clone rule

Do not clone support flows that only enumerate possible causes.
AnonSync should produce one expectation page that says which causes matter **here**, which do not, and what upside is realistically available.
