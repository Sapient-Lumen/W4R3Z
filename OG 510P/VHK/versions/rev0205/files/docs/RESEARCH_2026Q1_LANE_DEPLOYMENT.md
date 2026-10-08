# Research 2026 Q1 — lane-native deployment lessons

Product lesson:
- release lanes are not enough on Linux; each lane still needs a concrete
  install/autostart shape

Current ecosystem lessons folded into VHK design:
- freedesktop autostart remains a real cross-desktop lane for desktop-entry
  startup, so portal/session-first routes still need a `.desktop`/autostart
  story
- systemd user services remain a practical lifecycle surface for helper daemons
  and text services
- portal shortcuts are session objects, so they should not be documented as if
  they were permanent invisible hooks
- Espanso's Linux docs keep reinforcing that text-surface tools need package +
  service registration/start flow, not just exported config files

VHK consequence:
- every flagship lane should declare not only the trigger/runtime strategy, but
  also the shipping/deploy style and the artifact subset that matches it
