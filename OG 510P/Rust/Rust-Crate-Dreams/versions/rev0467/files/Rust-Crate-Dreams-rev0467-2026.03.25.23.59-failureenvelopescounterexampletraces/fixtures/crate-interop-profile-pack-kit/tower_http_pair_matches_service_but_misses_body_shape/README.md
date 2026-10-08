# Scenario — a tower/http pair matches on `Service` but still misses body or error shape expectations

This scenario exists to force **P-0511** to keep separate:

- the claimed shared ecosystem profile,
- the obligations needed to fit that profile,
- pairwise compatibility reality,
- and raw “these crates use the same broad ecosystem” vibes.

## Why it matters

Two crates can both talk about `tower::Service` and `http::{Request, Response}` yet still require adapters or manual review because body, error, or feature assumptions do not line up cleanly.

## Expected artifact pressure

- `boundary-obligation.receipt.json` should make body/error-shape obligations explicit instead of pretending `Service` alignment settles the whole seam.
- `pair-compatibility.report.json` should be able to say `warn` without pretending the pair is fully incompatible.
- `pair-fidelity.report.json` should distinguish static seam checks from real compile or behavioral witnesses.
