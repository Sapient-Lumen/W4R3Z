# Recursive Zero Route form

Form ID: `FORM-recursive-zero-route-state-switch-branch-lattice`

A Recursive Zero Route is a branch-lattice poem in which the selected surface routes through omitted candidates by a deliberately constant code.

## Requirements

1. The branch packet contains `N` layers and exactly one selected candidate per layer.
2. Each layer contains the same number of omitted candidates, usually three.
3. Selected candidate initials spell a declared word.
4. Unselected candidate final words, in packet order, spell a shadow sentence.
5. Selected-line spans are addressable by selector map and selector vector.
6. Opening the apparatus creates a state-switch by appending shadow slices to selected lines.
7. The ergodic traversal rule is `len(selected_final_word) % omitted_candidate_count`.
8. In the zero-route variant, every route index must equal zero.
9. The first omitted candidate in each layer therefore produces a route sentence.

## D008 instance

`P0001-D008` has seven layers spelling `RECURSE`. Every selected final word has length `3`; every layer has three omitted candidates; therefore each route index is `3 % 3 = 0`.

The route sentence is:

```text
open it again until you return changed
```

## Risk

The form may become too deterministic or too neatly self-explaining. A zero vector is only interesting if the returned reading actually changes the surface, not if it merely proves the arithmetic.

## Verification

Use:

```bash
make branch-selector
make selector-map
make selector-vector
make loss-budget
make state-switch
make ergodic-traversal
make zero-route
```

Validation remains bookkeeping only.
