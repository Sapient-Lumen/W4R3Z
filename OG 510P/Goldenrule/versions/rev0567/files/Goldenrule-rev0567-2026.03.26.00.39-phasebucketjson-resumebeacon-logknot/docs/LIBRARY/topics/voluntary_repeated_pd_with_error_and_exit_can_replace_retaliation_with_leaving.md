# Voluntary repeated PD with error and exit can replace retaliation with leaving

A new source sharpens what the next implementor should expect once Concord grows from fixed-pair reciprocity into a genuine leave/rematch world.

- `RS-GR-132` studies a voluntarily repeated Prisoner's Dilemma with substantial behavioral error, frequent strategy introduction, and the option to leave.
- In that setting, classical retaliatory fixed-pair winners such as Grim, Tit-for-Tat, and Win-Stay-Lose-Shift no longer dominate.
- The successful sanctioning pattern shifts toward **leave after exploitation** rather than **stay and retaliate by defection**.
- The paper also reports a directional reversal that matters for benchmark design: increasing expected interaction length can reduce cooperation without leaving, yet raise it when leaving is possible.

## Why this matters for Concord

The archive already knew that unilateral exit is not partner choice and that rematch delay is a first-class world parameter.
`RS-GR-132` strengthens the next tranche choice:

> once a true leave/rematch world exists, do **not** assume the fixed-dyad winners remain the right baselines.

A noisy voluntary-repetition lane should explicitly re-benchmark the classical families under:

1. endogenous leaving,
2. rematching / outside-option structure,
3. substantial implementation error,
4. and fresh-strategy pressure or at least heterogeneous entrant pools.

## Minimal implementor handoff

Before spending budget on broad search in a rematch world, run one compact baseline panel with:

- TFT,
- WSLS,
- Grim,
- one leave-based sanction baseline,
- and one Golden-Rule candidate.

Publish whether cooperation is maintained by **retaliatory staying** or by **selective leaving**.
That distinction is scientifically material and should not be hidden inside one payoff table.
