# Device authority posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

DeriveBSD already has the building blocks for treating device access as authority.
What this doc decides is narrower and more important for coherence:
**what is the default posture for raw device nodes, compiled `/dev` views, and portal/device-domain mediation in each product shape?**

This is intentionally **not** a full backend spec for devfs rulesets, device brokers, or portal transports.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0066-device-authority-posture-by-profile.md`
- device grants + devfs rulesets: `docs/278-device-grants-and-devfs-rulesets.md`
- devfs views as derived operations: `docs/323-devfs-views-plans-and-receipts.md`
- device isolation domains: `docs/204-device-isolation-domains.md`
- input authority / HID risk: `docs/207-input-authority-secure-attention-and-hid-risk.md`
- camera + audio capture portals: `docs/209-camera-and-audio-capture-portals.md`
- workstation boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- packet capture / raw packet authority boundary: `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

The archive already says device nodes are authority, `/dev` views should be compiled, and dangerous device classes should prefer mediation.
Without a profile-shaped default, those principles still drift in practice:

- fleet hosts accumulate ambient `bpf`, raw block, or USB authority as an operational convenience,
- workstation apps quietly inherit raw host device nodes instead of staying on portal or brokered streams,
- general-purpose systems become impractical if every legacy device consumer is forced into workstation-style ceremony,
- and factory/regulatory images claim sealed posture while still relying on ad-hoc live devfs expansion.

Device authority is too foundational to leave as implied local custom.
The archive needs a stable default for **when raw device nodes are ordinary, exceptional, or out of bounds**.

## Scope of this knob

`device_authority` covers the default handling of:

- compiled `/dev` views for host jails and service compartments
- raw host device-node exposure to interactive or legacy software
- when device domains, portals, or brokered streams are the default instead of raw nodes
- when runtime device-authority expansion belongs to maintenance or offline support workflows

It does **not** decide every backend detail of devfs rendering, guest transports, or exact device-class taxonomies.

## Product-shape defaults

| Profile | `device_authority` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `compiled-minimal-maintenance-leased` | Service compartments get compiled-minimal device views; raw block/packet/input/capture authority expands only through explicit leases or maintenance workflows with receipts. |
| B (`workstation`) | `portal-first-host-owned-trusted-ui-exceptions` | The trusted host owns raw sensitive devices; general interactive apps should use portals, mediated streams, or device-domain services by default, and dangerous raw-device exceptions must be trusted-UI-visible. |
| C (`general_os`) | `compiled-minimal-preferred-explicit-compatibility-fallback` | Compiled-minimal `/dev` views and mediated device lanes remain preferred, but explicit local compatibility fallback for raw device-node consumers stays viable. |
| D (`appliance_factory`) | `compiled-minimal-sealed-offline-maintenance` | Production images stay compiled-minimal and sealed; raw block/input/capture/debug node expansion belongs to offline or strongly approved maintenance/support workflows. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- device nodes are authority, not a filesystem implementation detail
- `/dev` views for host compartments should be compiled from intent + grants + host policy rather than hand-maintained folklore
- HID, camera, microphone, raw block, packet capture, and similar high-authority classes should not become ambient by accident
- attach/expand/revoke events should be receipted, diffable, and reviewable
- drift in effective device authority is an incident-grade surface, not a purely local debugging detail

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `compiled-minimal-maintenance-leased`

- Fleet services should not gain raw device authority just because someone edited a devfs ruleset during an incident.
- Device expansion belongs to named leases or maintenance, with receipts and later review.
- Least-authority claims become more credible when `/dev` is as explicit as networking or sysctls.

### B) Secure workstation (`workstation`)

Default: `portal-first-host-owned-trusted-ui-exceptions`

- The workstation host should own raw HID/camera/mic/block surfaces so the user can reason about trusted path and visible capture indicators.
- General interactive apps should ask for mediated device access, not wake up inside AppVMs with raw host `/dev` already present.
- Compatibility exceptions remain possible, but they belong in trusted-UI-visible lanes instead of ambient desktop folklore.

### C) General-purpose OS (`general_os`)

Default: `compiled-minimal-preferred-explicit-compatibility-fallback`

- General-purpose viability requires that some legacy or developer software can still use raw device nodes when explicitly chosen.
- The archive should keep compiled-minimal and portal/broker lanes preferred, but it should not pretend C stays viable if every audio/video/debug/storage workflow must be rearchitected first.
- The important move is keeping compatibility fallback explicit, local, and reviewable.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `compiled-minimal-sealed-offline-maintenance`

- Production and factory images should not depend on ambient debug or raw-device growth after deployment.
- Support or reprovisioning workflows may need stronger device authority, but those belong to offline or strongly approved maintenance lanes.
- A sealed device posture is part of being able to explain and audit the shipped appliance state.

## What this does **not** decide yet

This doc does **not** freeze:

- the exact `service-minimal` pseudo-device set
- the exact observed-node digest format
- the exact threshold for auto-quarantine versus human paging on drift
- the exact portal transport for every device class
- the exact guest `/dev` strategy for every microVM lane

Those remain implementation details or future RFC/ADR material.

## Why this is worth locking now

This decision collapses a recurring ambiguity without inventing a new subsystem:

- A gets compiled-minimal service posture with lease-shaped expansion,
- B explicitly rejects ambient raw host-device authority for ordinary apps,
- C keeps compatibility viable without silently redefining stricter profiles,
- D gets a real compiled-minimal sealed production baseline.

That is enough to guide future specs and coding while keeping the device broker, portals, and renderer details open.

## Design cue from current systems

A few ecosystem lessons are stable:

- FreeBSD `jail(8)` and `devfs(8)` make it clear that per-jail device exposure is part of whether isolation claims are real
- `devfs.rules(5)` is powerful, which means it is also a dangerous source of folklore unless views are compiled and receipted
- Qubes is right to treat USB/input and device attachment as security boundaries, not convenience plumbing
- workstation portal patterns are useful because they keep human-visible consent and raw device ownership in the trusted plane

DeriveBSD should steal those lessons while keeping the broker and transport replaceable.

Last updated: 2026-03-08r235
