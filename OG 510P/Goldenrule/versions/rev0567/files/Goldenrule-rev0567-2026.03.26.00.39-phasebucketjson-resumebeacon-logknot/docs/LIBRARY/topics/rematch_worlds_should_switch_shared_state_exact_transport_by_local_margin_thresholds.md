# Rematch worlds should switch shared-state exact transport by local margin thresholds

The earlier shared-state exact transport pass established a useful global rule: once exact normalized shortest scripts share one feasible interval state, batching quickly makes `state prefix once + local choice prefixes` beat per-word global exact-word prefixes. This follow-on pass makes that switch point exact per state.

For any feasible interval state, compute only three local quantities.

1. The interval-state prefix length `s`.
2. The **largest** local choice prefix length `m` inside that state's shortest-word family.
3. The **smallest** admissible per-word global exact-word prefix length `g` for that same family.

Then the transport thresholds are closed form.

- The shared-state path is **safe** (never loses) for every batch of length `n` exactly when `n >= ceil(s / (g - m))`.
- It is **strictly dominant** for every batch of length `n` exactly when `n >= floor(s / (g - m)) + 1`.

On the current path, `g = 9` for every state, so only the local worst-case choice width matters.

- Unique-word states have `m = 0`, so they switch immediately.
- Interior nonsingletons have `m = 1`, so `7`-bit states are strict at one word while `8`-bit states are safe at one and strict at two.
- Interior singletons have `m = 5`, so `7`-bit states are safe and strict at two words, while `8`-bit states are safe at two and strict at three.

This is the inheritor's practical shortcut: do not remember the older threshold table. Recompute the switch point from the local worst-case bit margin whenever a new exact shared-state batch appears.
