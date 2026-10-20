# ADR 0173: Qualify bounded multi-route sync population

Status: accepted for eight simultaneous tree pulls on two bulk routes over direct UDP and forced
TCP, 2026-08-25.

## Context

ADR 0171 proved the fixed and adaptive selectors with only two overlapping jobs. It established
topology, but could not show how either policy fills both routes, whether every admitted job makes
progress, or what one larger scheduler phase costs. ADR 0172 then bounded cancellation for one live
pull. Gate 4 still needed a population experiment large enough to saturate one route's signed work
budget and force spillover without turning the cell into another bulk-throughput benchmark.

A status sampler cannot require observation of a live positive byte position for a small object. A
complete transfer can begin and commit between two samples. Treating that outcome as “no progress”
would make sampling cadence, rather than product truth, the gate. Conversely, calling the resulting
timestamp an exact first-byte measurement would overstate the evidence.

## Decision

The `sync-tree-route-population` Sandwurm scenario constructs one protected primary and two
reciprocally authenticated bulk workers per guest. Each bulk worker exposes eight signed work units.
For each policy it starts eight independent manual-activation tree pulls; every pull contains a
131,139-byte treepack artifact plus its manifest and consumes two work units. The client snapshots
the two eligible worker keys before admission and accepts only those exact current incarnations as
carriers.

The fixed selector must fill one route before spilling to the other, producing normalized carrier
pattern `00001111` and maximum prefix imbalance 4. The conservative adaptive selector must alternate
the equally sized jobs, producing `01010101` and maximum prefix imbalance 1. Every job must request,
admit, and commit exactly two immutable objects, explicitly activate its exact signed HEAD, leave
staging empty, and release signed route work to zero.

Progress is sampled truthfully. A job's first progress observation is the first status sample with
either a positive live carrier receive position or at least one committed object. The latter is
conclusive evidence that bytes progressed before the sample, while avoiding a false failure when a
small transfer completes between samples. The exported metric is therefore
`progress-observation-spread-ms`, not first-byte latency.

Each policy phase captures one process-incarnation-fenced client interval with CPU ticks, faults,
context switches, descriptor counts, resident high-water, I/O, and transport iterations. The
adaptive phase runs first, then the same subscriber identity and savedata restart under fixed policy.
After both phases, 40 ordered Ratox samples traverse only the protected primary and every render must
remain below 250 ms. Raw and compact verification bind the exact patterns, counters, activations,
resource-file digests, carrier class, receipts, and binary.

Direct UDP `pair.slx3x0kb` and forced TCP `pair.rrizbuky` pass. The fixed/adaptive durations were
5,675/4,998 ms over UDP and 5,267/4,841 ms over forced TCP. Progress-observation spreads were
1,342/1,371 ms and 1,744/2,139 ms respectively. All 32 cross-cell activations completed, and no
resource interval recorded a major fault or descriptor increase.

## Consequences

- Gate 4's bounded eight-job population and scheduler-phase resource row is closed on the exact
  two-bulk-route topology and both native carrier classes.
- Fixed fill-then-spill and adaptive alternation are now live invariants across a complete route
  budget, not conclusions inferred from two jobs.
- The accepted samples do not show a first-progress fairness improvement from adaptive selection.
  Adaptive completed slightly sooner in both ordered cells, but one run per carrier with a fixed
  adaptive-first phase order is not a comparative performance result.
- The 131 KiB objects deliberately measure job population and object turnover. They do not qualify
  larger-object throughput, proportional bandwidth sharing, byte striping, or multi-source fetch.
- Resource intervals include all client-Agent work during the phase and are not scheduler-only CPU
  attribution. Process-lifetime resident high-water also depends on phase order.
- Randomized route startup/fault order, concurrent cancellation, cancellation during route loss,
  independent TCP relays, physical paths, and long-running policy remain open. Adaptive selection
  stays explicit rather than becoming the default. ADR 0174 subsequently closes the bounded
  concurrent-cancellation row while preserving the larger-object/common-link nonclaim.

## Verification

`tools/run-sandwurm-pair.py` rejects a protected or unknown carrier, a pattern or prefix mismatch,
fewer than eight progress observations, incomplete object accounting, missing activation, residual
work/staging, resource-capture drift, or protected Ratox failure. `tools/verify-sandwurm-pair.py`
independently verifies both private raw roots and content-free compact exports; its self-test rejects
altered population fields and resource digests.
