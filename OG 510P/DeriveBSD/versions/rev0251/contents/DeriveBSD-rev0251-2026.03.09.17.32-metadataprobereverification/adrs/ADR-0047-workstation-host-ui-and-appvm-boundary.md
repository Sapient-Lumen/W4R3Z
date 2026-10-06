# ADR-0047: Workstation host UI and AppVM execution boundary

- Status: Accepted
- Date: 2026-03-06

## Context

DeriveBSD wants profile **B** (secure workstation) to stay viable without weakening the host posture needed by profiles **A** and **D**.
The archive already contains strong desktop-oriented ideas:

- portal-mediated authority (`docs/179-portals-and-powerbox.md`)
- AppVM-first thinking (`docs/268-desktop-appvms-and-portalized-apps.md`)
- secure attention and host-owned input authority (`docs/207-input-authority-secure-attention-and-hid-risk.md`)
- desktop viability constraints (`docs/410-desktop-viability-checklist.md`)

But the current profile summary still says workstation runtime is `appvm-or-microvm`, which is too ambiguous.
That ambiguity risks a quiet slide toward “just run apps on the host,” which would:

- weaken the trusted host boundary,
- make B diverge from A/D for convenience,
- and turn portal/device mediation into optional folklore.

We need a small, durable decision that keeps B real **without** pretending to have solved the whole desktop stack.

## Decision

For profile **B** (workstation), DeriveBSD adopts this execution boundary:

1. The **host** is a **trusted UI + broker control plane**, not a general-purpose app host.
2. General interactive applications run as derived **AppVM artifacts** by default (microVM-first at the desktop app boundary).
3. Host↔app integration is mediated through **portals / brokers / leases** and remains receipted.
4. Raw HID/device passthrough is **not** the normal integration path for B; the host owns raw HID, focus, and secure-attention transitions.
5. Running general-purpose user apps directly on the host is **forbidden by default** in profile B. If ever needed, it must be treated as a narrow adapter/developer lane, not the workstation default.

## Consequences

### What is in-scope for the trusted host surface

The host may run a deliberately small set of trusted components such as:

- compositor / trusted shell / window-origin markers
- secure-attention and unlock / approval surfaces
- portal and broker daemons
- settings / update / recovery / support tooling
- device, network, and secret mediation components

### What is out-of-scope for the host by default

The host should not become the place where arbitrary browsers, editors, chat clients, document viewers, and similar daily-driver apps execute by default.
Those belong in AppVMs and use portals for access to files, clipboard, notifications, devices, screen sharing, and related resources.

### What this ADR intentionally does **not** decide yet

This ADR does **not** settle:

- the final GUI transport implementation,
- GPU acceleration strategy,
- audio/video backend details,
- or whether some trusted developer/admin tools may eventually get a bounded host-execution adapter lane.

Those remain future RFC/ADR territory.

## Why this is the smallest viable decision

This decision keeps the host threat model coherent across A/B/D while preserving B as a real product shape:

- A fleet host already wants a minimal control plane.
- A workstation still gets strong app isolation and ergonomic, portal-mediated sharing.
- Regulatory/appliance shapes keep a small trusted surface and don’t inherit “desktop sprawl” by accident.

The key move is not “ship the whole desktop now.”
It is: **do not let the workstation profile silently normalize host app execution.**

## Wiring

- Product profiles: `spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/412-product-profile-matrix.md`
- Workstation boundary doc: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- Prior art / related docs:
  - `docs/268-desktop-appvms-and-portalized-apps.md`
  - `docs/179-portals-and-powerbox.md`
  - `docs/207-input-authority-secure-attention-and-hid-risk.md`
  - `docs/410-desktop-viability-checklist.md`
