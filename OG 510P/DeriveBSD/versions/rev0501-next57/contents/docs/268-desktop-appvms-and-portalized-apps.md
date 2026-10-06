# Desktop AppVMs and portalized apps (Qubes + Flatpak lessons)

DeriveBSD’s security posture is easiest to preserve if the host stays small and “boring”, and **interactive apps live in compartments**.
Qubes shows that AppVMs/disposables can be usable; Flatpak shows that portals enable desktop ergonomics under confinement.

This doc sketches a DeriveBSD-native stance that avoids “desktop sprawl” on the host. The core boundary is now accepted for profile B: see `adrs/ADR-0047-workstation-host-ui-and-appvm-boundary.md` and `docs/457-workstation-host-ui-and-appvm-boundary.md`.

## Stance

- The host is a **hypervisor-centric control plane** with minimal interactive surface.
- Desktop/interactive applications are delivered as derived **AppVM artifacts** (microVM-first).
- Host integration is via **portals**, with receipts and policy gates.

This keeps the host’s threat model close to “appliance OS”, while still enabling a daily-driver workflow.

## AppVM as an artifact target

Define an artifact target class:
- `appvm.bundle` = (base root + app payload + runtime contract)

Key properties:
- a pinned closure (Spec→Lock→Plan)
- a sandbox profile (jail/microVM)
- a declared portal surface (what it may ask for)
- a default persistence model

### Persistence modes (borrow Qubes mental model)

- **Template-based AppVM**: immutable base + per-app writable dataset
- **Disposable AppVM**: no persistence across runs (amnesic)
- **Profiled disposable**: disposable with a small, policy-defined “seed state” (fonts, locale, trusted certs)

Storage is where these modes either stay crisp or devolve into folklore.
DeriveBSD should standardize the **template/private/volatile** mapping for AppVMs (and how `/home` is sourced).

See: `docs/270-appvm-storage-private-volatile-and-home-areas.md`.

## Portals are the only host integration

AppVMs should not be “special”: they use the same portal system as other sandboxes.
At minimum:
- FileChooser/Documents portal (explicit file handles)
- Clipboard/drag&drop portal (explicit export events)
- ScreenCast/RemoteDesktop portals (high-risk; require strong consent UX)
- Print portal
- Notification portal

**Design requirement:** portal approval produces receipts, and the AppVM sees only preopened handles/streams.

## Policy lessons (Flatpak’s sharp edge)

Flatpak portals are powerful but ultimately depend on user approvals; a malicious app can prompt repeatedly.
DeriveBSD should add:
- per-portal rate limits and cooldowns
- “suspicious prompt” heuristics (e.g. repeated requests)
- policy-mandated defaults (deny-by-default for high-risk portals)
- audit-visible consent receipts and export receipts

## Pre-warmed disposables (latency ergonomics)

Qubes uses preloaded disposables to make “open safely” feel instant.
DeriveBSD can do similar:
- keep a paused/prefetched disposable base image
- fork/clone a disposable instance on demand
- tear down aggressively, and record usage as evidence

## Why this is groundfloor-worthy

If we postpone the desktop stance, the ecosystem will invent:
- inconsistent sandbox tools
- ad-hoc file sharing channels
- long-lived “pet VMs” with unclear authority

Baking in AppVM artifacts + portals early makes the safe path the easy path.

## References

- Qubes disposables (stateless VMs; usability/security model): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-disposables.html
- Qubes disposable implementation notes (preloaded disposables, mechanics): https://doc.qubes-os.org/en/latest/developer/services/disposablevm-implementation.html
- Qubes template implementation (private + volatile storage; read-only root): https://doc.qubes-os.org/en/latest/developer/system/template-implementation.html
- Qubes templates overview (centralized updates; per-VM private storage): https://doc.qubes-os.org/en/latest/user/templates/templates.html
- Flatpak sandbox permissions (default isolation + portal approach): https://docs.flatpak.org/en/latest/sandbox-permissions.html

Last updated: 2026-03-06r186
