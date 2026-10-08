# Official voter-information horizontal-rail surface checklist

Use this checklist for official voter-information routes that present **answer-bearing items in a horizontal rail, snap lane, or carousel** where not every official item is visible at once.

## Continuation and discoverability

- [ ] Record which official routes use a horizontal rail, slider, snap lane, or carousel-like continuation pattern.
- [ ] Review whether the route makes it obvious that more official items exist beyond the first visible slice.
- [ ] Review whether the current item and overall set position are visible enough that the voter can tell where they are in the lane.
- [ ] Review whether the first visible item could be mistaken for the whole official set or for the uniquely controlling answer when later items remain offscreen.
- [ ] Review whether a stable “view all” or equivalent overview escape exists when the lane represents only one view onto a larger official set.

## Controls and operability

- [ ] Review whether continuation works without swipe-only discovery or hover-only controls.
- [ ] Review whether next/previous or equivalent controls are clearly labeled and understandable in the implemented page.
- [ ] Review whether any focusable scroll region has a labeled boundary and reachable keyboard posture.
- [ ] Review whether compact/mobile layouts still expose continuation cues instead of silently clipping later items.
- [ ] Review whether the voter can re-find a later item after moving through the lane.

## Motion, focus, and announcements

- [ ] Review whether any automatic rotation is genuinely necessary for an answer-bearing lane.
- [ ] Review whether the voter can pause automatic movement and inspect the current item without racing the interface.
- [ ] Review whether auto-rotation stops on focus/hover and does not silently resume while the voter is still using the lane.
- [ ] Review whether focus stays logical when the visible item changes and whether the route avoids surprise focus jumps.
- [ ] Review whether current-item or item-change cues are exposed to assistive technology without unnecessary interruption.

## Evidence discipline

- [ ] Preserve a small public digest of lane type, control posture, discoverability cues, and verification time.
- [ ] Preserve bounded review evidence that offscreen items remained discoverable on compact/mobile and keyboard paths.
- [ ] Do not retain per-user swipe traces, individualized slide histories, session replay, or other interaction exhaust merely to prove that later items existed.
