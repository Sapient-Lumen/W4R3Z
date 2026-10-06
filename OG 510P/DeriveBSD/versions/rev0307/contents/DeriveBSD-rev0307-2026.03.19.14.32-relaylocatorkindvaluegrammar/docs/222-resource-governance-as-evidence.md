# Resource governance as evidence (rctl / cgroup / PSI lessons)

Most OSes treat resource limits as:
- scattered daemon flags (`--memory=...`)
- hidden kernel defaults
- tribal knowledge about “this box is overloaded”

DeriveBSD already has the right *pattern* for fixing this: **inventory → explicit plans/policy → receipts → health gates**.

Bake in a first-class lane for **resource governance**:
- a host can answer “what are the limits, right now?” without parsing configs
- violations are **typed events**, not strings
- pressure can be used as an input to **health-gated commit/rollback**
- enforcement is a policy-bound capability, not ambient root power

## Lessons worth stealing

### FreeBSD / Solaris `rctl`
`rctl` generalizes per-process `rlimit` into limits attached to higher-level groupings (users, jails, projects/zones).
It also has the under-appreciated property we want for DeriveBSD: a **rule database** that can be updated at runtime.

References:
- FreeBSD: `rctl(8)` + Hierarchical Resource Limits wiki
- Solaris/illumos: `rctl` and zone/project resource controls

### Linux cgroup v2
Even though DeriveBSD isn’t Linux, cgroup v2 is a useful conceptual reference for:
- a **hierarchy** of resource domains
- controllers per resource type (CPU/memory/IO)
- “delegation” as an explicit policy boundary (who can change limits)

### PSI (pressure stall information)
PSI is valuable because it answers: “are we *waiting* on a resource?” not just “how busy are we?”
This is the missing signal that makes health gating smarter than “service is up”.

DeriveBSD should have an analogous **pressure** surface (even if implemented differently in-kernel).

## DeriveBSD approach

### 1) `resource-policy` (desired governance)
A `resource-policy` is a structured object that declares:
- the **subject** (workload/service/jail/microVM identity)
- the **budgets** / caps / shares
- what to do on breach (log, throttle, kill, emit fault, capture incident bundle)

This is intentionally a *portable* layer:
the apply engine maps it to the host’s enforcement backend (e.g., `rctl`, cpusets, IO throttles).

### 2) `resource-receipt` (what actually happened)
Every attempt to apply a policy emits a receipt:
- backend used
- applied rule set (or diffs)
- success/failure + reason
- correlation ids to the change-set step

### 3) `resource-snapshot` (what is enforced + pressure now)
A snapshot is the queryable view:
- effective limits per subject
- current usage summary
- pressure summary (cpu/mem/io), when available

Snapshots are produced:
- on demand
- periodically (for fleet observability)
- automatically as part of incident bundles

### 4) `resource-event` (violations and actions)
Violations are first-class events:
- `resource.violation.*`
- `resource.pressure.*`
- `resource.action.*` (throttle/kill/restart)
- `resource.policy.applied`

These events can:
- feed fault management (`fault-event` escalation)
- feed service supervision restarters (“service is flapping because it’s memory-capped”)
- be used as gate inputs (“commit only if pressure is below threshold for N seconds”)

## Wiring into the ops spine
- `change-set`: add `apply-resource-policy` step (near `apply-config` / `reconcile-services`)
- health-gated updates can consult `resource-snapshot`
- incident bundles should include: latest policy, latest receipt, and a snapshot
- event journal stores `resource-event` records and supports correlation by `change_id`

See: `docs/219-change-sets-and-apply-engine.md`, `docs/215-structured-event-log-as-evidence.md`,
`docs/216-incident-snapshots-and-support-bundles.md`, RFC-0157.

Last updated: 2026-02-24
