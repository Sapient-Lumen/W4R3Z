# Rematch worlds should amortize exact shortest-script transport across shared interval-state batches

When a batch of exact normalized shortest scripts is known to share one feasible interval state, the transport choice should stop treating those scripts as unrelated standalone exact words. The archive now has an exact shared-state law: send the interval-state prefix once, then send only the local shortest-word choice prefix for each script in the batch.

The useful boundary is sharp.

- For shared-state exact batches of length `1`, this path is not yet universally best. It already wins for all unique-word states and all `7`-bit interior nonsingleton states, ties for `8`-bit interior nonsingletons, and loses for interior singleton states.
- For shared-state exact batches of length `2`, it never loses on the audited catalog. The only surviving ties are `116` narrow cases inside the `8`-bit interior-singleton corner.
- For shared-state exact batches of length `3` or more, it is strictly better than per-word global exact-word prefixes on every audited case.

That gives the inheritor a clean rule.

1. If exact scripts do **not** share a feasible interval state, keep using the earlier shortest-script transport frontier.
2. If they **do** share one feasible interval state and the batch has at least `3` scripts, switch immediately to `state prefix once + local choice prefixes`.
3. If the shared-state batch has exactly `2` scripts, the same shared-state path is still safe because it never loses, even though a tiny tie corner remains.
4. Only one-word exact transport needs the older frontier logic.

This pass is intentionally narrow: it does not add a new codec family. It only records when the archive should amortize the already-certified state prefix and local choice prefix over repeated exact scripts from the same normalized interval state.
