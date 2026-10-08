# Plan (2026 Q1): Linux-native runtime strategy for VHK

This is a product/engineering plan for pushing VHK closer to the original ambition: **AHK-class usefulness on Linux**, while staying honest about the fact that Linux is a capability matrix, not one uniform desktop.

## 1) Product position

VHK should not try to be a line-by-line AutoHotkey clone. The stronger goal is:

- filesystem-friendly projects
- Pulover-style visible step composition and cleanup
- Linux-native integration with window managers, launchers, daemons, portals, and compositor APIs
- a headless runtime that can be embedded into many trigger surfaces

## 2) Runtime principles

### 2.1 Separate authoring from dispatch latency

The authoring/runtime CLI can be heavy. Low-latency triggering should continue to move toward:

- WM bindings / hotkey daemons / portal shortcuts
- `vhk-emit`-style lightweight emitters
- long-lived watcher processes (`busd`, clipboard/window watchers)

### 2.2 Treat Linux as layered authority, not one backend

Different jobs belong to different layers:

- compositor / WM: focus, workspaces, window events, native binds
- portal stack: permissioned capture / shortcuts / remote-control surfaces
- uinput/evdev helpers: broad injection when permitted
- X11 helpers: best legacy path where available
- VHK engine: sequencing, variables, diagnostics, packaging, selector logic

### 2.3 Prefer event-driven state when the platform can provide it

Polling vision remains essential, but it is expensive and brittle. Prefer, in order:

1. compositor/WM events
2. clipboard/filesystem/bus/process events
3. accessibility or structured selectors
4. vision polling

## 3) Near-term engineering priorities

### A) Recorder -> cleanup -> report loop

Keep tightening the flow from raw recording to maintainable macros:

- recorder smoothing and semantic collapse
- `optimize` / `optimize-project`
- `report` / `trace` summaries tied to real runs
- planner-side performance shape analysis so capture/OCR/polling costs are visible before a project is bound directly to hotkeys
- future Studio surface that reuses the same summarized data

### B) Capability-aware authoring

The capability matrix already reaches doctor/validate/lint. Extend that same language into:

- init templates
- scaffold flows
- launcher/install export guidance
- future Studio step editors

### C) Selector-first robustness

The Linux-native portability story improves when macros can move up the stack:

- named regions and needle metadata for vision
- better window/app scoping
- future accessibility selectors where practical

### D) Text-throughput lane

VHK should treat text automation as a performance surface, not just a convenience
step type. Long literal snippets and Tab/Enter-rich forms need an explicit lane:

- typed when per-character semantics matter
- clipboard when throughput matters more
- hybrid segmented when field separators must stay visible

This should remain planner-visible, lint-visible, optimizer-visible, and later
Studio-visible.

### E) Wayland helper spike

Do not bury complex portal/libei/session logic directly in the core Python engine first. Prefer a small helper spike/prototype that can fail fast and keep the main runtime simpler.

## 4) Explicit non-goals for the next revision window

- Do not promise one universal Wayland backend that works everywhere.
- Do not absorb full remapper/key-interceptor scope that belongs in keyd/kanata/kmonad/xremap-class tools.
- Do not hide platform caveats behind vague marketing terms like "Wayland supported".

## 5) Acceptance signals

The plan is working when:

- X11/i3 users can record, optimize, run, and inspect macros with a fast loop.
- Wayland users get precise capability diagnostics instead of generic failure.
- common trigger surfaces (WM binds, launchers, hotstrings, bus events) feel like first-class Linux integrations rather than afterthought exports.
- reports and logs point authors toward concrete fixes instead of just showing raw timings.
- planner/lint output makes long typed-text throughput costs visible before snippet-heavy projects are shipped onto hotkeys or launchers.
