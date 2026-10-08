# Disk pressure page: queue, load, and safe relief ladder interface spec

## Purpose

The archive already had queue explanation and host-cadence language.
What it still lacked was one fixed page for the ordinary question:

> is disk pressure actually the reason progress is slow, and if so is that pressure caused mainly by Sync or by the host around it?

Current Resilio docs still say disk load may reflect host-wide load rather than Sync alone.
AnonSync should elevate that into a stable page contract.

## Core decision

Disk telemetry must never collapse into a single scary `disk busy` badge.
AnonSync should model disk-state explanation as a reviewed **disk pressure page**.

The page must separate:

- Sync-created queue
- host-wide load not owned by Sync
- foreign-writer or antivirus interference
- write-finalize pressure versus read-stage pressure
- safe mitigations versus dangerous folklore

## Fixed review order

1. **Observed pressure**
2. **Ownership split**
3. **Phase concentration**
4. **Risk to current work**
5. **Safe relief ladder**

## 1) Observed pressure

Show:

- queue depth
- read/write operation rate
- observed disk latency / wait
- whether the condition is spiking, sustained, or clearing
- subject/seat scope

## 2) Ownership split

Classify current pressure as one of:

- mostly Sync-created
- mixed Sync and host
- mostly host-wide / foreign process
- insufficient evidence

Supporting evidence should include:

- Sync queue share of total wait
- known foreign-writer or AV hooks
- whether pressure persists while Sync work is idle

## 3) Phase concentration

Name which phase is paying the cost:

- hash/read
- write/finalize
- archive/history action
- placeholder materialization
- encrypted transform / decrypt
- unknown mixed phase

This keeps `disk busy` from flattening distinct corrective actions.

## 4) Risk to current work

The page must say whether current disk pressure risks:

- slower but safe progress
- timeout / disconnect perception only
- conflict with foreign writers
- backlog growth and space pressure
- user-visible finalize lag

## 5) Safe relief ladder

Offer a strictly ordered ladder such as:

1. wait for transient host load to clear
2. reduce competing local work or AV scanning scope
3. lower concurrent materializations / transfer pressure
4. change workload shape or timing
5. change explicit disk-priority knobs only with receipt

The page should also name what **not** to do if it would risk semantic damage.

## Compact rendering obligations

Any row or chip that says `disk pressure` must preserve:

- severity band
- ownership split
- dominant phase
- one safe next step

## Anti-clone rule

Do not clone telemetry that says `disk load high` without publishing whether Sync owns the problem, shares the problem, or is merely suffering from it.
