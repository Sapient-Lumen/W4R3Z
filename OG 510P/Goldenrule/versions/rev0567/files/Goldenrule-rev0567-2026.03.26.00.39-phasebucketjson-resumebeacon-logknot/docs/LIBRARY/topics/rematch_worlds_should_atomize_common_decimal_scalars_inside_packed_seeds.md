# Rematch worlds should atomize common decimal scalars inside packed seeds

The packed nanoframe pass and the keyless weight-vector pass removed most of the structural overhead from first writes. But after those gains, a stubborn residue remained: the archive was still spelling out the same quoted decimal strings over and over inside packed seeds.

In the current family10 archive, the recurring atoms are small and unsurprising:

- `1`
- `0.5`
- `2`
- `0.2`
- `0.0001`
- `0.000000`

Once those values recur often enough, it is cheaper to preserve a **tiny scalar atom codebook** in the archive-local packed codec than to keep writing the decimal text inside every new packet body.

So the packed tier should now behave like this:

- keep the existing numeric mode tags,
- keep the finite route/signature codes,
- keep the keyless weight bitmask vector,
- and, wherever a packed seed would otherwise store one of the archive's common canonical decimal strings, store the shared atom code instead.

This remains exact because expansion maps each atom code back to the same canonical decimal string before rebuilding the standalone or archive-local packet.

The storage consequence is material even after the earlier packed passes:

- the representative coordinate seed drops from `16` to `7` bytes,
- the hazard-only packed weight seed drops from `11` to `9` bytes,
- the mixed sparse weight seed drops from `27` to `15` bytes,
- and the dense all-ones weight seed drops from `39` to `23` bytes.

So future inheritors should keep `packed_seed` as the default first-write tier when the local packed codec is available, and should treat the **shared scalar atom codebook** as part of that codec rather than as an optional extra flourish.
