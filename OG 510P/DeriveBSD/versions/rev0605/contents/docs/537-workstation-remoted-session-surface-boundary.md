# Workstation remoted session-surface boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/536-workstation-display-composition-and-gpu-boundary.md` already decided that the trusted host owns composition and that isolated apps cross into the desktop through remoted GUI instead of ambient host display/GPU authority.
This doc makes the next small but expensive decision:
**the baseline GUI crossing for B is a domain-scoped remoted session surface, not seamless per-window host-native integration.**

See also:
- ADR: `adrs/ADR-0127-workstation-remoted-session-surface-boundary.md`
- host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`
- display/GPU boundary: `docs/536-workstation-display-composition-and-gpu-boundary.md`

## Why this needs a hard decision

The previous graphics boundary intentionally allowed two shapes:

- remoted guest windows/surfaces, or
- a remoted full-session surface.

That was useful to avoid premature lock-in, but it is too loose to guide implementation.
Those two options have very different complexity:

- seamless per-window remoting drags in foreign window-manager semantics, transient window handling, clipboard/data-control edges, IME/accessibility crossings, and harder trust-indicator work,
- while a session-surface baseline lets the trusted host reason about one labeled compartment surface at a time.

If DeriveBSD does not choose, the archive will quietly optimize for the harder path.

## Decision

For the ordinary workstation lane, the host should admit an AppVM into the trusted display plane as a **remoted session surface**.
That means:

- one compartment appears as one host-managed display object (workspace, card, tile, viewport, or similar)
- the host shows origin/trust cues at the session object boundary
- secure-attention overlays, focus policy, and teardown/revoke semantics remain host-owned
- clipboard, file selection, URL opens, printing, screencast, camera, microphone, and remote control stay separate broker/portal lanes
- the guest may still run multiple windows internally, but those are guest-local details until a future lane proves that exposing them individually is worth the security and implementation cost

This is the baseline viability floor for **B**.
It does **not** ban future better integration; it simply keeps the archive honest about what must exist first.

## What this buys

### 1) A smaller trusted crossing

The host compositor only has to trust and place a labeled compartment session surface.
It does not have to reconstruct arbitrary guest window lifecycles, override-redirect menus, clipboard-manager quirks, or every guest window-manager hint as part of the baseline contract.

### 2) A more practical bhyve-aligned floor

The documented bhyve host story is still serial-console-first, and the ordinary graphical lane the FreeBSD Handbook documents is framebuffer/VNC style guest presentation.
A session-surface-first floor fits that reality better than pretending host-native seamless windows are already the natural substrate.

### 3) A better explanation surface

Support, consent, and forensics can say:

- “this compartment/session is being shown”
- “this compartment/session is being remotely assisted”
- “this compartment/session was revoked”

That is easier to explain and export than a partially reconstructed pile of foreign windows.

## Ergonomics consequence: prefer small-role AppVMs

The archive should lean toward **small-role or single-app AppVMs** for daily workstation ergonomics.
That lets a session surface still feel reasonably app-like without redefining the trust boundary.

Examples:

- browser AppVM
- mail/chat AppVM
- office/document AppVM
- IDE/devtools AppVM
- disposable risky-open AppVM

This is not a new subsystem.
It is a packaging/defaulting consequence of choosing a session-scoped display crossing first.

## What is explicitly not baseline

The ordinary workstation lane does **not** require:

- seamless host-native per-window guest integration
- host-side reconstruction of guest menus/transient windows/popups as independent trusted objects
- a per-window GUI agent protocol as day-one minimum viability
- guest influence over host trust cues, secure-attention UI, or compositor-global clipboard/data-control surfaces

## Future bounded lane

A future seamless-window lane may still be valuable.
But it should only arrive after an explicit RFC/ADR answers:

- how window origin markers survive transient/override-redirect cases
- how input focus and secure attention stay host-owned
- how clipboard/data-control and drag/drop remain mediated
- how IME/accessibility cross the boundary without privileged backchannels
- how teardown/revoke/support capture remain reviewable

Until then, the archive should optimize for the session-surface baseline.

## Profile consequences

- **A** can reuse the same session-surface posture for occasional maintenance/recovery UI without inheriting workstation shell sprawl.
- **B** gets a viable secure-workstation floor that does not depend on perfect seamless GUI virtualization.
- **C** may later offer broader desktop adapters, but those are not the baseline definition of workstation viability.
- **D** can reuse the same pattern for bounded maintenance/inspection consoles when a human-facing session is unavoidable.

## Related docs

- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/536-workstation-display-composition-and-gpu-boundary.md`
- `docs/208-screencast-and-remote-desktop-portals.md`
- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/291-remote-assistance-sessions-as-evidence.md`

Last updated: 2026-03-17r266
