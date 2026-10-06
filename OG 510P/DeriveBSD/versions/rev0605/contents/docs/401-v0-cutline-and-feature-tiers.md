# v0 cutline + feature tiers (how DeriveBSD ships without becoming a monster)

**Tier:** A (Core meta-doc)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, supply-chain, operability
**Patterns:** Registry→Diff→Gate  

DeriveBSD’s archive contains many *good* ideas.
The failure mode is not “bad ideas,” it’s **shipping nothing** because the design surface never stops expanding.

This doc is a **meta-engineering** guardrail: it defines a v0 cutline and a small set of feature tiers so we can:

- keep the Derive core small
- ship a coherent system
- still make space for ambitious optional lanes

If a feature can’t be placed in a tier and doesn’t help the v0 cutline, it should be treated as *design tourism* until it proves otherwise.


## Runtime-first correction (2026-06-18r615)

The archive is contract-rich but product-poor. A schema, ADR, example, or checker is not delivery unless it closes an executable product gap. Until the golden thread below passes on a clean FreeBSD 15.1 host, profile A (fleet host/control plane) is the sole v0 product target; profiles B–D remain compilation targets for later work, not parallel launch obligations.

The v0 golden thread is one operator-visible flow:

1. parse one minimal declarative spec;
2. lock every input by digest;
3. build one artifact in a network-denied FreeBSD sandbox;
4. publish it to a content-addressed store with provenance;
5. activate it through a ZFS boot environment and prove rollback;
6. launch and stop one bhyve workload through a least-privilege control plane; and
7. reconstruct the complete why/source/authority chain with `derive explain`.

**Admission rule:** no new ADR, RFC, schema, example family, checker, or proof-transport layer may enter Tier A/B unless it directly unblocks a failing golden-thread step or converts an observed real-host failure into an executable regression. Prefer implementation plus end-to-end tests over another contract. The existing removable-media proof lane may collect its first real host result, but further hardening waits for evidence from that run.

**Exit evidence:** a fresh host completes the flow from one documented entry point; a repeated build has the expected digest behavior; activation and rollback are observed; the workload lifecycle emits receipts; and `derive explain` resolves those receipts back to locked inputs and policy. Green internal consistency alone is not a ship signal.

## 0) Tiers + profiles (two axes, no forks)

Tiers answer **how central** a feature is.
Profiles answer **for whom it is default**.

DeriveBSD must stay viable for multiple product shapes (A–D) without forks.
Use product profiles as compilation targets for defaults and gates:

- overview: `docs/411-product-profiles-as-compilation-target.md`
- schema: `spec/product.profiles.schema.json`
- example: `spec/examples/product.profiles.json`

A feature that is not universal should live as a **profile default** or an **optional lane**, not as a new global obligation.

## 1) Feature tiers

### Tier A — Core (must exist for DeriveBSD to be DeriveBSD)
These are the invariants that everything else assumes:

- **Spec → Lock → Plan → Artifact** pipeline (`docs/02-derive-core.md`)
- content-addressed store + hashing discipline (`docs/03-store.md`)
- sandboxing model (`docs/04-sandbox.md`)
- trust/caches/channel metadata invariants (`docs/05-caches-trust.md`, `docs/61-channel-metadata-tuf-inspired.md`)
- atomic activation + rollback substrate (ZFS boot environments) (`docs/06-system-activation.md`)
- structured outputs + evidence spine hooks (`docs/38-structured-outputs.md`, `docs/229-evidence-spine-overview.md`)

Core rule: **new core is forbidden by default**.
If something must be core, it needs an ADR plus a “why this cannot be an optional lane” argument.


### Tier B — Base (default-on, shipped in v0)
These are the minimum “it feels real” features that v0 ships with, but they are not allowed to bloat the core:

- host generations mapped to BEs + safe switch/rollback (`docs/69-host-generations-bectl.md`)
- minimal service supervision + manifests (`docs/214-service-supervision-health-as-evidence.md`, `docs/344-derive-unit-manifests-and-capability-routing.md`)
- microVM artifact target + bhyve backend mapping (`docs/24-microvm-artifact-target.md`, `docs/40-bhyve-config-mapping.md`)
- control plane (`derive-vmmd`) in a least-privilege posture (`docs/29-vm-control-plane.md`)
- baseline networking model (pf anchors, virtual networking defaults) (`docs/26-virtual-networking-pf.md`, `docs/67-pf-anchors-per-instance.md`)
- developer UX parity via devshells (`docs/159-devshells.md`)

Base rule: base features must have **small, typed contracts** and clear removal boundaries.


### Tier C — Optional lanes (supported, default-off)
Optional lanes are a greenfield advantage: they let DeriveBSD be ambitious without making every deployment pay the cost.

Examples:
- transparency logs / witness networks
- verified execution
- remote attestation admission
- CHERI lane
- chaos experiments
- netgraph/netmap datapaths

Optional lane rules:

- **default-off** unless a specific deployment opts in
- must map to the pattern catalog (plan→receipt, registry→diff→gate, broker→lease, etc.)
- must have a “kill switch” story (policy disable, safe fallback)
- must show up in drift surfaces (closure diff / authority diff / trust-boundary diff, as applicable)


### Tier D — Research lanes (docs-only until proven)
These are high-entropy ideas that are valuable to explore but should not be allowed to quietly become obligations.

Rules:
- may exist as docs/RFCs
- must not introduce required dependencies
- if promoted to Optional or Base, must pass the design-review rubric + pattern-fit discipline


### Tier E — Adapters (interop lanes, quarantined by design)
Interop is necessary, but it must never become the real product.
Adapters are lanes that bridge to existing ecosystems (ports/pkg, pkgbase, OCI transports, full TUF, etc.).

Adapter rules:
- treated as **tainted imports** unless proven (Quarantine → Promote)
- must produce receipts and be visible in closure diffs
- must include a strangler-style replacement plan (see `docs/402-adapter-lanes-and-strangler-discipline.md`)


## 2) The v0 cutline

DeriveBSD v0 should be “small but real”:

1) **Build & trust pipeline**
   - store + hashing
   - sandboxed builds
   - signed artifacts + channel metadata
   - reproducibility knobs (but not necessarily full diversity builds)

2) **Host lifecycle**
   - disk layout + install as derived operations
   - BE-backed activation + rollback
   - a minimal health gate (boot assessment + “commit”)

3) **MicroVM-first runtime**
   - a microVM artifact target
   - a least-privilege control plane
   - baseline networking + storage wiring

4) **Operator UX**
   - explain-by-default (`derive explain`, diffs, receipts)
   - support bundles + deterministic exports
   - JIT operator access leases (even if minimal)

5) **Developer UX**
   - devshells as first-class artifacts

Everything else must justify itself as:
- necessary to ship v0, or
- an optional lane with explicit boundaries.


## 3) Promotion rules (how features move between tiers)

A feature is eligible to move “up” a tier when:

- it has a small typed contract surface (schemas/IDL)
- it fits an existing pattern (or adds exactly one new pattern worth the entropy)
- it is testable and evidence-producing
- it has an operational story (failure modes + rollback)

Use the design-review rubric:
- `docs/348-design-review-rubric-and-feature-intake.md`


## 4) Why this matters

DeriveBSD’s strongest differentiator is not “we have more ideas.”
It’s that **complexity lives at the edges** and the center stays coherent.

This tiering discipline is how we keep that promise.


Last updated: 2026-06-18r616
