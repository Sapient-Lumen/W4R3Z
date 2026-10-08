# Crate resource-surface lanes — 2026-03-17

This note keeps **P-0521 Crate Resource Surface Pack Kit** from collapsing into generic “better performance docs”, “better observability”, or “better async capacity tuning”.

## The lane

**P-0521** is the crate-authored, receiver-facing artifact layer for:

- queues, pools, caches, worker classes, and other retained resource classes,
- boundedness versus effectively-unbounded posture,
- saturation behavior,
- reclaim and release obligations,
- named capacity profiles,
- and release-to-release resource diffs.

It answers:

- “What can this crate accumulate or keep around?”
- “Which of those things are actually bounded?”
- “What happens when demand outruns supply?”
- “Which knobs matter for backlog, memory, or pool size?”
- “How did the crate’s resource posture change across releases?”

## What it is not

### 1. Not performance envelopes

**P-0517** is about workload posture, metrics, and performance budgets.
**P-0521** is about retained resources, bounds, and saturation semantics whether or not benchmark numbers look good.

### 2. Not lifecycle surfaces

**P-0520** is about background work, cancel safety, shutdown, and drain obligations.
**P-0521** is about steady-state capacity posture and overload behavior even before shutdown begins.

### 3. Not observability surfaces

**P-0518** is about emitted telemetry.
**P-0521** is about the actual queues, pools, buffers, and budgets whether or not the crate emits metrics for them.

### 4. Not authority surfaces

**P-0519** is about what host powers a crate may touch.
**P-0521** is about how much work or state the crate may retain once it is using those powers.

### 5. Not configuration scenarios

**P-0516** is about named setup recipes.
**P-0521** may import them, but it is specifically about resource posture after a configuration has been chosen.

### 6. Not limiter/cache/queue substrate

`tokio::sync::mpsc`, `tower::limit`, `governor`, Moka, and similar crates provide implementation substrate.
**P-0521** sits above them as the contract layer that says what one crate promises downstream users.

### 7. Not metrics/profiling substrate

`tokio-metrics`, runtime metrics, profilers, and dashboards observe behavior.
**P-0521** is the declared and fixture-checked support surface that says what should be watched and why.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **configuration/setup scenarios**,
2. **performance envelopes**,
3. **telemetry / observability**,
4. **authority / ambient powers**,
5. **lifecycle / shutdown truth**,
6. **receiver-facing resource-surface contracts**,
7. or **lower-level queue/cache/limiter/runtime substrate**.

Do **not** let the archive quietly rephrase resource-surface contracts as “better perf docs”, “another backpressure crate”, or “just add metrics”.
