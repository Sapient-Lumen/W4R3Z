# ADR-0048: Removable media and USB posture by profile

- Status: Accepted
- Date: 2026-03-06

## Context

DeriveBSD already has strong pieces for device safety:

- device isolation domains (`docs/204-device-isolation-domains.md`)
- device grants + devfs views (`docs/278-device-grants-and-devfs-rulesets.md`)
- USB quarantine and sanitize-first imports (`docs/279-usb-quarantine-and-removable-media-workflow.md`)
- workstation host-owned HID/input authority (`adrs/ADR-0047-workstation-host-ui-and-appvm-boundary.md`, `docs/207-input-authority-secure-attention-and-hid-risk.md`)
- origin labels, quarantine metadata, and air-gap mirror kits (`docs/280-origin-labels-and-quarantine-attributes.md`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`)

But open question 12 still leaves too much room for convenience drift.
If “USB/removable media” stays a lesson instead of a profile artifact, the archive can quietly regress toward:

- automount into the most trusted plane,
- ad-hoc local attach workflows with no receipts,
- workstation/device-domain exceptions justified as “temporary”,
- and air-gap/media imports that bypass quarantine→promote discipline.

We need a **small, durable default** that works across A–D without pretending to have solved every hardware edge case.

## Decision

DeriveBSD adopts this baseline removable-media / USB posture:

1. **No profile automounts removable media into its most trusted plane by default.**
2. **All profiles are quarantine-first for removable media.** The default workflow is discover → classify → explicit attach/mount → sanitize/import or verified-kit ingest, with receipts.
3. **USB controller/device-domain use is profile-specific but explicit:**
   - **B (workstation):** `device-domain-required-when-supported`
   - **D (appliance_factory):** `device-domain-or-ingest-station`
   - **A (fleet_host):** `prefer-device-domain-no-host-automount`
   - **C (general_os):** `prefer-device-domain-fallback-to-local-policy`
4. **Raw HID remains special-danger.** This ADR does not weaken `ADR-0047`: workstation input stays host-owned/brokered, and raw keyboard/mouse passthrough is not normal plumbing.
5. These defaults become part of the **product profile artifact** (`spec/examples/product.profiles.json`) and are guarded by hygiene checks.

## Consequences

### What becomes true now

- “No automount into the trusted plane” is a checkable product-shape invariant, not a suggestion.
- Profile **B** keeps a coherent workstation story: trusted host UI, AppVM apps, and removable-media/device access routed through quarantine/device domains and brokers.
- Profile **D** keeps regulatory/offline ingest coherent: removable media enters through a quarantined path or dedicated ingest station, then quarantine→promote.
- Profile **C** remains viable on imperfect consumer hardware, but its fallback is still **policy-shaped**, not ambient convenience.

### What this ADR intentionally does **not** decide yet

This ADR does **not** settle:

- the exact BSD-native local USB authorization helper,
- controller-isolation detection and hardware qualification rules,
- integrated Bluetooth/FIDO/smart-card handling,
- or the final UX for local fallback prompts and remembered approvals.

Those remain future RFC/ADR work.

## Why this is the smallest useful decision

This ADR does not invent a new subsystem.
It simply turns existing archive lessons into a **profile-true baseline**:

- quarantine first,
- no trusted-plane automount,
- device domains where they are realistically supportable,
- explicit fallback policy where they are not.

That is enough to keep all four product shapes coherent while leaving implementation details open.

## Wiring

- Product profiles: `spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/412-product-profile-matrix.md`
- Focused wiring doc: `docs/458-removable-media-and-usb-posture-by-profile.md`
- Open questions / risk register: `docs/266-open-questions-and-risk-register.md`
- Related docs:
  - `docs/204-device-isolation-domains.md`
  - `docs/207-input-authority-secure-attention-and-hid-risk.md`
  - `docs/278-device-grants-and-devfs-rulesets.md`
  - `docs/279-usb-quarantine-and-removable-media-workflow.md`
