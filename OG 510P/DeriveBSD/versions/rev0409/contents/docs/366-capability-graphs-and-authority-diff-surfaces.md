# Capability graphs and authority-diff surfaces

We already have multiple **blast-radius diffs** (filesystem, network, devices, etc.).
This doc proposes a unifying mental model and tooling substrate:

> Every generation has an **authority graph**. Reviews see a **graph diff**.

The goal is not a single “perfect” security model, but a *repeatable* way to answer:
- What new authority exists?
- Who has it?
- How is it attenuated?
- How is it revoked?

## What is an authority graph?

A directed graph of:

- **Principals**: services, processes, jails, microVMs, users.
- **Edges (capabilities)**: handles that confer authority.

Each edge should carry minimal, reviewable metadata:

- **cap.kind**: e.g. `fs.bookmark`, `net.egress`, `net.listen`, `device.grant`, `portal.session`, `rpc.endpoint`, `uapi.surface`, `boot.bless`, `state.dataset`.
- **cap.digest**: a stable identity for the grant/endpoint/surface (often a contract digest).
- **attenuation**: facet/rights subset (what is *not* allowed).
- **revocation**: lease expiry, indirection pointer, escrow handle, or membrane boundary.
- **evidence hooks**: which receipts/events prove use or change.

The graph is not a runtime dependency.
It is a **derived explainability artifact**.

## Inputs (where the graph comes from)

The authority graph is compiled from already-existing “data-first” surfaces:

- Unit manifests (`derive.unit`) and capability routing (`docs/344-derive-unit-manifests-and-capability-routing.md`).
- Promise profiles + sandbox plans (`docs/232-service-promise-profiles.md`, `spec/sandbox.profile.schema.json`).
- Portals + permission store (`docs/179-portals-and-powerbox.md`, `docs/210-portal-sessions-and-permission-store.md`).
- Network brokers (egress/listen) and their grants (`docs/281-network-egress-broker-and-consent.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`).
- Device grants and devfs view plans (`docs/278-device-grants-and-devfs-rulesets.md`, `docs/323-devfs-views-plans-and-receipts.md`).
- Kernel UAPI registry (`docs/362-uapi-surface-registry-and-compat-gates.md`).
- Contract registry/diff gates (`docs/370-contract-registries-and-api-diff-gates.md`).
- Service identity/ownership (`docs/235-process-contracts-and-service-ownership.md`).

## Outputs (what we produce)

A minimal initial set:

- `authority.graph` — a generation-scoped snapshot (JSON), referenced from the runtime manifest.
- `authority.diff` — between two generations (JSON), used by CI/ops gates.
- `authority.explain` — query surface (“why does X have Y?”) for humans.

Implementation notes:
- `authority.graph` can reuse the canonical `capability.graph` shape (schema: `spec/capability.graph.schema.json`).
- `authority.diff` should be machine-checkable (schema: `spec/authority.diff.schema.json`).

See also: `docs/374-authority-diff-schema-and-review-workflows.md`.

This does **not** replace existing blast-radius diffs; it *derives them*.

## Review ergonomics (why this matters)

Authority drift is usually invisible because it is spread across:
- “just one more config file”
- “just one more daemon”
- “just one more ioctl”

A graph diff makes it boringly obvious:
- new endpoints that accept untrusted input
- new ambient filesystem reach
- new device exposure
- new network reach
- new identity/privilege edges

## Constraints and non-goals

- Not a complete formal model of the machine.
- Not required for boot.
- Not a substitute for sandboxing.

It is a **design-review and explainability substrate**.

## Wiring into existing policy gates

- “New authority” changes should be keyable in policy, by `cap.kind` and `cap.digest`.
- Promotion gates can require that `authority.diff` is empty (or only contains approved deltas).

See:
- blast-radius diffs: `docs/106-blast-radius-diff.md`
- explainability contract: `docs/95-explainability-contract.md`
- authority engineering: `docs/357-capability-attenuation-revocation-and-membranes.md`
