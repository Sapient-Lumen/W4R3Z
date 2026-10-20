# ADR 0264: Qualify persistent Ratox under content lane load

Status: accepted, 2026-08-30

## Context

ADR 0263 found useful same-source content-v2 throughput through four lanes, especially over
relay-only TCP, but deliberately did not measure a competing interactive terminal. A bulk profile
that improves completion time while making a future Eternal Terminal/Mosh-style session feel stuck
is not an IoTox improvement.

The first harness design opened a new Ratox session for each measured lane cap. Cap 1 and the cap-2
transfer-only control completed, but later OPEN attempts could remain behind the reliable-carrier
backlog. That confounded two different questions: whether an attached terminal survives bulk work,
and whether a new terminal can be admitted after bulk work. The reconnectable-session product
contract makes the first question primary. Fresh post-bulk admission remains independently useful
and must not be hidden by retries or a longer unmeasured deadline.

## Decision

Add the source-linked Sandwurm scenario `sync-content-ratox-latency-science` without changing Ratox
or content-v2 peer framing. It extends the fixed-order ADR 0263 experiment as follows:

- one client Agent, one authenticated Tox session, and one Ratox attachment remain live throughout;
- one 720-sample keypress-to-render timeline runs at 100 ms requested cadence and pauses after
  samples 240 and 480;
- cap 1 uses samples 1--240, cap 4 uses 241--480, and cap 8 uses 481--720; the existing cap-2
  transfer runs while the probe is deliberately paused as a transfer-only control;
- every measured phase requires three stable capability, authority, carrier, and online-epoch
  observations, plus one completed pre-transfer terminal sample;
- every phase transfers and explicitly activates the same deterministic high-entropy 8 MiB,
  24-chunk, 26-object graph under the existing 4 Mbit/s subscriber shaping;
- the evidence binds the exact content interval, overlapping terminal rows, nearest-rank
  p50/p95/p99/max round-trip latency, owner-queue p95/max, live-lane maximum, phase-transition delay,
  one terminal-session commitment, one timeline digest, and one Tox online epoch; and
- resource intervals must show the exact Ratox-active boundary sequence `0->1`, `1->1`, `1->1`,
  `1->0` over content caps 1, 2, 4, and 8.

The standalone verifier independently reconstructs every percentile and digest from the retained
timeline and metadata. It rejects fewer than 20 genuinely overlapping samples, a session or epoch
change, a missing pre-transfer sample, a carrier mismatch, a lane maximum above policy, resource
state-machine drift, or any receipt/inventory disagreement.

Keep `--max-sync-content-lanes` defaulted to one. Do not automatically select cap 4 or cap 8 from
this one fixed-order observation. Ratox v1 framing remains frozen.

## Findings

Both direct UDP and forced TCP pass raw and compact verification:

| Route | Cap | Content rate | Ratox p50 | Ratox p95 | Ratox p99 | Maximum | Queue p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct UDP | 1 | 385,683 B/s | 127.555 ms | 258.241 ms | 1,084.973 ms | 1,084.973 ms | 0.069 ms |
| direct UDP | 4 | 440,555 B/s | 53.522 ms | 815.429 ms | 1,035.088 ms | 1,035.088 ms | 0.097 ms |
| direct UDP | 8 | 374,090 B/s | 26.560 ms | 880.790 ms | 2,029.456 ms | 2,029.456 ms | 0.074 ms |
| forced TCP | 1 | 259,942 B/s | 171.052 ms | 412.735 ms | 835.052 ms | 1,245.082 ms | 3.069 ms |
| forced TCP | 4 | 418,050 B/s | 231.526 ms | 525.400 ms | 562.955 ms | 562.955 ms | 1.226 ms |
| forced TCP | 8 | 397,866 B/s | 256.879 ms | 739.272 ms | 784.838 ms | 784.838 ms | 1.102 ms |

Among phases with simultaneous Ratox, cap 4 is the smallest throughput winner in both accepted
cells: +14.2% over cap 1 on direct UDP and +60.8% on forced TCP. Cap 8 then regresses 15.1% and
4.8% against cap 4, respectively. Tail latency also worsens from cap 4 to cap 8 on both routes. The
fixed phase order, single run, busy construction host, and cap-1 warm-up position prevent a causal
or distributional claim. Cap 2 has no simultaneous terminal measurement and cannot select an
interactive bulk profile.

Owner-queue p95 remains far below end-to-end p95 in every cell. This localizes the dominant observed
tail beyond owner command scheduling, but does not by itself distinguish toxcore reliable-channel
head-of-line blocking, file-transfer scheduling, kernel/network queueing, or host contention.

Accepted compact proofs are `pair.af873531` for direct UDP and `pair.a3nglkh3` for forced TCP. See
`../evidence/2026-08-30-sandwurm-sync-content-ratox-latency.md`.

## Consequences

IoTox now proves that one authenticated Ratox attachment survives the complete content cap sequence
without session replacement, epoch change, daemon restart, framing change, or loss of exact terminal
bytes. This is the right construction prerequisite for a reconnectable terminal.

The evidence does not establish an interactive SLA. Default one remains the safe general setting;
cap 4 is only an explicit bulk-profile candidate. Cap 8 is not a latency-sensitive default
candidate on the accepted evidence.

Next gates are:

1. repeat lane phases in counterbalanced orders and report distributions rather than one sample;
2. qualify fresh Ratox OPEN admission and bounded recovery after reliable bulk backlog;
3. test an application-level content pacing/reservation policy if repeated cells preserve the
   observed tail, keeping reliable terminal/control work ahead of optional bulk progress; and
4. qualify multi-lane content recovery across client-daemon restart separately.

## Later qualification

ADRs 0265--0267 close fresh post-bulk OPEN, phase-order/bulk-policy, and multi-lane restart as
separate gates. ADR 0268 then measures cap two with Ratox continuously active and freezes the
threshold before either carrier run. Explicit cap two passes that bounded direct-UDP/forced-TCP
construction SLA under the same 4 Mbit/s shaping; no pacing experiment is required by the accepted
result. This later evidence does not rewrite this ADR's historical cap-1/4/8 observation.
