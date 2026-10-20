# ADR 0170: Select sync routes by bounded visible load

Status: accepted at the deterministic Agent boundary, 2026-08-25.

## Context

Gate 3 used a safe fixed selector: for one proven remote principal, choose the lexicographically first
eligible authenticated bulk route and keep the pull on it until completion or mandatory loss
reassignment. Gate 4 requires comparison with a conservative adaptive policy. A first implementation
must not infer bandwidth from Tox internals, migrate healthy work, let performance scores override
signed capacity, or make changing load counters look like route-incarnation loss.

## Decision

Agent accepts `--sync-route-policy fixed|adaptive` only with explicitly enabled synchronization and
route workers. `fixed` remains the default and preserves stable route-key order. Both policies reject
foreign principals, the exact excluded old carrier, malformed candidates, non-auxiliary carriers,
and routes at their signed work budget.

`adaptive` selects only when a new HEAD becomes an object job or an existing job has already lost and
fenced its carrier. It never moves healthy work. Eligible candidates are ordered by:

1. the exact rational `admitted_work / maximum_active_work`, compared by bounded integer cross
   multiplication rather than floating point;
2. lower signed-lifecycle restart count; and
3. lexicographic Tox route key followed by worker incarnation as a deterministic tie break.

The selector receives only current reciprocally authenticated candidates from Agent. Load and
restart counters are selection inputs but are deliberately excluded from carrier-incarnation
equality; changing a score cannot synthesize an offline event. At each initial admission or mandatory
reassignment, Agent copies the last authenticated-incarnation inventory and overlays the exact
current coordinator work/restart counters before selecting. Thus two serialized overlapping HEAD
results cannot both choose from one stale event-loop load snapshot. Content-free sync status
publishes the selected policy and cumulative fixed/adaptive decision counts.

## Consequences

- This is load-aware admission across pull jobs, not throughput prediction, byte striping, or live
  migration.
- Signed work budgets remain hard ceilings under both policies.
- A newly idle route can receive a later job without disturbing already admitted work.
- Fixed selection remains reproducible and is the reference side of the Sandwurm A/B qualified by
  ADR 0171.
- The route-set, route-binding, sync-wire, and Ratox framing remain unchanged.
- Gate 4 stays open until larger two-guest fixed/adaptive workloads measure fairness and resources,
  concurrent cancellation, randomized route startup/fault order, and relay diversity. ADR 0171
  closes carrier placement, counterbalanced policy phase order, and post-gate protected-Ratox rows;
  ADR 0172 closes the first bounded single-pull cancellation-tail row on UDP and TCP.

## Verification

Selector tests freeze grammar, fixed ordering, full-route skipping, exact unequal-budget ratios,
restart/key tie breaks, principal isolation, old-carrier exclusion, exhausted capacity, and malformed
candidate refusal. The existing two-worker mock Agent loss gate runs in adaptive mode and proves one
initial plus one mandatory-replacement decision, exact convergence/activation on the second carrier,
and live status reporting `adaptive-selections=2` with zero fixed decisions.
ADR 0171 subsequently qualifies the first genuine two-guest topology comparison without changing
this selector contract or claiming a throughput benefit.
