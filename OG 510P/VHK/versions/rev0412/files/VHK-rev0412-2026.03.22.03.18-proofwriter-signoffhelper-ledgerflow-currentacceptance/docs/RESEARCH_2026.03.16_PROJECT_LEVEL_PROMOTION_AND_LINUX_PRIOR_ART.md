# Research notes: project-level promotion planning and Linux prior-art lessons

_Date:_ 2026-03-16

## Why this research pass

VHK had become good at saying which lane an individual macro resembled, but it
was still weaker at saying what the **project as a whole** should promote into
Linux-native surfaces next. The missing layer was an aggregate planning surface:
not only "macro X looks text-tier", but also "this repo now wants a text package
promotion lane plus one remapper lane and one helper dossier lane".

## Current ecosystem lessons worth carrying forward

### 1) Text automation is its own lane

Espanso continues to reinforce the idea that text automation wants application-
specific configuration, inheritance, and include/exclude controls, not just raw
key replay.

Design lesson for VHK: a snippet-heavy project should be able to graduate toward
package-oriented text delivery instead of pretending the full runner is always
the best first surface.

### 2) Remapping is its own lane

keyd continues to present itself as a system-wide daemon built on kernel input
primitives (`evdev`, `uinput`), and xremap continues to frame itself as an
app-aware remapper for both X11 and Wayland.

Design lesson for VHK: low-latency transforms, tap-hold behavior, and app-aware
remaps should be treated as first-class promotion targets instead of a side
effect of general runner macros.

### 3) X11 remains the clearest "AHK-like" replay path

AHK_X11 still very explicitly presents itself as an X11-based AutoHotkey-for-
Linux effort, and xdotool still documents its X11/XTEST foundation.

Design lesson for VHK: when a project wants classic AHK-style direct replay, the
most honest strong lane is still X11/i3-style targets, not a hand-wavy claim of
identical Wayland behavior.

### 4) Wayland trigger lanes are real, but session-owned

The GlobalShortcuts portal is session-based and backend-routed, InputCapture is
compositor-controlled, `portals.conf` still decides backend selection, and
libportal / xdg-desktop-portal are still seeing fixes and support work in these
areas. Kando's Hyprland install flow also shows a practical desktop reality: on
some Wayland targets, the app ends up registering a shortcut id and the desktop
or compositor owns the actual bind.

Design lesson for VHK: route ownership should stay explicit all the way up to
project planning. A project that leans on helper-sensitive or desktop-owned
routes should say so in its plan, not bury that complexity in one macro note.

## Repo change justified by those lessons

This pass added two new planner aggregates:

- `route_portfolio`
- `export_promotion_plan`

These are deliberately simple, but they close an important product-planning gap:

- `macro_route_profiles` answers: **who owns this macro?**
- `route_portfolio` answers: **which lanes dominate the project?**
- `macro_export_candidates` answers: **what could this macro promote into?**
- `export_promotion_plan` answers: **what Linux-native promotion work should the repo stage next?**

## Next implementation opportunities

1. Let `scaffold-project` consume `export_promotion_plan` and generate starter
   stage trees or checklists for the promoted surfaces.
2. Let release/setup packs mark one promotion surface as the current reference
   lane and the others as fallback or future lanes.
3. Turn project-level promotion rows into concrete bundle/export manifests so the
   planner can move from advisory status to executable status.
