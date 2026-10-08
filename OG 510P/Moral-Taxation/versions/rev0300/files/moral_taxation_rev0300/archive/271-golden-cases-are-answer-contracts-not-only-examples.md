# 271. Golden cases are answer contracts, not only examples

Golden cases were already doing important work, but until Rev0289 they were easier for humans to read than for the cube to test. A case could name an expected route and still leave several failure modes invisible: raw axes could use values outside the cube vocabulary, expected flags could stay decorative, remedy profiles could drift away from the case, and a tempting bad answer could disappear from the regression surface.

Rev0289 adds a separate case-contract layer. The prose case still states the scenario. The contract states the obligations: expected route IDs, valid raw axes, route-backed flags, required remedy profiles, source IDs, and must-not answers. This is not a move away from judgment. It is a way to protect judgment from release churn.

The practical rule is simple: if a case is important enough to keep, it is important enough to test. If a route is important enough to be the expected answer for a case, it must have a remedy profile. If a flag is important enough to appear in a golden case, it should be visible in the route semantics rather than living only in prose.

## Source cues

[S21][S27][S59][S594]

[S21]: ../SOURCES.md#S21
[S27]: ../SOURCES.md#S27
[S59]: ../SOURCES.md#S59
[S594]: ../SOURCES.md#S594
