# Devfs views as derived operations: plans, receipts, and drift events

FreeBSD gives us a powerful primitive for sandboxing jails: **per-jail devfs mounts** plus **devfs rulesets**.
But in practice `/dev` becomes folklore:

- a jail starts with “whatever the base system had”
- an operator hotfixes `/etc/devfs.rules`
- a device appears after an update (new driver, new node naming)
- an incident ends with “why did this sandbox suddenly have `bpf`?”

DeriveBSD’s posture is: **device nodes are authority**, so `/dev` visibility must be:

- **compiled** from intent (promise profiles + device grants)
- **diffable** (as a small canonical IR)
- **receipted** (what rules were applied; what nodes were observed)
- **drift-monitored** (unexpected nodes are incident-grade)

This doc formalizes `/dev` views as a first-class derived operation. The new product default in `docs/476-device-authority-posture-by-profile.md` now tells us where compiled-minimal views are the baseline, where portal/device-domain mediation is preferred, and where raw device-node compatibility remains explicit fallback rather than ambient authority.

Related:
- Treat `/dev` as authority: `docs/278-device-grants-and-devfs-rulesets.md`
- Device isolation domains: `docs/204-device-isolation-domains.md`
- Lease revocation spine: `docs/249-lease-registry-and-cross-lane-revocation.md`
- Promise vocabulary → compilation: `docs/271-promise-profile-vocabulary-and-lint.md`

References (FreeBSD primitives):
- `devfs(8)` : https://man.freebsd.org/cgi/man.cgi?query=devfs&sektion=8
- `devfs.rules(5)` : https://man.freebsd.org/cgi/man.cgi?query=devfs.rules&sektion=5
- `jail(8)` warning about devfs exposure: https://man.freebsd.org/cgi/man.cgi?query=jail&sektion=8

---

## Product-shape default now fixed

The archive now has a stable A–D answer for device authority:

- **A**: compiled-minimal service `/dev` views with lease-shaped expansion
- **B**: portal-first / host-owned raw sensitive devices, with trusted-UI-visible exceptions
- **C**: compiled-minimal preferred, explicit compatibility fallback for raw device-node consumers
- **D**: compiled-minimal sealed production posture with offline/approved maintenance expansion

This doc stays focused on the lower-level plan/receipt/event machinery that realizes those defaults.

## New evidence objects

### `devfs.view.plan`
A digest-bound plan describing the intended `/dev` view for a target compartment.

- Inputs: promise profile intent, device attach grants, host policy constraints
- Output: canonical rules list (portable IR), plus optional rendered backend artifacts (devfs.rules text digest)

Schema + example:
- `spec/devfs.view.plan.schema.json`
- `spec/examples/devfs.view.plan.json`

### `devfs.view.receipt`
A receipt describing what was applied and what was observed.

- binds to `plan_id` + `plan_digest`
- records the effective ruleset id/name used by the backend
- optionally records a privacy-safe digest of observed nodes

Schema + example:
- `spec/devfs.view.receipt.schema.json`
- `spec/examples/devfs.view.receipt.json`

### `devfs.view.event`
An event stream object for drift/deny incidents.

- emitted by appliers and drift-checkers
- used by incident snapshots and drift alarms

Schema + example:
- `spec/devfs.view.event.schema.json`
- `spec/examples/devfs.view.event.json`

---

## Compilation: where the devfs view comes from

A devfs view is **not authored by hand** in the steady state.
It is compiled from:

1) **Promise profile** (intent vocabulary)
- “no raw devices”, “no packet capture”, “needs RNG”, “needs tty”, etc.

2) **Device attach grants** (lease authority)
- which concrete device(s) may be present *right now*
- constraints like read-only, consent gates, TTL

3) **Host policy** (platform constraints)
- “never expose `bpf` in service jails”, “HID must be portal-only”, etc.

The compiler produces:

- `devfs.view.plan` (canonical IR)
- (optional) a backend rendering artifact (devfs.rules text), referenced by digest

### Canonical IR shape (v0)

DeriveBSD keeps the IR intentionally small:

- a `baseline` (usually `service-minimal`)
- a list of **rules** (hide/unhide/perm) expressed in a stable ordering

The IR is the diff target and the audit unit.
Backend renderings are treated as *derived artifacts*.

---

## Apply + observe

At apply time, the host:

1) allocates or selects a devfs ruleset identifier (backend detail)
2) applies the rules to the target devfs mount
3) optionally enumerates the resulting `/dev` view and computes `observed_nodes_digest`
4) emits `devfs.view.receipt`

### Privacy posture

Even “just device node names” can leak hardware details.
Default posture:

- receipts are **digest-first** (count + digest)
- raw node lists appear only under explicit export/retention policy
- unexpected node samples (if included) should be truncated and/or hashed

---

## Drift monitoring

Drift checks can be triggered by:

- device attach/detach receipts (view should shrink/grow deterministically)
- periodic scanning (cheap; node lists are small for minimal views)
- `devd`-driven triggers (hotplug)

On drift, emit `devfs.view.event`:

- `ruleset-mismatch` (effective rules digest differs from plan)
- `unexpected-node` (node appears that is not in the expected allowlist)
- `write-denied` (policy denied a requested expansion)

These events should be incident-grade when they imply authority expansion.

---

## How this plugs into the component descriptor spine

`derive.unit` already compiles high-level intent to concrete backends.
Devfs views become a named compiled output alongside `preopen.map` and `mount.view`:

- promise profile → `devfs.view.plan`
- activation applies the plan and emits `devfs.view.receipt`
- drift monitoring emits `devfs.view.event`

See: `docs/297-component-descriptors-and-compiled-runtime-manifests.md`.

---

## Open questions

- Do we support multiple renderers (devfs.rules text vs direct `devfs rule` command streams) as adapter backends?
- What is the minimal “service-minimal” pseudo-dev set (and do we version it as policy)?
- For microVMs: do we treat `/dev` as an in-guest concern, or do we require paravirt device portals to keep the host authority model consistent?

Last updated: 2026-03-06r205
