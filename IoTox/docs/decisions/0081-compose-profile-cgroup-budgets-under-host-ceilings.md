# ADR 0081: Compose profile cgroup budgets under host ceilings

- Status: accepted and implemented in rev0030
- Date: 2026-08-18
- Scope: local Ratox terminal policy, cgroup-v2 admission, startup preflight, and aggregate runtime truth
- Wire effect: none

## Context

rev0029 can apply one administrator-owned cgroup-v2 resource envelope to every hardened PTY session.
That closes the unbounded-session gap, but it makes materially different local workloads share the
same process, memory, swap, and CPU maxima. The roadmap explicitly left per-profile budgets open.

A profile budget must not become an authority escalation. Remote OPEN bytes choose neither profile nor
limits: the authenticated stable principal is bound to an owner-private local profile. Even so, a
locally edited profile must never be able to weaken the daemon administrator's deployment-wide
ceiling. Startup must prove every distinct effective controller policy before network activation, and
the production factory must independently recompute the same result so alternate call paths cannot
bypass it.

Linux cgroup v2 is hierarchical: descendant settings can restrict further but cannot override
ancestor restrictions. IoTox currently writes its host and profile policy into the same per-session
leaf rather than constructing a second nested cgroup level, so it needs an explicit monotone
composition with equivalent security direction.

## Decision

1. Add `CgroupResourceLimits cgroup_limits` to the local `Profile` model and introduce canonical
   `iotox-terminal-profile-v3` records with five ordered `none|u64` fields for pids, memory, swap, CPU
   quota, and CPU period.
2. Continue accepting canonical v1 and v2 records. They decode with an empty profile budget; v1 also
   retains explicit compatibility confinement. The public encoder always emits v3.
3. Validate host and profile budgets through one shared implementation. Preserve the existing host
   page-alignment and CPU syntax bounds, including meaningful zero swap and the rule that a period
   requires a quota.
4. Compose scalar maxima by selecting the smaller configured value. An absent side inherits the
   configured side. Two absent sides leave the controller untouched.
5. Compose CPU bandwidth by selecting the lower exact `quota/period` rational. Treat an absent period
   as 100,000 microseconds. Use an overflow-free continued-fraction comparison; do not use floating
   point or cross-products that can overflow 64-bit input ranges. On equal ratios retain the host
   representation.
6. Require an explicit delegated cgroup-v2 root whenever any enabled profile has a nonempty budget.
   Disabled profiles may stage future policy without activating host requirements.
7. During host activation, compute the effective budget for every enabled profile and deduplicate
   preflight by `(payload identity, effective budget)`, not identity alone. Distinct policies sharing
   an identity receive distinct disposable probe leaves.
8. In the production POSIX factory, recompute host/profile composition before filesystem or spawn
   work and pass only the effective budget to session-cgroup creation.
9. Publish aggregate configuration truth only: whether a host budget is configured, the enabled
   profile-budget count, and the distinct preflight-policy count. Do not publish profile IDs,
   identities, numeric limits, paths, or terminal content.

## Consequences

- A profile can add or tighten a limit but cannot relax a deployment ceiling.
- Different profiles may receive different resource budgets without changing Ratox wire protocol,
  authority semantics, or remote request syntax.
- Preflight cost is bounded by the existing profile maximum and by exact policy deduplication.
- Canonical policy bytes gain a v3 migration step; existing v1/v2 stores continue to load without
  invented limits.
- CPU composition remains exact across the accepted signed-64-bit quota range.
- IoTox still does not implement per-device I/O throttling, PSI-based admission, aggregate host-wide
  reservation, or defense against a separate privileged writer mutating the delegated subtree.

## Rejected alternatives

### Let profiles replace the host envelope

Rejected because a local profile edit could weaken administrator-owned policy and because a missing
field would have ambiguous replacement semantics.

### Use only kernel ancestor hierarchy

Rejected for this revision because the current delegated namespace owns one session leaf per PTY.
Adding persistent per-profile ancestors would complicate orphan ownership, cleanup, and policy-update
semantics. Explicit composition preserves the same monotone restriction direction without expanding
that lifecycle surface.

### Compare CPU limits with floating point

Rejected because rounding can reverse decisions near equal ratios and cannot provide canonical exact
behavior over the full accepted range.

### Compare CPU limits by multiplying quota and period

Rejected because valid quota values up to `INT64_MAX` and periods up to 1,000,000 overflow 64-bit
cross-products.

### Preflight once per identity

Rejected because two profiles with the same payload uid may require different controllers or exact
values. An identity-only probe would leave one policy unproved before network startup.
