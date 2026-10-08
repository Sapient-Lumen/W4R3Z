# Scenario: trait facade contains codec until owned rewrite is ready

This fixture protects against the archive claiming “replaceable later” without a real seam.

The dependency is acceptable today only because one named facade exists, consumers are routed through it, and there is an explicit next-lane transition plan.
