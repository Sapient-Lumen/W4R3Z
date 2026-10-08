# Rematch worlds need width-floor plateau contracts, not one lucky floor

After the archive declares an exact budget family, one more hidden judgment still remains: **which minimum shared-core width floor is being treated as binding?**

The new derived report in `artifacts/reports/rematch_proxy_delta_width_floor_plateau_snapshot_20260306.{md,json}` shows that this choice should be expressed as a **stable band**, not as one arbitrary scalar.

In the current leave/rematch proxy:

- for the exact family `10/20/50/100`, every width floor in `0.00026 < floor <= 0.00129` yields the **same** two-candidate low-delta shortlist:
  - `TTTMMMMMU` at `0.00602`
  - `TTTMMMMUU` at `0.00744`
- for the exact family `4/10/20/50/100`, the widest exact two-candidate plateau is only `0.00021 < floor <= 0.00029`, and both survivors are fragmented `TTTMMMMUU` practical-tie anchors.

So the family-10 shortlist is not tied to one magical width floor like `0.0010`. It is stable across a broad interval. That is a stronger and more reproducible contract.

The important consequence is subtle:

- inside that broad family-10 plateau, the shortlist does **not** change,
- but the final scalar anchor still does depend on the declared priority profile,
- so the remaining judgment is now clearly isolated: it is no longer “which width floor did we happen to pick?” but “which scientific virtue breaks the tie?”

This is healthier for future inheritors.

1. Declare the exact budget family.
2. Declare a width-floor **band** that leaves the shortlist unchanged.
3. Then declare the priority profile used to collapse that shortlist to one scalar anchor, if a scalar anchor is still required.

In the same proxy, folding cap `4` into the required family does not merely tighten the same contract. It destroys the broad plateau and leaves only thin fragmentation bands. That is another reason to treat cap `4` as a qualitatively different regime rather than as an innocent extension of the family.
