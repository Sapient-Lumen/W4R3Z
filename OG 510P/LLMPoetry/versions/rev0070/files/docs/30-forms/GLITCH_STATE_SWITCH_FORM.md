# Glitch State-Switch Branch Lattice

Status: active for `P0001-D006`.

This form treats glitch as a state transition rather than decoration. A draft has two rendered states:

1. **Closed state**: the selected branch path can be read alone.
2. **Open state**: the same selected lines return with shadow triplets appended from the unselected branch endings.

The apparatus is not an explanation after the poem. It is the operation that changes the poem. The open state must be mechanically recoverable from the branch packet, selector map, selector vector, and state-switch receipt.

Required checks:

- branch packet has one selected candidate per layer;
- selected initials spell the declared word;
- final words of unselected candidates spell the declared shadow sentence;
- selected lines have exact character-position selectors;
- selector-vector slices recover the shadow in equal-width pieces;
- state-switch receipt preserves line count while appending the shadow slices;
- same-turn quality judgment is prohibited.

Risk: this can still become theatrical apparatus. A future cold review must ask whether the open state changes reading pressure or merely prints the receipt more elegantly.
