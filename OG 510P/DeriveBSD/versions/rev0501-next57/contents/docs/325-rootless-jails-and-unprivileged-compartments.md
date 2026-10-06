# Rootless jails and unprivileged compartments (hierarchical jails + lease-backed brokers)

A greenfield OS can make “run a sandbox” feel as normal and safe as “run a process”.
Linux got a lot of mileage out of **rootless containers** (user namespaces): ordinary users can create containers without host-root.
FreeBSD jails are a stronger primitive than chroot, but **creating or attaching to jails is normally privileged**.

DeriveBSD’s stance: steal the *UX* of rootless containers **without** pretending the host is unprivileged.
Do it with explicit delegation:

- a **broker** that owns the dangerous privileges
- a bounded “compartment namespace” handed out as a **lease**
- confinement defaults that are reviewable (promise profiles, devfs views, budgets)
- receipts for every compartment lifecycle event

## 1) Prior art worth stealing

### Rootless container UX
Rootless Podman commonly maps the calling user’s UID into the container as “root” inside a user namespace, so container creation can be unprivileged.
Reference: https://www.redhat.com/en/blog/rootless-podman-user-namespace-modes

### FreeBSD jails are privileged, but hierarchical jails exist
- `jail_set(2)` explicitly fails with `EPERM` when a process is not the super-user (among other cases), and `jail_attach(2)` similarly rejects non-super-user attach attempts.
Reference: https://man.freebsd.org/cgi/man.cgi?query=jail&sektion=2

- `jail(8)` documents **hierarchical jails** via `children.max` and states that jailed processes cannot create child jails with *greater* permissions than their parent (no “relaxing” confinement).
Reference: https://man.freebsd.org/cgi/man.cgi?jail(8)

These two facts suggest a useful pattern: **delegation-by-confinement**.

## 2) DeriveBSD shape

### A) “Jail broker” as the only privileged surface
Introduce a small privileged daemon (name sketch: `derive-jailbrokerd`) that is the only component allowed to:

- create/modify/remove top-level jails
- bind network addresses / manipulate host pf anchors
- attach devfs rulesets
- apply rctl/cpuset budgets

Everything else is an unprivileged client.

This is consistent with the archive’s general pattern:
- “authority is a lease, not ambient” (net egress/listen brokers)
- “compiled confinement profiles are artifacts” (promise profiles)

### B) A bounded “compartment namespace” lease
When a user (or service) wants “rootless sandboxing”, they request a lease for a compartment namespace.
The broker returns a lease bound to:

- **profile** (which jail knobs are allowed): `docs/150-jail-profiles-and-allowlist-knobs.md`
- **devfs view** (which device nodes exist): `docs/323-devfs-views-plans-and-receipts.md`
- **egress/listen posture** (no ambient network): `docs/281-network-egress-broker-and-consent.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`
- **resource budgets** (DoS containment): `docs/143-resource-controls-rctl-racct-cpuset.md`
- **expiry + revocation hooks** (it’s a lease)

Crucial constraint: the lease should be narrow enough that it is safe to hand to an unprivileged developer *by default*.

### C) Two implementation options (both useful)

**Option 1: Broker-mediated lifecycle (simplest, most portable)**
- Unprivileged user calls the broker API.
- Broker performs the privileged jail operations and returns a handle.
- Handle is used for non-privileged actions (start/stop, query, logs), with all privilege boundaries enforced in the broker.

**Option 2: Hierarchical-jail delegation (fast path / future hardening)**
- Broker creates a per-user “namespace jail” with a strict baseline and `children.max > 0`.
- A confined helper inside that namespace is allowed to create child jails *only within that confinement envelope*.
- Even if the helper is compromised, it cannot mint a child jail with broader privileges than the namespace jail (per `jail(8)`).

DeriveBSD can start with Option 1 and graduate to Option 2 where it meaningfully reduces broker complexity.

## 3) UX goals (what should feel boring)

- `derive sandbox run <cmd>` works as an ordinary user.
- The created compartment’s authority surface is visible in diffs:
  - promise profile / devfs view / budgets / network leases
- `derive explain` can answer: “why did this sandbox have access to X?”
- Every lifecycle step emits receipts that can be bundled in incident/support exports.

## 4) Security notes (don’t fool ourselves)

- Rootless is about *who can request a sandbox*, not “there is no privileged code.”
  The broker is privileged; keep it tiny and harden it aggressively.
- Treat “developer sandbox” as a first-class threat model tier:
  - deny-by-default network
  - deny-by-default devices
  - no mount permissions
  - strict budgets
- Keep the escape hatch honest: if a workflow truly needs more privilege, it should require an explicit policy decision (or breakglass) rather than quietly widening the rootless baseline.

Last updated: 2026-02-26r86
