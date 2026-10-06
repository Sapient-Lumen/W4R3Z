# Learned resource budgets (observation mode) and “right-sized by default” services

DeriveBSD treats *authority* as something you can shrink by iteration (promise profiles; network policy learning).
The same principle applies to **resource consumption**.

In hostile-builder and multi-tenant scenarios, “resource DoS” is a first-class failure mode:
- a compromised builder can exhaust RAM and thrash the host
- an accidentally unbounded service can starve other compartments
- a rollout can regress memory/CPU and only show up after it hits production traffic

Greenfield advantage: bake in a **learn → review → enforce** loop so “reasonable budgets” are cheap.

## Prior art: observed-usage → recommended budgets

- **Kubernetes Vertical Pod Autoscaler (VPA)**: a recommender analyzes current and historical CPU/memory usage and produces bounded recommendations.
  - https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/

- **systemd resource control**: cgroup-backed controls split “soft limits” (pressure) vs “hard stops” (OOM-kill), and explicitly recommends using `MemoryHigh=` as the main mechanism with `MemoryMax=` as a last line of defense.
  - https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html

- **Pressure Stall Information (PSI)**: Linux exposes explicit “time stalled due to resource contention” metrics, which are often more actionable than raw usage.
  - https://docs.kernel.org/accounting/psi.html

- **FreeBSD rctl/racct**: `rctl(8)` can enforce limits and actions across users/processes/jails; the FreeBSD Handbook explicitly calls out rctl for **jail resource limits**.
  - https://man.freebsd.org/cgi/man.cgi?rctl%288%29
  - https://docs.freebsd.org/en/books/handbook/jails/

## DeriveBSD proposal: `derive learn resources` (usage → resource profiles / policy patches)

Introduce a first-class learning workflow for resource governance.

### `derive learn resources <unit> --suite <tests>`

Runs the unit (or its test suite) with:
- `racct` enabled (where supported) and per-service accounting enabled
- explicit observation window bounds (time + max samples)
- optional “pressure” sampling (platform-specific)

Produces:
- `resource.snapshot` evidence (baseline + per-subject accounting snapshot)
- `resource.budget.usage` evidence (time-series-ish summary: peaks, percentiles, OOM/kill events)
- a candidate patch as a **generic** `policy.suggestion` artifact:
  - target: `resource.profile` and/or `resource.policy`
  - patch: `json-merge-patch` (default) or `jsonpatch`

Schema: `spec/policy.suggestion.schema.json`.

### What gets learned

Learning should focus on budgets that meaningfully cap blast radius while staying stable across runs:

1) **Memory (rss / swap) + OOM signals**
   - propose: `memory.rss` budget from P95/P99 + headroom
   - promote to “hard stop” only after confidence (avoid flapping)

2) **CPU burst vs sustained**
   - propose: short-window caps (e.g., `cpu.percent` with `window: 10s`) for bursty services
   - treat long-window sustained caps as a separate control

3) **Process/thread/FD ceilings**
   - propose tight maxima (cheap guardrails)

4) **I/O / write budgets**
   - for builders or log-heavy services, propose `fs.write.bytes` windows

5) **Network byte budgets**
   - sometimes more stable than “connection counts”; caps data exfil volume even when destinations are constrained

### Safety rules (what must not be auto-approved)

Learned budgets are **suggestions**, not enforcement:

- Default: produce `action: log` or `throttle` suggestions, not `kill`, unless explicitly requested.
- Never auto-propose budgets that are *higher* than current policy unless a human opts in.
- Always include a “max allowed” clamp in the suggestion metadata (to prevent a single noisy run from raising budgets unbounded).

### Drift posture: budgets as part of “authority budgets”

Once budgets exist, “permission drift” must include *resource drift*:
- sudden RSS growth is as important as “new network destination”
- CPU/FD regressions should be diffable between generations

This plugs into:
- `docs/298-authority-budgets-and-permission-drift-alarms.md`
- `docs/247-resource-budgets-and-limits-as-evidence.md`
- `docs/285-hierarchical-resource-limits-compilation.md`

## Open questions

- Portable “pressure” analogs on FreeBSD (PSI-like signals) vs just accounting peaks.
- How to model “multi-mode” services (feature flags) without over-permitting (tie into scenario test suites).
- How to avoid feedback loops where enforcement changes the observed profile (measure in observe mode first).

Last updated: 2026-02-26r89
