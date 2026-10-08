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
