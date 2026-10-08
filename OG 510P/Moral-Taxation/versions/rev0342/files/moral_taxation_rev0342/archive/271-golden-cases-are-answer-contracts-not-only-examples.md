# 271. Golden cases are answer contracts, not only examples

Golden cases now do more than illustrate doctrine. They are compact fact packets that drive a deterministic candidate router and answer contracts that block regressions when the router misses a protected route, collapses a composite case, or returns a tempting but wrong category.

Rev0320 hardens the runtime boundary. `tools/route_case.py` now returns both combined facts-and-axes candidates and facts-only candidates, and `tools/audit_case_contracts.py` requires expected routes to appear in both windows. A case can still contain judgment, but the release can no longer claim case discipline merely because expected IDs or normalized tags are internally self-consistent.

The practical rule remains simple: if a case is important enough to keep, it is important enough to run. If a route is expected, it must be surfaced by the router. If the case is composite, every expected route must appear in the candidate set. If a flag is important enough to appear in a case, it should be backed by route, remedy, or axis semantics rather than living only in prose.

## Source cues

[S21][S27][S59][S594]

[S21]: ../SOURCES.md#S21
[S27]: ../SOURCES.md#S27
[S59]: ../SOURCES.md#S59
[S594]: ../SOURCES.md#S594
