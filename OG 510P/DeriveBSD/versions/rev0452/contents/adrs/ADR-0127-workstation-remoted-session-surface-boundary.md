# ADR-0127: Workstation remoted session-surface boundary

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0126-workstation-display-composition-and-gpu-boundary.md` already fixed the hardest desktop trust cut:
the host owns composition and trusted prompts, isolated apps cross that boundary through remoted GUI, and software-first guest rendering is an acceptable viability floor.

But one expensive ambiguity remained open inside that decision:

- does the baseline workstation lane require **seamless per-window remoting** into the host compositor,
- or is the first viable target a **domain-scoped remoted session surface** that the host can label and manage as one object?

Leaving that fuzzy would recreate design drift immediately:

- engineers would assume “desktop viability” means host-native per-window integration from day one,
- the transport / trust-indicator / clipboard / focus story would silently inherit the complexity of full GUI virtualization,
- and B would start depending on a security-critical GUI agent/daemon stack before the archive even proves the simpler host-owned display boundary.

For DeriveBSD on bhyve/FreeBSD, this matters because the documented default host posture is still serial-console-first, with framebuffer/VNC-style guest graphics as the ordinary bhyve graphical path rather than a built-in host-native seamless-window substrate.
We need a narrow implementation-guiding decision that keeps B viable now without foreclosing a better integrated future lane.

## Decision

For profile **B** (secure workstation), the baseline GUI crossing is now:

1. The host admits an AppVM into the trusted display plane as a **remoted session surface**: one labeled compartment-owned desktop/session/workspace surface at a time, not host-native seamless individual guest windows.
2. The host compositor treats that session surface as the primary review/control object for origin markers, focus policy, secure-attention overlays, remote-assistance visibility, and revoke/teardown.
3. A workstation may still feel app-like by preferring **small-role or single-app AppVMs**, but that ergonomics choice does not change the trust boundary: the crossing is still session-scoped.
4. Clipboard, open/save, URL, print, screencast, remote-control, camera, microphone, and similar crossings remain **portal/broker lanes** outside the session surface.
5. Any future seamless per-window host integration is a **later bounded adapter lane** that must prove it preserves trust cues, focus/input routing, clipboard/data-control boundaries, accessibility/IME behavior, and reviewable teardown semantics.

## Consequences

### What this locks now

- The archive no longer treats “remoted windows/surfaces” and “remoted whole-session surface” as equivalent baseline answers.
- B can target a simpler, more defensible GUI floor: the host only needs to trust and compose labeled compartment surfaces, not reconstruct arbitrary foreign window-manager semantics on day one.
- Remote assistance, support capture, and user explanation surfaces can reason about a compartment session as one review object.

### What stays open

This ADR does **not** decide:

- the exact transport/protocol used for the remoted session surface,
- the exact host shell/compositor UX (tabs, cards, workspaces, tiling, etc.),
- the exact audio forwarding stack,
- IME/accessibility details,
- or whether a future seamless-window lane is ever worth standardizing.

Those remain future RFC/ADR material.

## Why this is the smallest viable cut

Qubes shows that seamless cross-domain windows are possible, but its GUI virtualization is explicitly security-critical and depends on guest/host GUI agents, per-window protocol messages, window-manager hint handling, and custom shared-memory plumbing.
That is valuable research input, but it is not the cheapest trustworthy starting point for DeriveBSD.

So the archive now chooses the smaller contract:

- host-owned composition and trust markers,
- software-first guest rendering,
- and **session-surface-first remoting** as the baseline workstation target.

If later work proves that seamless per-window integration is worth its complexity, it can arrive as an explicit bounded lane instead of silently becoming the hidden minimum for B.

## Wiring

- display/GPU boundary: `docs/536-workstation-display-composition-and-gpu-boundary.md`
- session-surface boundary doc: `docs/537-workstation-remoted-session-surface-boundary.md`
- workstation host/UI boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`
- risk register: `docs/266-open-questions-and-risk-register.md`
