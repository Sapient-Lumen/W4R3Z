# Rematch worlds should step positive-service local weakening with a two-support successor automaton

The recent exact-uncertainty weakening archive already compressed positive-service local state to `(mode, suffix_only_steps_remaining)`. The next compression is to stop carrying the full successor chain as a remembered list. In the current archive, the entire local successor law is generated from just two small counter-support sets:

- exact support: `{8, 5, 3, 1, 0}`
- shared support: `{2}`

From a suffix state `S_k`, consume one unit of suffix budget and inspect the next counter `k-1`. If that next counter is in shared support, the next state is `D_{k-1}`. If it is in exact support, the next state is `E_{k-1}`. Otherwise the successor stays suffix as `S_{k-1}`. The bridge rules are then tiny: `E_k -> S_k` for `k > 0`, `E_0 -> T_0`, `D_2 -> S_2`, and terminal is absorbing as `T_0 -> T_0`.

This matters because the whole audited positive-service chain is now mechanically regenerable from a tiny successor automaton rather than from an archived table:

`S10 -> S9 -> E8 -> S8 -> S7 -> S6 -> E5 -> S5 -> S4 -> E3 -> S3 -> D2 -> S2 -> E1 -> S1 -> E0 -> T0`.

For the inheritor, the practical instruction is: step local service relaxations by the automaton first, and treat the support sets themselves as the real local geometry. Any future revision that needs more than the current exact/shared support sets to determine the successor, or that breaks chain regeneration from `S10`, should be treated as a substantive redesign rather than a small perturbation.
