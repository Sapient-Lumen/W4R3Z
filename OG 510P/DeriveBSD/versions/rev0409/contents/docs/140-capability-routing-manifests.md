# Capability routing manifests (Fuchsia lessons)

Fuchsia’s Component Framework uses **capability routing** as its main access-control mechanism:
components are sandboxed, and they can only interact with resources explicitly routed to them.

References (primary):
- Fuchsia “Capabilities” (concepts): https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- Fuchsia “Original Principles” (explicit routing as access control): https://fuchsia.dev/fuchsia-src/contribute/contributing-to-cf/original_principles
- Fuchsia components intro (sandboxed modules + capabilities): https://fuchsia.dev/fuchsia-src/get-started/learn/intro/components

## Why this is juicy for DeriveBSD

DeriveBSD already wants:
- **least authority** (Capsicum/jails/microVMs)
- **policy as data** (decision records)
- **reviewable diffs** of authority changes

Capability routing is the ergonomic layer: an explicit, reviewable **grant graph** that says
what each compartment *is allowed to touch*.

## DeriveBSD translation

Add a derived, canonical artifact:

`caproute.json` (hashable, diffable)
- produced during **Plan → activation planning**
- consumed by activation/runtime tooling
- recorded in the Policy Decision Record

A normalized tooling view can be derived from this manifest:
- `capability.graph` (canonical JSON for lint/viz; see `docs/189-capability-graph-lint-and-viz.md`)

### Capability types (DeriveBSD-shaped)

Keep the set small and mechanically enforceable:

1) **FS views**
   - read-only mounts (store paths, artifacts)
   - state mounts (explicit ZFS datasets)

2) **Network rights**
   - pf anchor IDs and flow policy references
   - “deny network” as default

3) **Control-plane RPC endpoints**
   - vsock services / unix sockets / pipes
   - mediated via policy (qrexec-like)

4) **Secrets handles**
   - *not bytes in the manifest*
   - references to sealed secret IDs + delivery mechanism

5) **Device nodes**
   - explicit devfs rules (jails)
   - minimal sets (e.g., vmm for bhyve workers)

## Design constraints (to keep it small)

- The routing manifest is **derived**, not handwritten.
- The schema must be stable enough to diff, but extensible.
- Enforcers must be narrow:
  - jail mounts/devfs rules
  - pf anchors
  - Capsicum “preopened handles”
  - microVM device wiring

## Where it plugs in

- **Blast radius diffs**: capability graph changes are authority changes.
- **Explainability**: “why does component X have access to Y?” becomes routable facts.
- **Hostile builders**: builder compartments get *minimal* routed capabilities.

See RFC-0092.

Implementation note: routes are easiest to realize when the crossing substrate can *carry capabilities* (object references / brokered handles). See: `docs/183-object-capability-rpc.md` and the lease/revocation pattern in `docs/182-capability-leases-and-revocation.md`.

