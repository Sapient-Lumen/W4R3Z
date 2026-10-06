# Resource budgets and limits as evidence

DeriveBSD already treats *deployment* as an atomic, reviewable artifact.
A missing operational primitive is treating **resource governance** the same way: not as ad‑hoc `ulimit(1)`/rc scripts, but as **typed budgets** that:

- compile into enforcement backends (jails, rctl/racct, cpuset, PF, bhyve caps)
- produce **receipts** when applied
- emit **violation events** that can be bundled, replayed, and explained


See also: `docs/285-hierarchical-resource-limits-compilation.md` (rctl/racct compilation details and recommended v0 constraints).

This is one of those “obvious in hindsight” ideas that older ecosystems struggle to retrofit because limits were historically per-user, not per-service.

## Why bake this in now

### 1) Prevent resource incidents from becoming “mystery outages”
A CPU spiral or file-descriptor leak is only explainable if the OS can answer:

- *What budget was supposed to apply?*
- *Was it applied? When? By which change-set?*
- *What happened when it was exceeded?*

DeriveBSD’s evidence spine makes this cheap: the budget object is a stored artifact, the application is a receipt, and exceedances are events.

### 2) Adopt real, battle-tested primitives (FreeBSD rctl / illumos rctls)
FreeBSD’s `rctl(8)` provides a persistent rules database and actions when limits are exceeded (deny, signal, log, …) via `rctl.conf(5)` and the `rctl` rc service.

Illumos/Solaris resource controls (projects/tasks/zones) show the broader lesson: **limits must be scoped to the administrative unit you actually operate** (service instance, zone/jail, project), not just a login user.

## DeriveBSD model

### 1) Budgets are typed artifacts
Introduce `resource.profile` as a derivable object that holds a set of budgets.

- Store path: content-addressed (CAS)
- Review surface: diffs show what changed
- Compilation target: `rctl(8)` rules, jail parameters, cpuset masks, bhyve limits

See: `spec/resource.profile.schema.json`.

### 2) Services reference budgets explicitly
In `svcdb`, services can reference either:

- a legacy/host-native `resources.rctl_profile` string (compat)
- **or** a structured `resources.budgets[]` list that compiles into enforcement rules

See: `spec/svcdb.schema.json`.

### 3) Application is receipted
Budgets take effect through the apply engine as a change-set step (`apply-resource-budgets`).
The engine emits a `resource.budget.receipt` containing:

- the budget/profile digest
- the concrete backend rules applied (normalized)
- the scope (service/jail/instance/uid)
- correlation to the change-set and boot generation

See: `spec/resource.budget.receipt.schema.json`.

### 4) Violations are events, not logs
Limit exceedance becomes a structured `resource.violation.event` that can be:

- correlated into `causality.graph`
- packed into `incident.bundle`
- used as a policy gate (e.g., “if exceeded > N times, fail promotion”)

See: `spec/resource.violation.event.schema.json`.

## Operational patterns worth standardizing

### Budget defaults by service class
Provide prebuilt profiles for common classes:

- `svc.class=network-facing` → strict file descriptor and memory caps
- `svc.class=builder` → high CPU/mem but strict filesystem and network
- `svc.class=hypervisor-worker` → strict device node policy + CPU pinning

### “Budget capabilities” for controlled bursts
DeriveBSD already contemplates budget authority as a capability (`docs/193-resource-budget-capabilities.md`).
Budgets as evidence make that lane *actually safe*: you can grant a temporary “burst budget” as a leased capability and still have clean receipts.

## Open questions

- Do we normalize limits in human units (MiB, %CPU) or backend units (bytes, ticks)?
  - Recommendation: author in human units; compile to backend units; receipt stores both.
- Which actions do we standardize as portable? (`deny`, `signal`, `throttle`, `log`)
- How do we expose budget state in `svc.snapshot` without creating high-cardinality churn?

Related:
- `docs/143-resource-controls-rctl-racct-cpuset.md`
- `docs/214-service-supervision-health-as-evidence.md`
- RFC-0179


## References

- FreeBSD rctl(8): https://man.freebsd.org/cgi/man.cgi?rctl(8)
- Solaris/illumos resource controls overview: https://docs.oracle.com/pls/topic/lookup?ctx=E88353-01&id=REFMAN7resource-controls-7
- Oracle Solaris resource control flags/actions: https://docs.oracle.com/cd/E37838_01/html/E61043/resource-ctrls-1.html
