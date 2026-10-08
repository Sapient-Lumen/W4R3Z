# Performance notes

VHK is often used in **polling** patterns:

- `WaitForImage*` / `WaitForPixel*`
- `VisualAssert` / `WaitForRegionChange`
- `WaitForText*`

In these loops, the *current* screenshot changes every attempt, but the
*reference assets* (needles, baselines, OCR configs) usually do not.

## Cached decoding for needles + baselines

As of v0.22.48, VHK keeps a small in-process cache for:

- **needle metadata** (`foo.png` + `foo.json`) keyed by the JSON sidecar mtime
- **decoded pixels** for relatively-static image assets (needles/baselines)
  keyed by the image file mtime

This avoids re-reading and decoding the same PNGs hundreds/thousands of times in
polling waits.

### Safety

- If an asset changes, its mtime changes and the cache automatically invalidates.
- If a JSON sidecar is invalid (mid-edit), VHK caches `None` until the file is
  modified again.

### Debugging

If you suspect caching is hiding asset edits during a run, stop and re-run the
macro (caches are in-process only).

## Hotkey trigger latency

If you run macros from a window manager binding or a hotkey daemon, startup time
can matter.

Recommended low-latency pattern:

1) Run a long-lived bus watcher with `dispatch: true` (see `docs/BUS_EVENTS.md`).
2) Export hotkeys with `--via-bus` so the hotkey command only emits a small IPC event.
3) Prefer `vhk-emit` as the emitter (it avoids importing the full CLI stack).


## Event-log optimization loop

A fast Linux-native macro engine needs a tight loop between **run**, **measure**, and **cleanup**. VHK's event log/report flow is meant to provide that loop without requiring a GUI first.

Recommended workflow after recording or after a flaky run:

1. Run the macro with event logging enabled (default in normal projects).
2. Inspect the newest run with `vhk report --project . --latest`.
3. Follow the advice section: replace brittle `Delay` steps, shrink visual search regions, move from polling to event-driven waits where possible, and review capability mismatches with `vhk doctor` / `vhk validate`.
4. Use `vhk optimize` / `vhk optimize-project` on recorder output before doing manual polish.

This is intentionally heuristic, not magical. The report can point to likely Linux bottlenecks, but the final authoring decision stays explicit and filesystem-friendly.

## Planner-side performance profile

`vhk plan-project` now emits a `performance_profile` section in both JSON and
terminal output. The goal is not microbenchmark theatre; it is to expose the
*shape* of likely runtime cost before the project is shipped onto a hotkey,
watcher, or desktop launcher surface.

The profile currently highlights:

- unscoped live capture steps (screen-backed image/OCR actions without a region)
- aggressive polling waits
- OCR-heavy runtime paths
- large fixed-delay budgets
- heavy macros that sit directly on hotkeys instead of behind a lightweight dispatch lane

This is meant to complement `vhk report`, not replace it:

- `plan-project` answers **what looks expensive or latency-sensitive in the source tree**
- `report` answers **what was actually slow or flaky in a real run**

Use both. Planner output is a design-time warning surface; event logs remain the
truth source for host-specific timing.


## Text throughput is a first-class performance concern

AHK-class usefulness on Linux is not only about hotkeys and pointer playback. A
large share of real automation is **text throughput**: snippets, forms, canned
responses, and structured field entry.

VHK now treats long literal `TypeText` bodies as a planner/lint signal too:

- long single-body text can often move to `backend=clipboard`
- Tab/Enter-rich form text can often move to a hybrid segmented lane
- interpolation-heavy or delayed typing should stay explicit and visible

The rule of thumb is simple: keep per-character typing when semantics matter;
promote or segment when throughput matters more.
