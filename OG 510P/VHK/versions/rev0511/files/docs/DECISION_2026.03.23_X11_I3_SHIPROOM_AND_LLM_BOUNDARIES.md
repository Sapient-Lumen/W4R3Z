# Decision — X11/i3 shiproom and LLM boundary contract (2026.03.23)

Status: accepted for the current flagship lane.

This note tightens the active product story into one operator/LLM-facing rule:
**keep work that sharpens the warm i3/X11 lane; demote work that mostly broadens Linux scope without improving that lane.**

## The current shiproom order

1. **Resident-runtime honesty and fast path**
   - keep `vhk-emit -> socket -> resident busd` cheap
   - treat session drift, runtime-contract drift, and daemon-epoch drift as first-class blockers
   - prefer bounded reload/restart receipts over hand-wavy "service answered" claims

2. **Reliable i3/X11 control primitives**
   - prefer i3 IPC for workspace/window truth
   - keep X11 focus/window/cursor control explicit and testable
   - do not hide focus-sensitive behavior behind generic cross-desktop abstractions

3. **Recorder -> cleanup -> replay contract**
   - recorder sidecars are product, not scaffolding
   - cleanup is reviewable and optionally applied, not magical background mutation
   - replay proof and durable signoff must stale honestly after source/runtime/session drift

4. **Private-LLM author loop**
   - macro YAML is the canonical editable surface
   - generated helpers, receipts, logs, and runtime snapshots are inspect surfaces, not source
   - execution happens only through explicit generated wrappers

## What now gets demoted unless it pays rent to the X11/i3 core

- broad Wayland parity
- portal-first runtime activation as the default story
- app-native adapters that do not improve the i3/X11 lane
- abstractions whose main effect is to blur runtime/session/window truth

## Engineering consequences

### Runtime

The session-bound user service remains the default runtime story. The warm lane is not "healthy" merely because a process answers a socket; it is healthy only when the live daemon is bound to the live X11/i3 session and still serving the expected watcher/runtime contract.

### Dispatch

Thin emitters stay thin. i3 binds and wrapper scripts should emit compact events into the resident lane rather than respawning heavyweight CLI logic for every hotkey.

### Source authority

The flagship editing story is:

1. inspect the selected-macro ticket / author loop
2. edit checked-in macro YAML
3. rerender / lint / validate
4. replay or dispatch through explicit wrappers
5. inspect new proof

### Recording

The recorder lane is not optional product garnish. If a macro is UI-shaped, missing or stale recorder context is allowed to outrank generic execution advice.

## Why this decision exists

The repo already had the right primitives, but the keep-vs-demote rule and the project-wide edit/inspect/actuate boundary were still too implicit. The generated `control-plane.json` now carries both explicitly so operators and private LLM loops can make the same decision without re-reading long prose docs.
