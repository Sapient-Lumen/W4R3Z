# Why rematch worlds need unique minimal cap-probe contracts

Once the remaining choice has collapsed to two anchors and the hazard-normalized margin `rho` determines the full additional-budget-cap path, it is tempting to treat a small probe set as a matter of convenience. The stronger result is better for handoff: if the strict winner classes are open `rho` intervals, then separating any adjacent pair **for all rho in both classes** requires a probe whose threshold equals their shared boundary exactly.

In the current family `10/20/50/100` policy box, the four strict classes are separated by exactly three thresholds:
- `tau(10) = -0.000463764`
- `tau(10000) = 0.000033068`
- `tau(20) = 0.000313597`

Those are not merely memorable reference points. They are the only thresholds that can universally separate the adjacent class pairs. Replacing cap `10` with any larger cap leaves some `rho` just above `tau(10)` still material on that substitute probe. Replacing cap `20` with any other cap leaves some `rho` just below `tau(20)` still stable there. Replacing cap `10000` with any merely “high” interior cap leaves either the one-reversal class or the two-reversal class on the wrong side of the substitute threshold.

So the archive should publish `[10, 20, 10000]` as the **unique** strict-winner probe triple, not as one handy witness set among many. That keeps future sessions from silently weakening the classifier by swapping in nearby caps that feel equivalent but are not.
