# ADR 0268: Freeze the cap-two interactive bulk SLA

Status: accepted, 2026-08-31

## Context

ADR 0264 proved that one Ratox attachment survives content-v2 caps one, four, and eight without a
session or Tox-epoch change, but it deliberately paused the probe during cap two. ADR 0266 later
identified explicit cap two as the efficient mixed/relay-heavy bulk recommendation. Neither result
could call cap two suitable for interactive use because no cap-two latency distribution had been
measured and no pass/fail threshold existed before measurement.

The threshold must precede the result. Otherwise a construction sample can always be declared good
after the fact. It must also remain separate from ADR 0265's fresh post-backlog OPEN deadline:
admitting a controller and keeping an already-attached raw terminal responsive are different
lifecycle claims.

## Decision

Add `sync-content-ratox-cap-2-sla` without changing Ratox, content-v2, FileId, or local-control
framing. It repeats the stable-session 8 MiB/24-chunk content workload in order `1,2,4,8`, keeps one
Ratox attachment and one authenticated Tox online epoch across all four phases, and records 240
ordered raw-echo samples per phase at 100 ms requested cadence. Every phase must begin after one
completed pre-transfer sample, genuinely overlap the content interval, converge, explicitly
activate, and preserve the exact resource-state transitions `0->1`, `1->1`, `1->1`, `1->0`.

Before running either carrier cell, freeze the cap-two construction SLA as:

- at least 40 samples whose input timestamps lie inside the exact content interval;
- nearest-rank round-trip p50 no greater than 250 ms;
- p95 no greater than 500 ms;
- p99 no greater than 1,000 ms;
- maximum no greater than 1,500 ms; and
- owner-queue p95 no greater than 10 ms.

The guest enforces those bounds after producing the canonical summary. The standalone host verifier
independently parses all 960 rows, reconstructs content overlap and every percentile, binds one
terminal session and online epoch, rechecks resource transitions and content receipts, and enforces
the same constants. A carrier-specific relaxation is forbidden.

Define the bounded native interactive-bulk construction profile as explicit effective cap two with
an already-attached Ratox session and the qualified 4 Mbit/s subscriber shaping. Keep process default
one. Do not automatically select the profile, infer a bandwidth-independent pacing policy, or expose
a new protocol/profile selector from this ADR.

## Findings

Both final-tree Sandwurm cells pass raw verification, compact export, and strict compact replay with
IoTox binary SHA-256
`531dfb224e133b3fc0735455f1a5d077c02dbf6a6c2a91b0e0d85f766321d5b6`.

| Route | Cap | Rate | Overlap | p50 | p95 | p99/max | Queue p95 | SLA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| direct UDP | 1 | 406,897 B/s | 90 | 119.233 ms | 302.428 ms | 547.939 ms | 0.159 ms | context |
| direct UDP | 2 | 418,071 B/s | 83 | 83.680 ms | 479.100 ms | 876.158 ms | 0.298 ms | pass |
| direct UDP | 4 | 422,706 B/s | 59 | 69.400 ms | 970.865 ms | 1,120.360 ms | 0.506 ms | fail p95 |
| direct UDP | 8 | 444,570 B/s | 32 | 106.303 ms | 1,836.902 ms | 1,929.880 ms | 1.311 ms | fail p95/p99/max |
| forced TCP | 1 | 365,246 B/s | 97 | 135.502 ms | 292.475 ms | 610.902 ms | 0.119 ms | context |
| forced TCP | 2 | 401,484 B/s | 68 | 199.264 ms | 401.813 ms | 531.662 ms | 0.083 ms | pass |
| forced TCP | 4 | 412,947 B/s | 62 | 220.301 ms | 523.960 ms | 696.405 ms | 0.410 ms | fail p95 |
| forced TCP | 8 | 408,861 B/s | 55 | 233.623 ms | 553.267 ms | 836.610 ms | 1.364 ms | fail p95 |

Cap two improves throughput over cap one by 2.75% on direct UDP and 9.92% on forced TCP while
meeting every frozen bound. Cap four adds only 1.11% and 2.86% over cap two in these cells while
missing the p95 ceiling on both carriers. Cap eight also misses. This makes cap two the smallest and
only nondefault tested cap that passes the cross-carrier construction SLA.

Accepted compact proofs are `pair.rpblreul` for direct UDP and `pair.rwiyixfh` for forced TCP. See
`../evidence/2026-08-31-sandwurm-sync-content-ratox-cap-2-sla.md`.

## Consequences

The roadmap's persistent-Ratox cap-two gate is closed. Operators may deliberately configure cap two
for the bounded native interactive-bulk construction profile; IoTox still starts at cap one and does
not tune itself. Cap four remains a controlled direct-UDP throughput option only when interactive
latency is not the governing objective. Cap eight remains stress-only.

This decision does not promise Internet or physical-host latency, an unshaped or faster-link SLA,
mobile behavior, routed Tor/I2P latency, multiple simultaneous terminals, local echo, fresh OPEN
admission during active bulk, arbitrary payload distributions, confidence intervals, or long-running
tail stability. Those remain independent work. The next content scheduler gate is same-source object
distribution across independently authenticated auxiliary paths.
