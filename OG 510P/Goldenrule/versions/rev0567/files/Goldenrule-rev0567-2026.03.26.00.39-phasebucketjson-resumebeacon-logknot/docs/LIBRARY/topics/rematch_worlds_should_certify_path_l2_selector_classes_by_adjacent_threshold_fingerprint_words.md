# Rematch worlds should certify path L2 selector classes by adjacent-threshold fingerprint words

Once path-`L2` selector classes are already keyed as `half_step_selector_index = h`, the archive can certify them without replaying full witness projections.

Sweep the `16` adjacent width-`1` feasible intervals `[0,1]` through `[15,16]`. Each interval has one odd midpoint threshold `2j+1` on the same half-step lattice. Compare `h` to that threshold:
- write `L` when `h < 2j+1`,
- write `B` when `h = 2j+1`,
- write `R` when `h > 2j+1`.

The resulting `16`-symbol word is a complete behavioral certificate for the selector class. Valid certificates are exactly the monotone ternary words
- `R^kL^(16-k)` for singleton selectors, and
- `R^kBL^(15-k)` for adjacent tie selectors.

Practical consequence for inheritors:
- use the adjacent-threshold fingerprint word as a compact regression and audit certificate for path-`L2` selector classes;
- decode it back to `half_step_selector_index` by counting leading `R` symbols and then checking whether the next symbol is `B`;
- on the current path, the `33` selector classes map bijectively to `33` such words;
- the same `16` adjacent intervals remain a minimal complete separating family, because omitting any one interval drops the signature catalog uniformly from `33` classes to `31`;
- and any future non-monotone fingerprint word should be treated as a redesign signal for the current path geometry rather than as normal drift.

Do **not** use the fingerprint word as a replacement for the feasible-band clamp law; it certifies the unconstrained selector class, while feasible witness execution still clamps that class into the doubled feasible band.
