# Scenario: workspace overlay authorizes a break-glass network grant

The crate manifest declares default-deny network policy.
A temporary workspace overlay authorizes network egress for one build script to fetch a vendor artifact during migration.

This scenario exists so the kit records that the overlay, not the crate manifest, became the true authority route.
