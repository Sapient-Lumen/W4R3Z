# Resilio diagnostic telemetry and evidence custody evaluation

## Purpose

The archive already had issue-home, crash-capture, diagnostic export, and performance pages.
What it still lacked was one explicit comparison document for another ordinary seam:

> when the operator asks `what exactly am I allowing this product to observe, keep, and send away?`, where does the product itself own the answer?

Current official Resilio docs are candid enough that AnonSync needs a serious answer.
Resilio does not completely hide the mechanics.
It names anonymous statistics, log-size and log-retention controls, profiler capture, hidden storage locations, restart gates, automatic log submission, and even a mobile debug ritual that routes through a magic claim string.
That honesty is worth borrowing.

## What Resilio gets right

Resilio is still right that:

- observation scope and support evidence are not the same thing
- extra capture should have an explicit enable step
- heavy capture sometimes needs a restart and a bounded reproduction window
- local evidence artifacts really do have locations, budgets, and rotation behavior
- outbound diagnostic send should admit that volume and time-to-finish matter

That is better than products that pretend support evidence simply appears by magic.

## What still should not be cloned

The page contract is still scattered.
Current official docs still require the operator to combine at least four article families:

1. **Power user preferences** for `send_statistics`, `log_size`, `log_ttl`, and `profiler_enabled`
2. **Automatic / manual debug-log collection** for enable flows, reproduction dwell, and outbound send
3. **Mobile log collection** for the hidden `SNC.DBG.LOGS` intake ritual and hidden `.synclogs` path
4. **Storage / dump articles** for where the evidence artifacts actually live

That means one ordinary answer is still reconstructed from several places:

- what low-grade telemetry is always on versus optional?
- what extra capture did I just enable, and what cost comes with it?
- what exact files or bundles now exist locally?
- what is about to leave the node if I press `send logs`?
- when do those artifacts expire or rotate away?

The product substance is good.
The page ownership is still too weak.

## Why this matters for AnonSync

AnonSync should not repeat two common mistakes here:

1. **silent observation sprawl** — background metrics, debug capture, profiler traces, and crash artifacts all blurring into one invisible bucket
2. **support ritual leakage** — requiring operators to remember hidden paths, restart requirements, and secret trigger strings just to understand what evidence exists

A serious sync product needs one stable public answer to four different questions:

- **telemetry truth** — what classes of operational data can leave or stay?
- **capture truth** — what extra instrumentation is being enabled for this investigation?
- **send truth** — what exact bundle members are included, and what is still local only?
- **retention truth** — what evidence artifacts currently exist, where, and for how long?

## Replacement pages in this revision

This revision adds four fixed pages:

- `357` — Telemetry consent
- `358` — Profiler capture review
- `359` — Diagnostic send
- `360` — Local evidence retention

Together they replace article-shaped diagnostics with product-owned evidence custody.

## The doctrinal line

Borrow directly:

- explicit enable steps for debug/profiler capture
- explicit note that some capture requires restart
- explicit local artifact paths and rotation limits
- explicit admission that outbound log transfer is a real send with volume and completion time

Do not clone directly:

- settings tables that bury telemetry alongside unrelated knobs
- hidden local artifacts without one public evidence ledger
- support-send flows that do not preview bundle membership
- mobile evidence rituals that depend on memorized magic strings rather than one stable page

## Conclusion

The correct AnonSync response is not merely `collect less`.
It is stronger than that:

> keep instrumentation explicit, but make every telemetry toggle, profiler run, outbound evidence send, and local debug artifact resolve into one stable explanation surface that says what is being observed, why it exists, what it costs, what leaves the node, what stays local, and when it expires or rotates away.
