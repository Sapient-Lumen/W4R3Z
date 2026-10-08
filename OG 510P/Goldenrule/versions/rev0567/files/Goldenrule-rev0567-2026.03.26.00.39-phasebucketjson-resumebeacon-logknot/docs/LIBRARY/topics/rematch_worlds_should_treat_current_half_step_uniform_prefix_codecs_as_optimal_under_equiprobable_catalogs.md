# Rematch worlds should treat current half-step uniform prefix codecs as optimal under equiprobable catalogs

The recent normalized half-step transport passes already squeezed the obvious tree-shape slack out of the archive. The next useful inheritance fact is that this is **not just empirical** on the current path: under the archive's current **binary prefix + equiprobable catalog** assumptions, the main codecs are already optimal.

## What is now certified

Three current codec families now have exact uniform-prefix optimality certificates:

- the `153`-state normalized feasible-interval prefix,
- the `513`-word exact shortest-generator-word prefix,
- and the state-known local shortest-word choice prefix families.

That means no alternative binary prefix tree can remove even **one** catalog bit from any of those regimes unless the archive changes assumptions.

## Forced balanced splits on the current path

The current optimal balanced splits are now explicit:

- `153` equiprobable states force exactly **`103` seven-bit leaves + `50` eight-bit leaves**, totaling `1121` bits,
- `513` equiprobable exact words force exactly **`511` nine-bit leaves + `2` ten-bit leaves**, totaling `4619` bits,
- local choice families force the per-family optima:
  - size `1` → `{0: 1}` and `0` total bits,
  - size `2` → `{1: 2}` and `2` total bits,
  - size `18` → `{4: 14, 5: 4}` and `76` total bits.

The current archive codecs already match those forced spectra exactly.

## What this means for future sessions

Future inheritors should **stop searching for shorter uniform binary prefix trees** in these same regimes. The present transport frontier is already closed under the current assumptions.

So if someone still wants more savings, the question is no longer “can we reshape the prefix tree?” The question becomes “which assumption are we willing to change?” The current archive makes the relevant options explicit:

- exploit a **nonuniform** source distribution,
- change the **side-information regime** (for example, known state or canonical reconstruction),
- or leave the current **binary prefix** transport family.

But as long as the catalog is equiprobable and the code must stay binary-prefix, the current tree shapes are already the correct ones.
