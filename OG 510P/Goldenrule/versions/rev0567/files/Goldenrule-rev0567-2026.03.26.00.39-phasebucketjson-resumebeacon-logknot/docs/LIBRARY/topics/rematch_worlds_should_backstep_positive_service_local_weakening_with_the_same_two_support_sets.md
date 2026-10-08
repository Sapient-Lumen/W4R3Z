# Rematch worlds should backstep positive-service local weakening with the same two support sets

The recent exact-uncertainty weakening archive already compressed positive-service local state to `(mode, suffix_only_steps_remaining)` and then showed that the whole forward chain can be stepped from two tiny support sets over the suffix counter:

- exact support: `{8, 5, 3, 1, 0}`
- shared support: `{2}`

The next compression is that the same basis is enough to run the chain backward. In the current archive, every non-source local code has a unique strict predecessor. The only source boundary is `S10`, and the only terminal boundary is `T0`.

Backward stepping is local:

- for `S_k` with `k < 10`, inspect `k` itself
  - shared support gives predecessor `D_k`
  - exact support gives predecessor `E_k`
  - otherwise the predecessor is `S_{k+1}`
- bridge states are tiny in reverse as well:
  - `E_k <- S_{k+1}`
  - `D_2 <- S_3`
- terminal entry is `T_0 <- E_0`

This matters because the positive-service local weakening staircase is now an almost perfectly reversible path in the same coordinates. The only extra wrinkle is that the full automaton also contains the absorbing self-edge `T_0 <- T_0`; as a strict chain predecessor, however, terminal still has the unique predecessor `E0`.

For the inheritor, the practical instruction is: when auditing local weakening history or explaining how a band was reached, use the same exact/shared support basis plus the two boundaries `S10` and `T0`. Any future revision where a non-source state gains multiple strict predecessors, or where reverse stepping needs more than the current two support sets, should be treated as a substantive redesign rather than a small perturbation.
