# Rematch worlds should store keyless weight vectors inside packed seeds

The packed nanoframe pass already made first writes and repeats much smaller than tagged microframes. But one mode was still paying an avoidable archive tax: `oracle_weights` packets were carrying the full eight-key JSON weight map even inside the packed seed tier.

That is unnecessary in this archive because the family10 weight order is already fixed:

`[w_width, w_buffer, w_knife, w_delta, w_material, w_undecided, w_ties, w_hazard]`

So the archive can store a **bitmask plus ordered nonzero values** instead of a keyful mapping. Missing coordinates are reconstructed as canonical zeroes on read. This stays exact because `packet_from_weights(...)` already canonicalizes the declared weights before classification.

The storage consequence is sharp:

- a hazard-only declaration shrinks from a `125`-byte legacy packed seed to `9` bytes,
- a mixed sparse declaration shrinks from `129` to `15` bytes,
- and even a dense all-ones declaration shrinks from `125` to `23` bytes.

Those numbers now reflect the later scalar-atom pass as well: the weight vector removes the repeated axis names and explicit zero coordinates, and the scalar atom codebook removes repeated quoted decimal strings like `1`, `2`, `0.5`, and `0.2`.

So future inheritors should keep `packed_seed` as the default first-write tier when the local packed codec is available, but treat the **keyless weight vector** as the correct packed payload for `oracle_weights`. The archive should not spend durable bytes repeating fixed axis names, explicit zero coordinates, or common decimal strings when the codec already knows the order.
