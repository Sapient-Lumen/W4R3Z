# Resilio work heartbeat, stall, and rescue fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- rank live decisions in a portfolio
- dispatch one work item now
- publish who accepted custody of that work
- preserve claim expiry, redelegation, and abandonment truth

What it still lacked was the next ordinary operator answer:

> after custody is accepted, is the work actually alive, merely quiet for a valid reason, blocked, silently stalled, or already in need of rescue?

That is the seam this pass locks.
A product that can tell you who owns the work but not whether the work is still moving still leaves too much truth trapped in inbox habits, green badges, and the operator's memory of what they last saw.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **motion / pressure / troubleshooting** ingredients, but mostly as separate status surfaces rather than one operator-facing work-heartbeat contract:

- `Sync Main View (Desktop)` still exposes search, a 30-day History lane, notification bell state, peer counts, and status icons, with green check meaning synced with connected peers.
- `My files don't sync` still tells the operator to inspect peer connectivity, warnings, History, and upload/download queues when motion appears to stop.
- `Performance overview` still exposes real-time network and disk graphs with 1-minute, 10-minute, and 1-hour windows, per-peer speeds, latency, and disk queue depth.
- `Some internal tasks are taking time to complete` still says hidden background work can consume time, may self-recover, and does not by itself prove permanent stuckness.
- `Agent run out of system notify watchers...` still says watcher exhaustion can degrade update discovery so that Sync learns about updates by manual or periodic rescans.
- the current `Resilio Sync change log` still records motion-adjacent interface signals like synchronized notifications, a `Last transferred` column, improved peer-list accuracy, and improved receiving-statistic accuracy.

## What current Resilio still gets right

### 1) It exposes several honest motion witnesses

History, peer counts, upload/download queues, performance graphs, latency, disk queue depth, and warnings are all real witnesses.
That candor is worth borrowing.

### 2) It admits that apparent quiet can still be healthy background work

The internal-tasks warning is useful because it tells operators that not all quiet is failure.
That distinction matters.

### 3) It surfaces some liveness degradation causes directly

Watcher exhaustion, disconnected peers, queue visibility, and performance pressure all give operators clues about why movement may have slowed or vanished.
That is valuable.

## Where current Resilio still fragments the operator answer

### A) Motion evidence is still weaker than one claimed-work heartbeat

History, graphs, queues, and warnings each illuminate one part of the picture.
They still do not compile one explicit answer to whether **this accepted work item** is alive right now.

### B) Short-window graphs are still not a durable liveness contract

Real-time graphs are useful for troubleshooting.
They are still weaker than a page that says what heartbeat was expected, what quiet window is allowed, and when silence becomes overdue.

### C) Healthy wait and silent stall still rely on operator synthesis

Resilio usefully states that hidden tasks may self-recover.
But the operator still has to infer when that healthy-wait story stops being plausible and becomes stall or rescue territory.

### D) Status light and peer connectivity still do too much work as proxy progress

A green check with connected peers, visible peers, or a quiet queue can all be useful.
But none of them is a complete claim that a named accepted task is moving on schedule.

### E) Rescue ownership still lives outside the motion surface

Current docs can tell you where to inspect, what warning to read, and when to collect deeper artifacts.
They still do not compile one explicit answer to who must rescue the claimed work once its heartbeat is overdue.

## What AnonSync should borrow

- visible motion witnesses like history, queues, and performance views
- explicit disclosure that some quiet periods are healthy background work
- direct warning language for known liveness degradations
- motion-adjacent columns and notification aids that help operators notice change

## What AnonSync should not clone

AnonSync should not clone a world where the operator must infer work liveness from status lights, graphs, or queue inspection alone.
It should not leave the following questions scattered across separate surfaces:

- what heartbeat is expected for this claimed work?
- what quiet window is still healthy?
- what evidence counts as motion?
- when does silence become overdue?
- when does overdue become silent stall?
- who owns rescue once the stall boundary is crossed?

## Product requirement extracted from this evaluation

AnonSync should own one stable page family for **work heartbeat and rescue truth**.
That family should make it ordinary to publish:

- claimed work item
- expected motion class
- allowed quiet window
- last observed motion
- next required heartbeat
- blocker-aware wait posture
- stall boundary
- rescue owner and rescue route
- durable heartbeat receipt

## Bottom line

Current Resilio still deserves credit for exposing useful motion and troubleshooting signals.
But it still does not own one operator-facing answer to:

> after custody is accepted, is the work still alive, how much quiet is still allowed, and who must rescue it when motion fails to return?

That is why this seam belongs on the non-clone side.
