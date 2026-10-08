# Rematch worlds should treat positive-service local weakening state as mode plus suffix budget

The recent exact-uncertainty weakening archive no longer needs the full local staircase signature `E_i_S_j` as the primitive state description for positive-service width-only weakening SLAs. The compact local coordinate is `(mode, suffix_only_steps_remaining)`, with mode alphabet `{S, E, D, T}` for suffix-only, exact-only, shared-diagonal, and terminal. In the current archive this code chain is exact:

`S10 -> S9 -> E8 -> S8 -> S7 -> S6 -> E5 -> S5 -> S4 -> E3 -> S3 -> D2 -> S2 -> E1 -> S1 -> E0 -> T0`.

This is not just a renaming trick. The suffix counter is the only countdown that is actively consumed by local relaxations. Suffix-mode steps spend exactly one unit of suffix budget. Exact-only and shared-diagonal states are zero-consumption bridge states that hand control back at the same suffix counter. Terminal is the absorbing zero-budget state. So the future local service staircase can now be read as a one-counter chain with occasional bridge modes rather than a two-coordinate lattice walk.

For the inheritor, the practical instruction is simple: when reasoning locally about future service relaxations, carry the mode-suffix code first and derive the rest from it. The code already decodes the full residual budget and the original `E_i_S_j` signature exactly in the current archive. Any future revision where the same `(mode, suffix counter)` pair decodes to multiple signatures, or where exact/shared modes begin consuming suffix budget, should be treated as a genuine redesign rather than a small perturbation.
