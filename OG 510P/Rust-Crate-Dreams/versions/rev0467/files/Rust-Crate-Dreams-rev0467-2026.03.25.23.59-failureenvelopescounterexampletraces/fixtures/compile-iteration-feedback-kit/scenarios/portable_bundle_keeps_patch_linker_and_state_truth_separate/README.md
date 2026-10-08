# Scenario — portable bundle keeps patch, linker, and state truth separate

This scenario exists because a review bundle is most useful when faster-linking facts, patch-eligibility facts, and state-continuity facts remain separate objects.

The point of this fixture is to prevent future tooling from collapsing all three into one vague “hot reload is supported” verdict.
