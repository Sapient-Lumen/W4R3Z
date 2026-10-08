# Research — specialist tools and shipping-lane reviews

Date: 2026-03-17

## Why this note exists

VHK's planner already distinguishes export surfaces from workload-oriented input
lanes. The remaining question is whether review-facing promotion artifacts
should render that distinction explicitly.

## Online lessons being applied

- Espanso's package/config model stays strongly text-surface oriented, with
  app-specific configurations and include/exclude rules rather than pretending
  every automation should be expressed as generic replay.
- xremap continues to frame itself as an app-specific remapper for X11 and
  Wayland built around `evdev`/`uinput`, which is a specialist low-latency lane
  rather than a generic text/package/export surface.
- The XDG RemoteDesktop and InputCapture portal interfaces remain session-based
  and permissioned, which keeps portal-backed input in a reviewed/conditional
  lane instead of a silent default shipping path.
- `ydotool` still documents `ydotoold` as mandatory because the persistent
  virtual device must stay alive long enough for the environment to recognize
  it, reinforcing that daemon-backed helpers are their own shipping lane with
  explicit host/service ownership.

## Product implication

Promotion artifacts should not stop at "export surface X exists." They should
also show which Linux-native lane actually owns shipping for that surface, what
host requirements come with that lane, and which alternates stay on deck.
Otherwise project-level review drifts back toward generic automation folklore.

## Concrete repo consequence

`gen-promotion-pack` should render `promotion_input_lane_plan` directly in both
JSON and Markdown so the same artifact used for waves/gates/backlog/evidence
also carries shipping-lane ownership.
