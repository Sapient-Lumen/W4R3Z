# Scenario: workspace feature forwarding

Purpose: prove that the kit can emit a **short cause chain** for a feature that feels “indirect” to the user.

This is the most important baseline because Cargo's official troubleshooting advice already points people toward `cargo tree --edges features --invert`, but that workflow is still too manual for CI, review, or support handoff.
