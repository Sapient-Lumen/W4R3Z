# Scenario: feature unification forces vendoring, but policy blocks it

This scenario exists because `system-deps` issue #97 calls out additive `vendored` features as a real problem: one dependency can silently force source builds across the graph, which is hard to detect and may violate air-gapped or distro-managed policy.

The worthy crate should freeze that as an explicit policy finding before pretending the build merely “failed somehow.”
