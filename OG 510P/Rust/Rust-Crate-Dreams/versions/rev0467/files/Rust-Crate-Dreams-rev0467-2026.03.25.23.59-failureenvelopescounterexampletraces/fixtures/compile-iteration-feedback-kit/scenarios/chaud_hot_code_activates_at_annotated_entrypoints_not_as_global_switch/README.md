# Scenario — Chaud activation is entrypoint-gated, not a global instant switch

Chaud documents that hot-reloaded code only becomes active once a `#[chaud::hot]` function is called.
It also documents that old code can continue via function pointers or trait objects.

So the iteration bundle should not claim:
- immediate global activation,
- universal fresh-code takeover,
- or a zero-residency stale-code story.

It should at least export an `activation-boundary.report` making the delayed activation boundary explicit.
