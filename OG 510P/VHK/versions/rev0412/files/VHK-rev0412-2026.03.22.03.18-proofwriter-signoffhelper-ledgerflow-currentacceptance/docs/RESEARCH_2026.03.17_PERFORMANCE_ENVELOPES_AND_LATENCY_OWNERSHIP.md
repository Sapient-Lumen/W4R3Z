# Research notes (2026-03-17): performance envelopes and latency ownership

## Why add a promotion-side performance envelope?

Linux automation tools keep teaching the same lesson: the fastest path depends on *which lane owns the work*.

- Text expansion tools win by staying warm and package-oriented instead of replaying every character through a heavyweight general runner.
- Remappers win by owning a very thin edge path near evdev/uinput or compositor-native binding surfaces.
- Helper-backed replay wins when daemon/device startup is amortized rather than paid on every action.
- Portal/session paths can be perfectly valid, but their first-use latency is shaped by consent, activation, and compositor state rather than raw helper speed.
- Watcher/services win when event delivery stays resident and event-driven instead of degrading into poll-heavy fallback loops.

That is why VHK benefits from a planner surface that says *what performance shape each promoted surface should preserve*, not just who owns shipping and proof.

## What current tools reinforced

### keyd keeps the edge path explicit

keyd still describes itself as a system-wide daemon using kernel-level primitives (`evdev`, `uinput`) and explicitly lists speed as a goal, including a hand-tuned input loop that takes `<<1ms`. It also centers `keyd monitor`, `keyd reload`, and `journalctl -eu keyd` in the operator loop. The lesson for VHK is that remapper exports should explicitly protect a low-latency edge path rather than being reviewed like ordinary helper playback.

### xremap keeps remapping thin and resident

xremap still presents itself as fast, written in Rust, and built around `evdev`/`uinput` while supporting X11 and Wayland. It also keeps app/device specificity and `--watch` close to the remapper lane. The lesson is similar: remapper promotion is not just “another backend,” it is a latency envelope with a thin resident edge path.

### wtype shows a narrower Wayland fast path

wtype still documents itself as “xdotool type for wayland” and notes that modifiers are released when the process terminates because the compositor destroys the associated virtual keyboard object. That reinforces VHK’s existing design split: a narrow text fast path is useful, but it is not the same product as a daemon-backed repeated-playback lane.

### Espanso still models text as a service/package lane

Espanso’s CLI still exposes `status`, `restart`, `service`, `path`, and `match` surfaces. That supports VHK treating text-package promotion as a throughput-first surface whose performance comes from warm service/package semantics and explicit config/runtime ownership, not from pretending that per-character typing is always good enough.

### InputCapture and RemoteDesktop still make async/consent visible

The XDG portals still document session/activation boundaries and permission-gated keyboard/pointer notification methods. The lesson is that portal-backed helper routes should have an explicit consent-bound performance envelope rather than being mislabeled as generic “fast input.”

## Product lesson for VHK

A Linux-native AHK successor should not just say “this export ships.” It should also say which latency/throughput envelope that export is supposed to preserve:

- throughput-first text lane
- low-latency remap edge lane
- warm daemon-backed helper lane
- consent-bound portal/session lane
- resident event pipeline lane
- launcher wake-path lane

That is the reasoning behind `promotion_performance_plan`.
