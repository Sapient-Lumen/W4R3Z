# Scenario: typosquat campaign signal forces manual review even with a clean registry surface

This scenario protects against one ordinary lie:

- the graph has no current advisory on the intended legitimate dependency,
- the registry surface looks routine,
- but a similarly named dependency is close enough to a recently attacked namespace family that the graph should still stop for identity review.

The fixture keeps `identity-risk.report` and `policy-decision.report` separate so a clean registry surface does not erase identity confusion.
