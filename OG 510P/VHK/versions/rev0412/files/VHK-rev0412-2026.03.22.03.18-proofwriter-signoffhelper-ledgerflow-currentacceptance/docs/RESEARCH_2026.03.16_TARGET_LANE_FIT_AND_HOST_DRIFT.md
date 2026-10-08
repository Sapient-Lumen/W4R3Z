# Research — target-lane fit and host drift

## Why this research note exists

VHK already had two useful but separate truths:

- **observed host truth**: what helpers, portals, and services the current host
  actually has
- **release lanes / target profiles**: what kind of Linux desktop posture the
  project intends to ship against

The missing piece was an explicit comparison between them. That comparison is
important on Linux because a host can be perfectly healthy for itself while
still drifting from the desktop/session lane a project wants to market as its
flagship experience.

## What we learned from others

### 1) Portals are frontend/backend contracts, not a single support bit

Upstream `xdg-desktop-portal` documentation keeps the split explicit: the
frontend service exposes portal APIs on D-Bus, while backend implementations
provide desktop- and host-specific behavior and are selected through config such
as `portals.conf`. Backend services are D-Bus activatable, so configured,
installed, and live truth can diverge on a real machine.

Implication for VHK: a useful Linux-native review surface cannot stop at
"portal present". It should preserve at least configured routing, installed
backend manifests, and live interfaces — and then compare that stack with the
intended target lane.

### 2) Adjacent Linux automation tools still keep boundaries explicit

AutoKey still positions itself as Linux/X11 automation rather than pretending to
be one universal desktop backend. Espanso likewise keeps configuration scope and
precedence explicit: only one configuration is active at a time, and app
filters define that active context.

Implication for VHK: be ambitious, but keep truth boundaries visible. A host
readiness summary and a target-lane story should not be merged into one vague
"Linux support" sentence.

### 3) wlroots and compositor-specific portal stories are still plural

Current portal reality remains uneven. Luminous is explicitly positioning itself
as an alternative backend for wlroots compositors, while other compositor- or
wlroots-adjacent stacks still have open issues around RemoteDesktop/InputCapture
class support.

Implication for VHK: target-fit should not assume one universal Wayland lane. It
should stay profile-driven (GNOME, KDE, wlroots, X11 fallback) and explain
drift/mismatch in human terms.

## Product rule for VHK

Later-stage artifacts should keep **both** of these answers visible:

1. what the current host can actually do
2. how that host compares with the declared flagship lane

That leads to a small contract instead of a giant matrix: `target_fit_contract`.

## Contract shape

A useful first-pass target-fit contract should stay compact and explainable. It
should compare at least:

- desktop family
- backend posture
- deploy style
- trigger-route choice
- requirement-state drift

It should produce simple fit states such as:

- `aligned`
- `drifted`
- `degraded`
- `outside-profile`

Those states are easier to defend than one fake numeric support score.

## Why this is creative in the right way

This is not just more packaging work. It makes VHK more Linux-native by letting
release/stage/rehearsal/support artifacts say:

- "this host is healthy for its own session"
- "but it drifts from the flagship lane because the desktop family, portal
  posture, or trigger route differs"

That is much closer to the real ergonomics of Linux automation than pretending
there is one global support truth.

## Next follow-through

The same contract should eventually feed:

- planner promotion gates
- claim/audit packs
- optional explicit multi-profile comparisons

That would let VHK express a careful statement like: "supported on this lane,
review on that lane, and outside profile on a third" without becoming vague or
overconfident.

## References

- XDG Desktop Portal docs: https://flatpak.github.io/xdg-desktop-portal/docs/
- portals.conf docs: https://flatpak.github.io/xdg-desktop-portal/docs/portals.conf.html
- system integration docs: https://flatpak.github.io/xdg-desktop-portal/docs/system-integration.html
- AutoKey intro: https://autokey.github.io/intro.html
- Espanso basics: https://espanso.org/docs/configuration/basics/
- Espanso app-specific configs: https://espanso.org/docs/configuration/app-specific-configurations/
- Luminous portal README: https://github.com/waycrate/xdg-desktop-portal-luminous
- Hyprland portal RemoteDesktop issue: https://github.com/hyprwm/xdg-desktop-portal-hyprland/issues/252
