# Derive unit manifests: “component declarations” for services, brokers, and microVMs (Fuchsia lesson)

DeriveBSD already has two strong ideas:
- **crossings are contracts** (interfaces are review surfaces)
- **authority is routed, not ambient** (leases, portals, capability routing manifests)

Fuchsia’s Component Framework is a good reminder that these ideas get *operationally cheap* when the system has a single,
first-class **component declaration** that names:
- what the component **uses**
- what it **provides**
- what it **offers** to children / peers
- what it **exposes** outward

DeriveBSD should treat `derive.unit` as that declaration.

## Why this matters (greenfield leverage)

Older ecosystems often split “service configuration” across:
- init system units
- ad-hoc policy (firewall rules, sudoers, SELinux/AppArmor)
- runtime wiring (sockets, env vars, secrets, mounts)

The result is that **authority changes hide in many places**.

A unit manifest gives us a single diff surface:
- capability routing changes show up next to the executable change
- contract surface changes (RPC IDL digests) show up next to the version bump
- resource budgets / observability knobs show up next to health gates

## DeriveBSD mapping

### 1) `derive.unit` is the source-of-truth declaration

Keep `derive.unit` as the *human-facing* source document (what you author), then compile it into:
- `svcdb` entries (service graph)
- `caproute.json` (normalized capability routing)
- `contractset.json` (RPC contract digests bound to endpoints)
- per-backend wiring plans (jails/devfs/pf/vmm)

The important discipline: **only the compiler emits runnable wiring**.

### 2) Separate “who can call” from “what bytes are called”

For any IPC endpoint:
- *who can call* is a routing/lease decision (policy-keyed)
- *what is called* is a contract digest (artifact-bound)

This mirrors Singularity-style contract channels and prevents “stringly-typed admin sockets” from becoming ambient authority.

See: `docs/12-design-principles.md`, `docs/183-object-capability-rpc.md`, `docs/339-singularity-manifests-and-contract-channels.md`.

### 3) Capability routing wants a tree (or at least a graph)

Fuchsia makes capability routing legible by embedding it in a **component instance tree**.
DeriveBSD can get the same effect without copying the whole model:
- the service dependency graph already exists (`svcdb`)
- make capability offers explicit along those edges
- compile a normalized routing graph artifact for lint/viz

See: `docs/140-capability-routing-manifests.md`, `docs/173-compiled-service-database-bundles.md`.

## Tight “day-0” rules (to keep this from sprawling)

1. A unit manifest must be sufficient to answer:
   - what does this component run?
   - what authority does it gain?
   - what contracts does it speak?
   - what evidence does it emit?

2. Any new capability type must:
   - have a **mechanical enforcer**
   - be represented in the normalized routing graph
   - show up in blast-radius diffs

3. “Escape hatches” are allowed, but only as explicit, receipted lanes.

## References

- Fuchsia capabilities (concepts): https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- Fuchsia component manifests overview: https://fuchsia.dev/fuchsia-src/concepts/components/v2/component_manifests

Last updated: 2026-02-27
