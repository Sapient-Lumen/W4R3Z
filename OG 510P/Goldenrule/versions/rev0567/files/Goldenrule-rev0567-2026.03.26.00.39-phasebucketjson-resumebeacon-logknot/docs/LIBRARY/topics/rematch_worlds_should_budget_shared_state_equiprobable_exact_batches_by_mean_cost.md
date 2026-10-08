# Rematch worlds should budget shared-state equiprobable exact batches by mean cost

The previous passes already told the inheritor when shared-state exact transport beats standalone exact-word transport, and how much expected margin that win yields.

This pass turns the same regime into a more direct budgeting rule.

When the decoder already knows that every exact shortest script in a batch shares one feasible interval state and the active source model is equiprobable across the exact shortest branches inside that state, the expected **bits per script** cost is now available directly.

For every realized state, expected shared-state exact transport cost per script has the form

- `local_choice_floor + state_prefix_bits / n`,

where `n` is batch length.

On the current path that collapses the full 153-state catalog to only six families:

- `7/n`,
- `8/n`,
- `1 + 7/n`,
- `1 + 8/n`,
- `38/9 + 7/n`,
- `38/9 + 8/n`.

So the universal all-state ceiling is now just

- `38/9 + 8/n`.

That produces a sharper planning rule than the earlier target-margin language whenever an implementor is working from a direct transport budget:

- want all realized states at or below `9` expected bits per script: use `n = 2`,
- at or below `8`: use `n = 3`,
- at or below `7`: still `n = 3`,
- at or below `6`: use `n = 5`,
- at or below `5`: use `n = 11`.

The boundary is also explicit now.

No finite shared-state batch can force every realized state to or below

- `38/9` bits per script,

because that is the asymptotic local-choice floor of the worst current family.

So future sessions should treat this as the right budgeting law for the equiprobable shared-state exact regime:

- use `local_choice_floor + state_prefix_bits / n` when a specific state class is known,
- use `38/9 + 8/n` when an all-state guarantee is needed,
- and stop searching for finite-batch schedules below the `38/9` all-state floor because that target is unattainable on the current path.
