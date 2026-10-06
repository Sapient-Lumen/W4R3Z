# ADR-0126: Workstation display composition and GPU boundary

Date: 2026-03-17
Status: Accepted

## Context

DeriveBSD already decided that profile **B** keeps the host as the trusted UI / broker control plane and runs general interactive apps in AppVMs by default (`adrs/ADR-0047-workstation-host-ui-and-appvm-boundary.md`).
The archive also already decided that raw device authority on B stays portal-first and trusted-host-owned instead of ambient `/dev` folklore (`adrs/ADR-0066-device-authority-posture-by-profile.md`).

What was still missing was the hardest desktop-shaped boundary that sits between those two decisions:

- does an isolated app join a shared host display server,
- does B require guest GPU acceleration to count as viable,
- or does the host own composition while guests export remoted windows/surfaces?

Leaving that open for too long would quietly force the archive into one of two bad outcomes:

- B blocks on “perfect GPU virtualization” before the workstation story can become implementable, or
- B drifts back to ambient host X11/DRM/render-node authority because “graphics are special.”

We need a small, implementation-guiding decision that keeps B viable **without** forcing A/D to inherit desktop sprawl and **without** pretending the exact transport/backend stack is already solved.

## Decision

For profile **B** (secure workstation), DeriveBSD adopts this display boundary:

1. The **trusted host owns composition**: compositor, secure-attention indicators, window-origin markers, focus policy, and trusted prompts stay on the host side.
2. General interactive apps in AppVMs export **remoted windows/surfaces** (or, where needed, a remoted whole-session surface) into the host-controlled compositor instead of joining a shared host display server.
3. The required viability floor is **software-first guest rendering**: software-rendered or 2D guest output is acceptable for the baseline workstation lane.
4. **Raw host display/GPU authority is not baseline workstation plumbing**: ordinary AppVMs do not get raw host X11 access, raw DRM/render nodes, or direct PCI GPU passthrough by default.
5. Any future accelerated path (mediated GPU, GPU device domain, virtio/virgl-style acceleration, direct passthrough for a bounded class) is an **explicit adapter/RFC lane**, not an assumed requirement for B viability.

## Consequences

### What this locks now

- B no longer depends on a day-0 answer for high-performance guest GPU acceleration.
- The trusted path stays coherent: window origin, secure prompts, and focus policy remain host-owned.
- Graphics stop being a loophole that reintroduces ambient host authority after the archive already rejected it for files, devices, and networking.

### What stays open

This ADR does **not** decide:

- the exact remoting protocol or transport,
- the exact host compositor implementation,
- the exact audio/video forwarding stack,
- IME/accessibility mechanics,
- or whether a future bounded accelerated lane is worth shipping.

Those remain future RFC/ADR material.

## Why this is the smallest viable cut

This decision is intentionally conservative.
It chooses a baseline that DeriveBSD can explain and implement incrementally:

- start from host-owned composition + remoted guest surfaces,
- accept software/2D rendering as the required floor,
- keep acceleration optional instead of letting it redefine the trusted boundary.

That keeps B honest without forcing A/D to inherit a giant graphics TCB, and it lets C keep broader compatibility as an explicit adapter lane rather than as workstation baseline leakage.

## Wiring

- Workstation boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- Desktop viability checklist: `docs/410-desktop-viability-checklist.md`
- Device authority posture: `docs/476-device-authority-posture-by-profile.md`
- Display/GPU boundary doc: `docs/536-workstation-display-composition-and-gpu-boundary.md`
- Risk register: `docs/266-open-questions-and-risk-register.md`
