# ADR 0159: Preserve file-callback pacing until explicit scheduling

Status: accepted, 2026-08-24.

## Context

ADR 0158 removed redundant Agent bookkeeping for most successful synchronous outgoing file chunks.
The exact clean-commit direct-UDP `bulk-1` A/B completed, but made terminal behavior dramatically
worse: render p50/p95/p99 became 473.704/505.064/508.521 ms, maximum 665.246 ms, and 991 of 1,000
samples reached 250 ms. Only 238,554 bytes of the 1 GiB bulk stream had become observable when the
sampling interval ended.

At the same time, the measurements disproved local event congestion on the remote host. Interactive
owner p99 fell to 0.103 ms, remote stage-to-output p95 fell to 10.759 ms, event high-water was five,
and required-event backpressure was zero. Client/device CPU usage also fell to roughly 5.3%/5.4% of
one core over 476 seconds. The regression therefore sits below the Agent's remote queue/PTY service:
unpaced reliable file traffic filled c-toxcore's shared lossless path and Ratox output waited behind
bulk carrier work.

The previous per-chunk required bookkeeping was expensive, but its bounded consumer backpressure
also paced synchronous file production. Removing it without replacing that pacing converted a local
owner-queue problem into much larger transport head-of-line blocking.

## Decision

Restore one required bookkeeping event for every synchronous outgoing chunk request, as ADR 0057
originally specified. Keep the ADR 0158 receive-descriptor optimization and the event high-water plus
required-backpressure counters.

Do not suppress, batch, or make these callbacks observational until IoTox has an explicit bounded
bulk scheduler that can pause/resume or otherwise pace c-toxcore file production while reserving
interactive headroom. Accidental event backpressure is not the desired final scheduler, but it is the
known safer behavior and remains part of the current provider contract.

The next A/B changed only the retained receive descriptor and diagnostics relative to the accepted
ADR 0157 source. It recovered direct p95 to 51.146 ms and owner p99 to 3.972 ms, but did not meet
either target. Both guests bind their final content-free Agent status into their signed receipt and
compact proof; the client reached the 1,024-event ceiling and waited 1,227 times, while the device
reached 765 without backpressure. The roadmap therefore selects explicit high/low-water bulk pacing
before the already constructed authenticated protected route.

## Consequences

- Outgoing position remains exact in the live manager and terminal completion remains unchanged.
- CPU/event work returns to the pre-ADR-0158 sender level. Runtime projection still coalesces its
  filesystem writes at 250 ms; only in-memory bookkeeping remains per callback.
- Required-event backpressure is now measured rather than inferred. This enables an explicit pacing
  design to preserve the useful rate limit without coupling it to event-queue saturation.
- The failed coalescing proof is retained because it establishes that local owner latency alone is
  not a sufficient optimization target and that Ratox/file traffic share a consequential reliable
  carrier bottleneck.
- Ratox framing, route identity, authority, replay, and file integrity are unchanged.

## Evidence

- `.sandwurm/exports/pairs/pair.bmar1y5q` strictly verifies the exact failed A/B from commit
  `1d4792fb5e325250d7109639a204642ba2680b88` with both process-resource intervals.
- The compact export is about 1.6 MiB and contains no guest disks, private keys, raw savedata,
  terminal content, file bytes, or bootstrap secret.
- `.sandwurm/exports/pairs/pair.y__zgt1p` strictly verifies the descriptor-only committed rerun from
  `b76c1f7`; its compact export is about 1.6 MiB and includes both final Agent status records.
