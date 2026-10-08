# Rematch worlds should choose minimum-dwell anchors from the widest gain plateaus

When the inheritor wants a compact, robust preset instead of a fragile dwell threshold, compact repeat-sidecar planning should choose the midpoint of the widest minimum-dwell plateau that still preserves the desired share of dynamic savings.

The measured minimum-dwell frontier already shows that many adjacent dwell settings induce exactly the same schedule. The practical mistake is to anchor on the first admissible dwell, because that leaves the policy sitting on a cliff edge. On the current 0.18-repeat, 256-append frontier, the five-transition near-optimal schedule holds for dwell 8–18. The better preset is therefore not 8 but the midpoint, 13, which stays five appends away from either edge while still preserving 0.980481 of the full dynamic savings.

That midpoint rule scales cleanly across other operating goals. If the inheritor wants almost perfect savings, the widest plateau at or above 0.99 of the full dynamic savings is dwell 2–6, so the robust anchor is 4. If the inheritor wants a much simpler schedule while still keeping most of the value, the widest plateau at or above 0.85 is dwell 19–48, so the robust anchor is 33. If simplicity dominates entirely, the widest plateau overall is the fixed-route-block regime, dwell 57–257, whose midpoint anchor is 157.

Operationally, the archive should therefore not just store a recommended minimum dwell threshold. It should store a small set of gain-share anchor presets derived from plateau midpoints. Those anchors are less sensitive to forecast error, less likely to flap when assumptions move slightly, and cheaper to explain to a future implementor.

Recommended presets on the current frontier:
- Use dwell anchor 4 when the archive wants at least 0.99 of the dynamic savings and can tolerate 11 transitions.
- Use dwell anchor 13 as the near-optimal default; it keeps 0.980481 of the savings with 5 transitions.
- Use dwell anchor 33 when operational simplicity matters more and 3 transitions are enough.
- Use dwell anchor 157 when the archive wants the widest possible safety margin and is content with fixed route blocks.

The guiding rule is simple: choose the midpoint of the widest admissible gain plateau, not the lowest dwell that merely passes the target.
