# ADR-0066: Device authority posture by profile

Date: 2026-03-06
Status: Accepted

## Context

DeriveBSD already treats device nodes as authority and already has the raw ingredients for a coherent `/dev` story:
`docs/278-device-grants-and-devfs-rulesets.md`, `docs/323-devfs-views-plans-and-receipts.md`,
`docs/204-device-isolation-domains.md`, `docs/207-input-authority-secure-attention-and-hid-risk.md`,
and `docs/209-camera-and-audio-capture-portals.md` define device grants, compiled devfs views, device domains,
HID danger classes, and portal-mediated AV capture.

What the archive still lacked was a **product-default boundary** for when raw device nodes are ordinary,
when device access should be portal-first, and when `/dev` expansion is only a maintenance exception.
Without that boundary, the same device vocabulary drifts into contradictory defaults:

- fleet services quietly accumulate ambient `bpf`, raw block, or USB authority because an operator "needed it once",
- workstation apps inherit raw host device nodes instead of staying on portal/mediated streams,
- general-purpose installs lose compatibility viability if every device consumer is forced through workstation/fleet ceremony,
- and factory/regulatory images claim sealed posture while still depending on ad-hoc live devfs expansion.

## Decision

DeriveBSD will treat **device authority posture** as a first-class, profile-shaped default captured in
`spec/examples/product.profiles.json` under `device_authority` and guarded by `tools/check_product_profiles.py`.

This posture covers the default handling of:

- compiled `/dev` views for host jails and service compartments,
- raw host device-node exposure to interactive or legacy workloads,
- when portal/broker/device-domain lanes are the default instead of raw device nodes,
- and when runtime expansion of device authority belongs to maintenance or offline support workflows.

The default values are:

- **A / `fleet_host`**: `compiled-minimal-maintenance-leased`
- **B / `workstation`**: `portal-first-host-owned-trusted-ui-exceptions`
- **C / `general_os`**: `compiled-minimal-preferred-explicit-compatibility-fallback`
- **D / `appliance_factory`**: `compiled-minimal-sealed-offline-maintenance`

## Meaning by profile

### A) Secure fleet host (`fleet_host`)

- Ordinary service compartments get compiled-minimal device views.
- Raw block, packet-capture, USB, HID, and similar high-authority nodes are not ambient service authority.
- Device authority may expand through explicit leases or maintenance workflows, with receipts.

### B) Secure workstation (`workstation`)

- The trusted host owns raw HID, camera, microphone, and similar sensitive device surfaces.
- General interactive apps should consume portals, mediated streams, or device-domain services rather than raw host `/dev` nodes by default.
- Dangerous exceptions belong in trusted-UI-visible admin or maintenance lanes, not hidden compatibility folklore.

### C) General-purpose OS (`general_os`)

- Compiled-minimal `/dev` views and mediated device lanes remain the preferred and explainable default.
- Explicit local compatibility fallback remains viable for software that truly expects raw device nodes.
- The archive keeps that fallback explicit so C stays practical without silently redefining A/B/D posture.

### D) Appliance factory / regulatory (`appliance_factory`)

- Production posture is compiled-minimal and sealed by default.
- Raw block/input/capture/debug node expansion belongs to offline or strongly approved maintenance/support workflows.
- Production images should not depend on ambient devfs growth or ad-hoc live debugging surfaces.

## Consequences

### Positive

- The archive now has a coherent answer to "when are raw device nodes normal?" across A–D.
- Workstation posture explicitly resists ambient host-device authority leakage into AppVM-style workloads.
- Fleet/factory claims about least authority become more credible because `/dev` is now product-shaped, not just implementation advice.

### Negative / trade-offs

- This adds one more stable product-profile knob that must remain small and guardrailed.
- Some implementation details remain open: exact `service-minimal` pseudo-dev set, exact portal/device-domain thresholds, and exact drift/auto-quarantine policy.
- General-purpose compatibility remains a deliberate compromise: it preserves viability but leaves more local-footgun room than A/B/D.

## Non-goals

This ADR does **not** decide:

- the exact canonicalization algorithm for observed node digests,
- the exact `service-minimal` node allowlist contents,
- the exact guest `/dev` strategy for every microVM transport,
- or the exact UX for all workstation device prompts.

Those remain implementation work or future RFC/ADR material.

## Why this shape

The coherence win is not "portals everywhere" or "raw `/dev` everywhere."
It is deciding that:

- A is compiled-minimal with lease-shaped expansion,
- B is portal-first with host-owned raw devices,
- C preserves an explicit compatibility fallback,
- D is compiled-minimal and sealed in production.

That is enough to guide future specs and coding without prematurely freezing the device broker or portal backends.
