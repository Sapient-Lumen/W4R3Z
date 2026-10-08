# Scenario — independence pairs need test lineage, not just percentages

This scenario protects against a common bluff: an overall coverage summary can look healthy while still failing to show **which test executions formed each independence pair**.

The crate must keep independence evidence and lineage linked.
