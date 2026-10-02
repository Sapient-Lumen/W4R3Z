# ADR 0266: Counterbalance content lane scaling

Status: accepted, 2026-08-31

## Context

ADR 0263 measured same-source content caps `1/2/4/8` in one ascending order per native carrier.
ADR 0264 then kept one Ratox attachment alive through caps 1, 4, and 8 and found that cap 8 lost
both content goodput and terminal p95 against cap 4. Those results made cap 4 a plausible explicit
bulk setting, but they did not separate lane count from warm-session, phase-position, or host-load
effects. They also did not measure cap 2 while Ratox was active.

An automatic or default profile must not be selected from one favorable phase order. A useful
counterbalance must make cap 8 the first signed transfer in the reverse cell, rather than running
another cap-1 base transfer and merely replaying the remaining isolated namespaces backwards.

## Decision

Add `sync-content-lane-science-reverse` as the exact descending companion to
`sync-content-lane-science`.

Both scenarios retain:

- one source-linked IoTox binary and the reused immutable private identity baseline;
- one deterministic 8 MiB, 24-chunk, 26-object content-v2 graph;
- one subscriber process with process ceiling 8, one publisher, one authenticated Tox session, and
  zero daemon or carrier restarts;
- the same 4 Mbit/s subscriber bottleneck;
- separately signed effective namespace ceilings `1`, `2`, `4`, and `8`;
- exact live-lane attribution, convergence, explicit activation, per-phase monotonic duration,
  artifact rate, CPU ticks, resident high-water, and transport iterations; and
- strict raw and compact replay over both direct UDP and forced TCP.

The ascending cell signs its already-published base namespace to cap 1 and runs `1,2,4,8`. The
descending cell signs the base namespace to cap 8 and runs `8,4,2,1`. The base signed HEAD is reused
as publication evidence for the initial cap; only the other three caps are republished into isolated
roots. This keeps setup work symmetric and avoids repacking a fourth redundant copy before transfer
measurement.

Add `tools/analyze-content-lane-counterbalance.py`. It must first run the full standalone Sandwurm
verifier over every compact root, reject duplicate roots, mixed binary/artifact identities,
unbalanced orders, restart drift, malformed summaries, or secret-bearing exports, then emit exact
integer distributions. Means are retained as numerator plus denominator instead of rounded
floating-point claims. The canonical report remains content-free.

Keep the ordinary `--max-sync-content-lanes` default at one. Do not add automatic route-based
selection: the process ceiling is chosen before a future route transition, cap 2 lacks simultaneous
Ratox latency evidence, the persistent Ratox cells do not yet meet a frozen interactive SLA, and all
measurements remain two VMs on one construction host.

For explicit latency-insensitive operator tuning, name these construction recommendations:

- cap 2 is the efficient mixed/unknown-carrier and relay-heavy bulk setting;
- cap 4 is the controlled direct-UDP throughput setting when that route is fixed; and
- cap 8 is a qualification stress bound, not a recommended product profile.

Signed namespace policy and outstanding-request quotas may still tighten every process ceiling.
No content-v2, Ratox, CTA1, FileId, authority, HEAD, activation, or local-control frame changes.

## Findings

Every accepted cell reached its exact signed cap, converged, activated, retained the same binary and
artifact identities, and recorded zero restarts.

| Route | Cap 1 mean | Cap 2 mean | Cap 4 mean | Cap 8 mean | Paired winner |
| --- | ---: | ---: | ---: | ---: | --- |
| direct UDP | 406,943 B/s | 423,197 B/s | 439,476.5 B/s | 443,054.5 B/s | cap 8 by 0.81% over cap 4 |
| forced TCP | 295,899 B/s | 370,799 B/s | 354,623 B/s | 294,106.5 B/s | cap 2 by 4.56% over cap 4 |
| both routes | 351,421 B/s | 396,998 B/s | 397,049.75 B/s | 368,580.5 B/s | cap 4 by 0.013% over cap 2 |

The raw aggregate winner is cap 4 by only 51.75 B/s over cap 2. That difference is not operationally
meaningful on this corpus. Cap 2 uses 346.5 mean CPU ticks across the four route/order samples while
cap 4 uses 406.5, a 14.8% reduction. On forced TCP, cap 2 is simultaneously 4.56% faster and uses
21.0% fewer CPU ticks than cap 4. On direct UDP, cap 4 stays within 0.81% of cap 8 while cap 8 uses
21.3% more CPU ticks. These paired results support the explicit recommendations above and reject cap
8 as a general setting.

The retained compact proofs are:

- `pair.t6b6exf1`: direct UDP, ascending;
- `pair.ku2fxml0`: direct UDP, descending;
- `pair.70p2plez`: forced TCP, ascending; and
- `pair.o_6q_m1n`: forced TCP, descending.

The canonical report is `artifacts/rev0045/content-lane-counterbalance.json`. See
`../evidence/2026-08-31-sandwurm-sync-content-lane-counterbalance.md`.

## Consequences

The roadmap's phase-order gate is closed. IoTox has a repeatable proof-driven way to add later
ascending/descending pairs without changing report semantics. The default remains one because a
safe ordinary device setting includes interactive behavior, route changes, and hosts outside this
construction machine—not only bulk goodput.

The next content scheduler gates are cap-2/cap-4 client-daemon restart recovery, simultaneous Ratox
measurement at cap 2 before any interactive bulk profile, and same-source auxiliary-path
distribution. An application pacing/reservation experiment is justified only if a later frozen
terminal SLA requires it. This ADR does not qualify a confidence interval, public network, physical
host pair, automatic tuning, byte striping, or a universal throughput optimum.

## Later qualification

ADR 0267 closes the cap-two/cap-four subscriber-restart gate. ADR 0268 then freezes and passes the
missing cap-two persistent-Ratox SLA over both native carriers under the same 4 Mbit/s shaping.
That result promotes explicit cap two from latency-insensitive mixed-bulk guidance to a bounded
native interactive-bulk construction profile. It does not raise default one, add automatic tuning,
or make the profile bandwidth-independent.
