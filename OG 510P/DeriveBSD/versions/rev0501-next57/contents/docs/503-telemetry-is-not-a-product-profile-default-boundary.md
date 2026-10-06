# Telemetry is not a product-profile default boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Registry→Diff→Gate, Broker→Lease→Receipt  

DeriveBSD already has real observability/evidence posture surfaces.
This doc makes one smaller but expensive decision explicit:
**`telemetry` is not a separate A/B/C/D default key.**

See also:
- ADR: `adrs/ADR-0093-no-separate-telemetry-product-profile-key.md`
- profile vocabulary boundary: `docs/501-product-profile-default-vocabulary-boundary.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- export posture: `docs/466-export-boundary-posture-by-profile.md`
- observability as capability: `docs/192-observability-as-capability.md`

## Why this needs a hard decision

The archive already says useful things about telemetry-like behavior:
local evidence, support export, remote collectors, network egress, redaction, and live tracing.
But once `telemetry` appears as a product-profile default key, review gets fuzzy fast:

- does a proposed change belong in `telemetry` or `evidence`?
- if it leaves the machine, is that `telemetry` or `evidence_exports`?
- if it needs network reachability, is that `telemetry` or `network_egress`?

That ambiguity is exactly how profile artifacts turn into overlapping folklore.

## The accepted boundary

The archive now treats telemetry posture as the composition of existing surfaces:

- **`evidence`** answers what evidence/diagnostics are normally collected and retained.
- **`evidence_exports`** answers how evidence may be shared, exported, or handed to support.
- **`network_egress`** answers whether off-box delivery is brokered, explicit, or absent.
- richer tracing/export behavior stays in explicit observability or export lanes, not a new profile knob.

So the boundary is:

- telemetry remains a useful **word**,
- exporters and remote collectors remain useful **lanes**,
- but `telemetry` is **not** a first-class product-profile default key.

That same discipline applies to narrower evidence-class decisions. For example, DNS receipt detail/export posture is now fixed as a compiled consequence of `evidence` + `evidence_exports` + `network_egress`, not as another profile knob (`docs/504-dns-receipt-detail-and-export-posture-by-profile.md`).

## What still stays true by profile

### A) Secure fleet host

A can keep bounded always-on local evidence and policy-shaped export without inventing a special telemetry key.
Fleet operability still matters; the point is that the posture is already captured by evidence + export + egress.

### B) Secure workstation

B still rejects ambient support telemetry and hidden background uploads.
That promise belongs to trusted-UI-visible evidence/export posture, not a second overlapping default axis.

### C) General-purpose OS

C still allows explicit optional collectors/exporters as killable adapter lanes.
Local viability should not require a hidden vendor telemetry stack.

### D) Appliance factory / regulatory

D still forbids ambient live production diagnostic streaming by default.
That remains a strong product promise, but it lives in bundle-oriented evidence posture and forbidden-by-default lanes rather than a one-off `telemetry=minimal` knob.

## Review rule

When someone proposes a telemetry-related profile change, ask these in order:

1. Is the real change about **collection/retention**? Use `evidence`.
2. Is it about **sharing or support handoff**? Use `evidence_exports`.
3. Is it about **transport authority**? Use `network_egress`.
4. Is it richer than a posture string? It probably wants a dedicated lane/spec instead of a new profile key.

That rule keeps A/B/C/D comparable without flattening observability into hand-wavy prose.

## Why this is worth locking now

This is an entropy cut, not a subsystem expansion.
It removes one overlapping vocabulary key and forces future observability decisions onto the already-canonical surfaces.
That keeps the profile artifact small enough to stay implementable.

Last updated: 2026-03-08r233
