# Desktop viability checklist (profile B must remain real)

**Tier:** C (Optional lane)  
**Profiles:** B
**Pillars:** isolation, operability
**Patterns:** Registry→Diff→Gate  

DeriveBSD must keep “secure workstation” (profile **B**) viable even if v0 ships as a fleet host.
This checklist exists to prevent accidental design choices that make B impossible later.

This is **not** a desktop roadmap. It is a constraint list.

## Trusted UI boundary

- define a **trusted UI / secure attention** path (how the user knows “this prompt is real”)
- define what is in the trusted computing base for UI:
  - compositor? small “trusted shell”? minimal window manager?
- define how prompts are mediated when apps are isolated (AppVMs / microVMs)

## Portals / powerbox (mandatory for B)

Portal-mediated access for:

- file open/save
- clipboard
- URL handling
- notifications
- screenshots/recording
- printing
- device access (USB, cameras, microphones)
- secrets (credential prompts)

Rules:

- no ambient “read the whole home directory” by default
- portal decisions must be receipted and explainable (“why does app X have access?”)

## GUI transport across isolation boundaries

- Wayland/X11 strategy (and the security implications)
- display protocol boundary (host compositor vs guest compositor)
- GPU acceleration boundary (software fallback vs mediated GPU)
- input method boundary (HID, IME, key logging risk)

## Device mediation

B requires a coherent plan for:

- USB/HID pass-through (policy-gated, time-bounded leases)
- webcam/mic access (indicator lights, revocation UX)
- Bluetooth
- smart cards / FIDO keys
- printing/scanning

## “Daily ergonomics” integration points

- networking UX (VPNs, Wi‑Fi secrets) without leaking ambient authority
- password manager / secret store (brokered capabilities)
- updates/rollback UX that non-experts can understand
- backups and portable homes UX

## Forensics and support bundles (user-safe)

- support bundles must avoid leaking secrets
- user-controlled redaction + deterministic export
- “explain my system state” should work without privileged spelunking

## How to keep this viable now (even before desktop work)

When making core decisions, ensure we do not foreclose:

- portal services as capability-brokered ops
- per-app isolation boundaries that can still render UI safely
- a stable policy vocabulary for “user intent” approvals
