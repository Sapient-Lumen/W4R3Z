# Rematch worlds should group repeated weight atoms inside packed seeds

The scalar-atom pass removed quoted decimal text from packed weight seeds, but it still left one avoidable cost in the dense and repeated-value cases: the archive was still writing the **same atom code once per active axis**.

That is fine for one-hot or highly irregular declarations. It is wasteful for declarations like:

- all axes set to `1`,
- half the axes set to `1` and half to `0.5`,
- or any other profile where several active axes share the same scalar atom.

Inside this archive, those cases should now use a **grouped atom-mask form**:

- keep the existing packed numeric mode tag for `oracle_weights`,
- keep the scalar atom codebook,
- but when several active axes share the same atom, store **one axis mask per atom** instead of listing that atom once per axis in fixed order,
- and fall back to the older sparse ordered-value vector when that remains smaller.

This is still exact. Expansion simply paints each stored atom back onto the axes named by its mask and then rebuilds the full eight-axis weight map before reconstructing the archive-local or standalone packet.

The storage consequence is material in the repeated-value cases:

- the dense all-ones packed seed drops from `23` to `12` bytes,
- a two-atom block profile (`1` on the first four axes, `0.5` on the last four) drops from `21` to `15` bytes,
- while one-hot declarations correctly stay on the older sparse vector form because grouping would not help.

So future inheritors should keep `packed_seed` as the default first-write tier when the local packed codec is available, but should treat **grouped repeated weight atoms** as part of that codec and choose the grouped form whenever it is smaller than the scalar-atom sparse vector.
