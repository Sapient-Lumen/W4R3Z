# Rematch worlds should close shared-state equiprobable exact batches by marginal gain

The previous passes already gave the inheritor three planning views of shared-state equiprobable exact transport:

- whether it wins,
- how much expected total margin it yields,
- and what expected bits-per-script ceiling it reaches.

This pass turns the same regime into the most local operational rule so far: **is it still worth waiting for one more same-state exact script before flushing the batch?**

Once the active source model is equiprobable across the exact shortest branches inside one shared feasible interval state, the answer depends only on the state-prefix width.

If the current batch length is `n`, then the expected per-script gain from extending the batch to `n + 1` is exactly

- `state_prefix_bits / (n(n+1))`.

Nothing else survives into that marginal law. The local choice floor cancels completely.

On the current path every realized feasible interval state uses either a `7`-bit or `8`-bit state prefix, so the whole `153`-state catalog collapses to just two marginal-gain families:

- `7/(n(n+1))` for the `103` seven-bit states,
- `8/(n(n+1))` for the `50` eight-bit states.

That gives a direct batch-closing rule.

If an inheritor wants at least `t` expected bits-per-script improvement from waiting for one more same-state exact script, keep the current batch open only while

- `current_batch_length <= floor((sqrt(1 + 4 * floor(state_prefix_bits / t)) - 1) / 2)`.

For all-state guarantees, replace `state_prefix_bits` with `7`, because the seven-bit family is the exact lower envelope.

So the universal all-state close schedule is now immediate:

- want at least `2` more expected bits per script from one extra item: keep waiting only through batch length `1`,
- at least `1`: through `2`,
- at least `1/2`: through `3`,
- at least `1/4`: through `4`,
- at least `1/10`: through `7`.

This is the right law for **streaming closure** decisions in the shared-state equiprobable exact regime.

- Use the earlier target-margin and mean-cost laws when sizing a whole batch in advance.
- Use this marginal law when a live writer is deciding whether one more same-state exact script is still worth waiting for.
- And stop carrying the full state category when only the marginal question matters, because only the `7`-bit versus `8`-bit state-prefix split survives.
