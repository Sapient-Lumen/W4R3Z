# Rematch worlds should switch shared-state exact transport by equiprobable mean margins

The earlier shared-state exact transport passes established a worst-case crossover rule: three exact shortest scripts sharing one feasible interval state are enough to make `state prefix once + local choice prefixes` strictly beat per-word global exact-word prefixes on every audited case, and a local max-bit formula recovers the exact safe/strict thresholds per state.

This follow-on pass adds the **equiprobable mean-cost** version of the same law.

For a fixed feasible interval state, let:

1. `s` be the interval-state prefix length,
2. `c` be the shortest-word family size,
3. `L` be the total local choice prefix bits across that family.

On almost the entire current path every admissible global exact-word code inside one state still costs `9` bits, but the exact law uses the full family total `G` of global exact-word bits so it also covers the lone split family `[15,15]`, whose global widths are `16 × 9` and `2 × 10` bits. The shared-state mean transport therefore beats the standalone mean transport exactly when the state overhead is amortized against the mean per-word margin `(G - L) / c`.

That gives closed-form mean thresholds.

- **Weak expected switch threshold**: `ceil(sc / (G - L))`
- **Strict expected switch threshold**: `floor(sc / (G - L)) + 1`

The practical inheritance consequence is sharper than the worst-case story.

- Every realized state is already a **strict expected winner by batch length 2**.
- The only states whose strict threshold improves against the worst-case law are the **eight 8-bit interior singletons**, which move from strict threshold `3` down to `2` in expectation.
- The only mean tie at one word comes from the **32 eight-bit interior nonsingletons**, where `8 + 1 = 9` exactly matches the standalone `9`-bit word cost.

So the inheritor now has two compatible rules.

- Use the earlier max-bit threshold when the batch must survive worst-case branch patterns.
- Use this mean-margin threshold when the working assumption is equiprobable exact branches inside a known shared interval state.
