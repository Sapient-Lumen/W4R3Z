# ADR 0279: Close the founding route-policy campaign

Status: accepted, 2026-09-01

## Context

Gate 5 accumulated individual accepted Sandwurm cells but did not have one population-level
accounting rule. It also asked for randomized fault timing even though the bounded construction
laboratory deliberately uses exact timing strata so both sides of a race are reproducible. A small
random sample would cover those boundaries less reliably than the existing stratified cells.

ADR 0277 makes same-machine Sandwurm evidence the repository's complete route substrate. Physical
path independence, production relay diversity, and universal QoS remain nonclaims, not gates.

## Decision

`tools/qualify-route-policy-campaign.py` treats every retained compact proof matching the seven
named route-policy scenarios as one integrity-checked population. It verifies every compact-file
commitment, both content-free role receipts, carrier/scenario identity, and the pair manifest. A
published seed orders the accepted proof IDs by SHA-256 so discovery order cannot bias reporting.
This randomizes the audit schedule, not the historical fault clocks.

The accepted seed `20260901` population contains:

- 16 direct-UDP/forced-TCP cells and 9,814,432 cumulative observation milliseconds;
- startup, delayed admission, population loss, both loss/cancel linearizations, shared-link
  contention, and counterbalanced throughput;
- exact 250, 500, 750, 1,000, 5,000, and 20,000 ms timing strata;
- 131,369, 524,355, 1,048,643, 4,194,601, and 16,777,283 byte artifact strata;
- 16 independently recorded ABBA phase durations, 76,430--94,290 ms; and
- adaptive/fixed aggregate ratios from 1,055,522 to 1,167,986 ppm.

Make `adaptive` the default initial bulk-route selector. It may select only at initial admission or
after an incumbent carrier is already fenced; it still cannot move healthy work. Keep `fixed` as an
explicit deterministic diagnostic policy.

## Consequences

Adaptive placement is the supported ordinary two-route policy on this construction substrate. The
observed 5.55%--16.80% gains are observations, not a throughput promise. Fail-closed versus available
replacement remains an independent owner decision. Logical Ratox protection, physical bandwidth
bonding, strict traffic-class reservation, independent links, and public-relay diversity remain
separate claims.

The campaign receipt is reproducible from `.sandwurm/exports/pairs`; it contains commitments and
aggregates only. It does not need raw disks, identities, payloads, or keys.
