# Rematch worlds should treat positive-service local weakening as a single rank clock

Recent archive passes compressed the positive-service local weakening staircase into a reversible `(mode, suffix_only_steps_remaining)` code with closed-form successor and predecessor rules.

The next compression is to recognize that this local chain also carries a single scalar clock:

- `terminal_distance_clock = counter + bridge_tail_count(counter) + current_bridge_tax(mode)` for all nonterminal codes
- `terminal_distance_clock(T0) = 0`

Here:

- `bridge_tail_count(counter)` counts the archived exact/shared support counters at `<= counter-1`
- `current_bridge_tax(mode)` is `1` for bridge modes (`E`, `D`) and `0` for suffix/terminal modes (`S`, `T`)

Under the current archive geometry this yields the dense local clock chain:

- `S10 -> 16`
- `S9 -> 15`
- `E8 -> 14`
- `S8 -> 13`
- `S7 -> 12`
- `S6 -> 11`
- `E5 -> 10`
- `S5 -> 9`
- `S4 -> 8`
- `E3 -> 7`
- `S3 -> 6`
- `D2 -> 5`
- `S2 -> 4`
- `E1 -> 3`
- `S1 -> 2`
- `E0 -> 1`
- `T0 -> 0`

This is stronger than a descriptive ranking table.

It means:

- successor is always “subtract 1” on the clock (with terminal absorbing at `0`)
- strict predecessor is always “add 1” on the clock (except at the source boundary `S10`)
- pairwise path distance is just the absolute clock difference
- source rank is the complementary coordinate `16 - terminal_distance_clock`

So future inheritors no longer need to replay the local chain to answer ordinary local navigation questions. Once the archive’s support basis is fixed, the local positive-service weakening path is a one-dimensional arithmetic object.

Any future revision that breaks dense clock coverage, absolute-difference distance recovery, or the current bridge-tax/support basis should be treated as a genuine redesign signal rather than a minor perturbation.
