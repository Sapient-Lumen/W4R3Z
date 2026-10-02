# ADR 0263: Measure same-source content lane scaling

Status: accepted, 2026-08-30

## Context

ADR 0262 proved that two independently digest-addressed content objects can overlap safely on one
authenticated Tox session, but deliberately made no throughput claim. Raising the process cap based
only on scheduler correctness would trade memory, descriptors, transfer state, and interactive
latency for an unmeasured benefit. Direct UDP and relay-only TCP may also have different useful
ceilings.

A lane-count experiment must not measure daemon restart or reconnection time. It must hold the
artifact, source, live process, Tox session, shaping, object graph, and activation rules constant
while changing only an authority-bound effective lane ceiling.

## Decision

Keep the ordinary process default at one content lane. Add the source-linked Sandwurm scenario
`sync-content-lane-science` with these frozen cells:

- one deterministic high-entropy 8 MiB content-v2 artifact, producing 24 chunks and 26 objects;
- one stable subscriber process with `--max-sync-content-lanes 8` and no daemon restart between
  cells;
- four isolated namespace/CAS roots whose signed `maximum-lanes` and
  `maximum-outstanding-requests` values are exactly `1`, `2`, `4`, and `8`;
- one authenticated publisher and one stable Tox session;
- the existing 4 Mbit/s subscriber bottleneck in both direct-UDP and forced-TCP route modes;
- fixed phase order `1,2,4,8`;
- exact live-lane attribution, convergence, explicit activation, duration, artifact bytes/second,
  fresh-process CPU ticks, resident high-water mark, and transport iterations for every cell; and
- strict offline verification and compact export without content, paths, keys, or private disks.

The verifier must accept a coherent observed maximum below the requested signed cap. Failure to
reach a cap is a scientific observation, not automatically a protocol failure. It must still reject
zero lanes, a maximum above the signed cap, malformed attribution, incomplete convergence,
activation failure, or receipt/digest disagreement.

Do not change content-v2 peer framing, feature bit 29, CTA1, FileId attribution, signed HEADs,
activation, source authority, or the default lane cap.

## Findings

Both route cells reached all four signed caps and passed independent replay:

| Route | Cap 1 | Cap 2 | Cap 4 | Cap 8 | Best observed cell |
| --- | ---: | ---: | ---: | ---: | --- |
| direct UDP | 378,035 B/s | 325,771 B/s | 399,838 B/s | 443,138 B/s | cap 8, +17.2% vs cap 1 |
| forced TCP | 301,423 B/s | 375,833 B/s | 420,481 B/s | 415,072 B/s | cap 4, +39.5% vs cap 1 |

Direct UDP is non-monotonic: cap 2 regressed 13.8%, cap 4 improved 5.8%, and cap 8 improved 17.2%
against cap 1. Forced TCP scales through cap 4, then cap 8 regresses 1.3% against cap 4. The data
therefore identify cap 4 as the smallest promising relay-heavy bulk setting, not a new universal
default. One ordered sample per cell is insufficient to estimate variance, rule out warm-cache or
phase-order effects, or claim cap 8 is useful on direct UDP.

Accepted compact proofs are `pair.amcrp0_3` for direct UDP and `pair.805kzu4a` for forced TCP. See
`../evidence/2026-08-30-sandwurm-sync-content-lane-science.md`.

## Consequences

IoTox now has a reproducible route-by-lane measurement gate and evidence that object concurrency can
recover meaningful forced-TCP goodput without changing framing. The conservative default remains
one. Cap 4 is a candidate for an explicit bulk profile only after repeated, counterbalanced trials
and the competing Ratox-latency gate show that it does not harm interactive traffic.

The next experiment should compare caps 1 and 4, with cap 8 retained as a stress bound, while a
Ratox terminal shares the same shaped session. It must report content goodput plus terminal
p50/p95/p99/max latency and tail stalls. Multi-lane daemon-restart recovery and same-source
distribution across authenticated auxiliary carriers remain separate gates.
