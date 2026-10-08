# Scenario — Chromium EditContext canvas path needs bounds updates and an offscreen accessibility mirror

This scenario exists to keep **web-edit-path truth** and **selection-geometry truth** honest.

The visible editing surface is a custom-rendered canvas-like region.
The engine is using **EditContext** rather than a hidden input, which is a stronger path for composition handling and geometry exchange.
But that still does **not** mean the visible text is automatically accessible.

The scenario should stay explicit about four facts:

1. the visible surface is not the same thing as the accessibility surface,
2. caret / selection / character bounds are being provided to the OS text service,
3. provisional composition text is rendered inline instead of detached in the corner,
4. an **offscreen mirror** is still required so assistive technology can inspect equivalent text/selection state.
