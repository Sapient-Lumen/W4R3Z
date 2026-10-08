# Rematch worlds should compute shared-state equiprobable exact transport margins by affine family

The earlier shared-state exact transport passes already gave two correct switch laws:

- a worst-case law from local **max** bit margins, and
- an equiprobable law from family totals `G - L`.

This pass compresses the equiprobable side one step further. The exact expected advantage of `state prefix once + local choice prefixes` over standalone global exact-word prefixes is now an **affine function of batch length** that depends only on a tiny state family classification.

On the current path the full `153`-state catalog collapses to just **seven** affine laws:

- `9n - 7` for the `23` seven-bit unique-word states,
- `9n - 8` for the `10` eight-bit unique-word states,
- `8n - 7` for the `73` seven-bit interior nonsingletons,
- `8n - 8` for the `32` eight-bit interior nonsingletons,
- `43n/9 - 7` for the `7` seven-bit regular interior singletons,
- `43n/9 - 8` for the `7` eight-bit regular interior singletons,
- and `44n/9 - 8` only for the lone edge state `[15,15]`.

That makes the global picture much easier to carry forward.

- The universal lower envelope is `43n/9 - 8`.
- So every realized state is a **strict expected winner by batch length `2`**, with worst expected margin already `14/9` bits.
- The only one-word expected ties are the `32` eight-bit interior nonsingletons because `8(1) - 8 = 0`.
- The edge case `[15,15]` is slightly *better* than the regular eight-bit singleton family in expectation because two of its global exact-word codes spill to `10` bits.

The inheritor no longer needs to keep the full per-state equiprobable totals in working memory. Once the feasible interval state category and state-prefix width are known, the expected batch margin comes from one short affine formula.
