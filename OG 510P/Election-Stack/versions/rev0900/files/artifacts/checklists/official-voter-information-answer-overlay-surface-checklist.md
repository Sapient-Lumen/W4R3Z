# Official voter-information answer-overlay surface checklist

Use this checklist for official voter-information routes that place **the controlling answer, item details, or next official action inside a dialog, drawer, bottom sheet, or similar answer-bearing overlay**.

## Trigger and route posture

- [ ] Record which official routes expose answer-bearing overlays.
- [ ] Review whether the overlay opens only after explicit voter action rather than on page load, hover, or focus exploration.
- [ ] Review whether the overlay is really needed for the answer-bearing task or whether the route should expose the controlling answer directly in ordinary page flow.
- [ ] Review whether the overlay context clearly names the selected office, location, notice, or item.
- [ ] Review whether the route preserves a stable non-overlay detail route or equivalent share-safe recovery path when the overlay contains controlling information.

## Close, return, and same-item recovery

- [ ] Review whether closing the overlay returns the voter to the same parent route context and same item rather than resetting the current list, map, filter, or viewport state.
- [ ] Review whether the overlay keeps deep-link, share, revisit, and citation posture legible enough that the answer is not trapped in a transient UI layer.
- [ ] Review whether the overlay distinguishes temporary inspection from the durable official route clearly enough that the voter can tell where the authoritative path lives.
- [ ] Review whether the route preserves an easy overview/help escape when the overlay is incomplete or inconvenient.
- [ ] Review whether reopening the same item is ordinary and predictable rather than requiring the voter to rediscover it from scratch.

## Accessibility and compact/mobile review

- [ ] Review whether focus moves into the overlay when it opens and returns to a sensible location when it closes.
- [ ] Review whether keyboard users can reach the close control and traverse the overlay without leaking into ambiguous background interaction.
- [ ] Review whether screen-reader users hear a clear overlay label and enough context to identify the selected item.
- [ ] Review whether small-screen, zoomed, and rotated layouts keep the overlay heading, close posture, and route-return meaning legible.
- [ ] Review whether modal/background behavior matches what the route visually claims about the overlay.

## Evidence discipline

- [ ] Preserve a small public digest of which routes use answer-bearing overlays, what type of overlay appears, and whether a stable non-overlay route exists.
- [ ] Preserve bounded review evidence showing whether close/return, same-item recovery, keyboard access, and compact/mobile posture remain understandable.
- [ ] Do not retain person-level click trails, individualized overlay-open histories, session replay, or other interaction exhaust merely to prove that the overlay existed.
