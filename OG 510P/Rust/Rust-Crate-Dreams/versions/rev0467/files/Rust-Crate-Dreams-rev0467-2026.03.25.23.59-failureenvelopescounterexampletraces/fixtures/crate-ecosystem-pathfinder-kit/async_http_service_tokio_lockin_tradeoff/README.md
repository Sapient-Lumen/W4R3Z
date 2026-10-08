# Async HTTP service with Tokio lock-in tradeoff

Simulates a team choosing a service stack where at least two plausible winners exist, but runtime coupling and middleware/ecosystem alignment differ materially.
The decision artifact should not collapse “widely used” into “best for every service.”

Why this matters:
- async service crates often carry runtime, middleware, extractor, and telemetry expectations that become real migration cost later;
- a newcomer-visible popularity signal is useful, but it does not erase lock-in or role coverage differences.

What this scenario should force:
- a role-coverage report for routing, request extraction, serialization, telemetry, and testing roles
- an interop-surface report with explicit runtime coupling and companion-crate expectations
- a decision-axis report where adoption signal stays separate from interop fit and migration friction
- either a reviewable starter set or an explicit `manual_review_required` boundary if the trade-off is too role-dependent
