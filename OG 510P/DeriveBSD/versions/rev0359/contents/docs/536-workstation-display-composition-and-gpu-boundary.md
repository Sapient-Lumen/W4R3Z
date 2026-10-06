# Workstation display composition and GPU boundary

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

DeriveBSD already decided that profile **B** keeps the host as the trusted UI / broker control plane and keeps ordinary apps inside AppVMs by default.
The unresolved question was whether graphics would quietly punch through that boundary.

This doc makes a conservative but practical decision:
**the trusted host owns composition and trusted-path UI, while isolated apps render in their own compartment and cross into the desktop through remoted GUI rather than ambient host display/GPU authority.**

See also: `adrs/ADR-0126-workstation-display-composition-and-gpu-boundary.md`.

## Why this needs a hard decision

Desktop designs often fail at exactly this seam:

- ambient X11/display-server access sneaks back in because “GUI apps need it,”
- direct raw DRM/render-node access turns graphics into a device-authority bypass,
- or the whole workstation plan blocks on perfect guest 3D before a defensible baseline exists.

DeriveBSD should reject all three failure modes.
B needs a **viable floor** that preserves the host trust boundary even when acceleration is incomplete.

## Decision

For the baseline workstation lane:

- the **host** owns composition, secure-attention indicators, focus policy, trusted prompts, and window-origin markers
- AppVMs cross into that host-controlled display plane through **remoted GUI**, with `docs/537-workstation-remoted-session-surface-boundary.md` now fixing the baseline as **session-surface-first**
- the required floor is **software-first guest rendering**: software-rendered or simple 2D guest output is acceptable baseline behavior
- ordinary AppVMs do **not** get ambient host X11 display access, raw DRM/render nodes, or direct PCI GPU passthrough by default
- any accelerated path is a **future bounded adapter lane**, not the default definition of B viability

This is a boundary decision, not a claim that all graphics/backend details are already implemented.

## What counts as the trusted display plane

The trusted host display plane may own a deliberately small set of responsibilities:

- compositor / trusted shell
- secure-attention and unlock / approval surfaces
- window-origin markers and trust indicators
- focus policy and prompt routing
- portal and broker UI surfaces
- review/maintenance/support UIs that are part of the host control plane

That is the smallest set that keeps “this prompt is real” and “which domain owns this window?” answerable.

## What isolated apps are allowed to see

Ordinary AppVMs should see:

- a guest-local display stack suitable for the app workload
- remoted presentation channels into the host-controlled display plane
- brokered clipboard / DND / screencast / printing / open-save / URL flows through host-owned portals

Ordinary AppVMs should **not** assume:

- ambient access to a shared host X server
- ambient access to host Wayland compositor internals
- raw host render nodes or full GPU management surfaces
- direct influence over trusted-path UI elements, origin markers, or secure-attention affordances

## Wayland/X11 consequence

DeriveBSD should treat host display protocols as part of the trusted boundary, not as ambient compatibility plumbing.
That means:

- host-side X11 sharing is not the baseline workstation answer
- guest-local X11 compatibility remains acceptable inside the guest/AppVM if the exported result still crosses into the host through the remoted GUI boundary
- host-side composition stays responsible for trust cues and for keeping privileged clipboard/data-control surfaces out of ordinary app authority

In other words: **legacy GUI compatibility may exist inside the compartment, but the host display boundary stays owned by the trusted plane.**

## Why software-first is the right floor

Software-first guest rendering is a deliberate choice, not an accident.
It buys three things:

1. **Implementability:** B can become real before the archive solves every GPU-virtualization edge case.
2. **Coherence:** graphics do not become the excuse for ambient host authority after other boundaries were tightened.
3. **Honesty:** a secure workstation can be “usable with a conservative graphics floor” before it is “fast for every workload.”

If acceleration later proves worth the complexity, it must justify itself as an adapter lane rather than silently rewriting the trusted-path story.

## Accelerated graphics remains a future adapter lane

A future accelerated lane may still be worthwhile.
But it must arrive with stricter questions answered up front:

- does it preserve host-owned trust indicators and secure-attention surfaces?
- does it avoid ambient host DRM/render-node authority in ordinary AppVMs?
- can it be killed or disabled without breaking the baseline workstation story?
- is it still explainable in support/recovery bundles and review surfaces?

Until those answers exist, acceleration stays optional.

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** remains mostly headless or console-shaped; if a local UI exists, the same host-owned composition rule keeps the control plane small.
- **B / secure workstation:** gets a coherent baseline now — remoted GUI with software/2D floor, not host-side ambient graphics authority.
- **C / general-purpose OS:** may later offer explicit compatibility lanes (including broader host graphics assumptions), but those do not redefine B.
- **D / appliance factory / regulatory:** does not need a general desktop baseline, but maintenance HMIs still benefit from a host-owned trusted display plane instead of ad-hoc app privilege.

## What remains intentionally open

This doc does **not** settle:

- the exact remoting transport or damage-tracking protocol
- the exact audio/video forwarding stack
- IME, accessibility, and multi-monitor details
- remote-session composition details
- whether a future mediated-GPU or passthrough lane is ever justified

Those are future implementation/RFC topics.

## Design cue from current systems

A few lessons are stable even before we pick exact backends:

- Qubes is right that window origin markers and host-owned GUI mediation are part of the trust boundary, not cosmetic UX
- Wayland’s privileged clipboard/data-control surfaces are a reminder that compositor-side power should stay in the trusted plane
- current FreeBSD virtualization/graphics support is good enough to justify a conservative 2D/software floor, but not a reason to make raw guest GPU authority the baseline workstation contract
- modern virgl/venus-style acceleration exists in the ecosystem, which is exactly why DeriveBSD should keep acceleration as an explicit optional lane rather than pretending it is free

DeriveBSD should steal the architectural lesson while keeping the transport/backend replaceable.

## Related docs

- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/476-device-authority-posture-by-profile.md`
- `docs/179-portals-and-powerbox.md`
- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/207-input-authority-secure-attention-and-hid-risk.md`
- `docs/268-desktop-appvms-and-portalized-apps.md`

Last updated: 2026-03-17r266
