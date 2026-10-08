# Ergodic Traverse State-Switch Branch Lattice

Status: pilot form introduced in `rev0018` for `P0001-D007`.

The form keeps the previous branch-lattice apparatus but adds a work-path. The selected surface is not merely a poem plus a receipt; its final words become route codes into omitted material.

## Required parts

- A branch packet with one selected candidate and at least one omitted candidate per layer.
- A selected-path acrostic claim.
- A shadow sentence from all omitted candidate final words in packet order.
- Selector-map and selector-vector receipts for selected-line addressability.
- A state-switch receipt that maps closed selected lines to triplet-open lines.
- An ergodic-traversal receipt.

## Traversal rule

For each layer, take the final word of the selected candidate. Compute:

```text
len(final_word) % omitted_candidate_count
```

That index chooses one omitted candidate from the same layer. The chosen omitted candidates form the traversed state. Their final words form the traversal sentence.

## Non-claim

The validator proves only that the route is deterministic and reproducible. It does not prove that the resulting poem is good.
