# Shadow comparison packets, minimal pre-promotion lanes, and overflow tests

This is the compact successor surface for `OQ-0116`.
Use it when a candidate landing surface, wrapper, or packet should see live-ish pressure before promotion but must not yet become serve authority.

## The compact packet

A real shadow comparison packet should name only the clauses that make the compared lane interpretable and promotion-governed:

1. **candidate surface and control surface** — what is being tested, and what still serves the live baseline.
2. **comparison frame** — what request family, population, traffic slice, or time window the compared lane actually covers, or an explicit non-comparability note if that never became honest.
3. **serve-authority and sink rule** — what surface still returns authoritative output, whether candidate outputs are non-returning, log-only, or inspection-only, and an explicit note that mirror responses are ignored rather than quietly treated as live authority.
4. **selection and delivery geometry** — whether the candidate saw all eligible requests, a sampled percentage, a fraction, or a route subset, whether the compared lane ran for a predefined duration, and whether mirrored delivery was guaranteed, best-effort, or fire-and-forget.
5. **request-shape and substrate witness** — whether any host rewrite, header mutation, protocol bridge, or route-kind shift changed what the candidate saw, whether the lane stayed on the same endpoint/backend type/protocol/route kind the mirroring substrate actually supports, and what one production/one shadow, one deployment, or one single destination endpoint limits applied.
6. **side-effect isolation** — whether the candidate path was read-only, dry-run-aware, isolated to a non-authoritative sink, or reconciliation-backed if out-of-band writes could still occur.
7. **comparison basis and verdict gate** — what metrics, rubric, or side-by-side judgment counted, what initial delay, minimum sample, or comparison duration made the verdict mature enough to count, what aggregate-versus-slice guardrail or missing-data rule still applied, and what explicit verify or approval surface actually clears promotion.
8. **promotion consequence** — what abort trigger, soak window, rollback, continued-shadow, or promotion outcome follows.

## What keeps the packet honest

The packet stays compact by preserving only the clauses that official shadow and mirroring substrates repeatedly make non-ambient: production responses stay authoritative while shadow responses are ignored; traffic may be mirrored only for a bounded duration or bounded percentage; mirrored delivery may be best-effort rather than guaranteed; and the supported topology may limit the comparison to one production lane, one shadow lane, or one single mirror destination endpoint. See `docs/00-meta/bibliography.md#ref-0790`, `docs/00-meta/bibliography.md#ref-0791`, `docs/00-meta/bibliography.md#ref-0792`, `docs/00-meta/bibliography.md#ref-0793`, `docs/00-meta/bibliography.md#ref-0794`, and `docs/00-meta/bibliography.md#ref-0795`.

## Overflow test

Reopen the stronger machinery only if one compact packet is no longer enough — for example, if the archive honestly needs standing multi-candidate adjudication, persistent scorekeeping across many mirror lanes, or a durable promotion-verdict controller that cannot be expressed as one bounded packet plus an explicit verify or approval surface.

Until then, prefer this compact successor surface over a scorecourt, mirror senate, or release-trial board.
