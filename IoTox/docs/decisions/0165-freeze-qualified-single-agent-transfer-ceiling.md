# ADR 0165: Freeze the qualified single-Agent transfer ceiling

Status: accepted from the complete 8/16/32/64 two-route matrix, 2026-08-25.

## Context

ADRs 0163 and 0164 make accepted incoming files fair on one Tox friendship: one receive is runnable,
waiting transfers rotate oldest-first every 50 ms, pause ownership is explicit, and cancellation
fallout is bounded. Exact 1,000-sample Sandwurm cells pass both direct UDP and forced TCP at 8, 16,
and 32 simultaneous transfers. Every file progresses, every lifecycle closes, owner p99 stays below
2 ms, direct p95 stays below 50 ms, and neither route records a 250 ms render.

The explicit 64-transfer opt-in completes semantics but fails performance on both routes:

- direct proof `pair.t736zqqh` advances all 64 files and keeps owner p99 at 0.118 ms, yet render
  p50/p95/p99 is 220.897/331.081/446.692 ms with 108 renders at or above 250 ms. Event high-water is
  only 50/50, CPU is low, reactive pacing never activates, and aggregate file progress collapses to
  1,549,230 bytes over a 242-second interval;
- forced proof `pair.swij6mj9` advances all 64 files by 168,951,072 aggregate bytes, but client event
  high-water reaches 711, owner p99 is 2.199 ms, and one render reaches 560.528 ms. Reactive pacing
  activates strongly and CPU remains busy.

The two route classes therefore reject the same accepted-transfer population through different
observable mechanisms. More Agent queue capacity would not repair the direct low-utilization case;
less file work would not by itself explain the forced route's high-pressure case. Ratox v1 framing,
the owner queue, PTY execution, and local rendering are not the common bottleneck.

IoTox already defaults both `max_active_sends` and `max_active_receives` to 32. An incoming offer is
kept paused until `receive_to_path()` safely admits it; when the accepted-receive limit is full, the
operation returns typed `resource_exhausted` without silently accepting or dropping the offer.

## Decision

Thirty-two accepted outgoing and 32 accepted incoming transfers are the qualified ceiling for one
IoTox Agent/Tox instance. Values above 32 remain explicit experimental controls for construction and
future A/B work; command help labels them experimental. They are not release-qualified capacity.

Excess work stays outside the accepted-transfer population until capacity exists. The current
paused-offer plus typed `resource_exhausted` boundary is preserved. A higher-level sync or route
scheduler may retry bounded work later, but must preserve immutable object/attempt identity and may
not silently drop, duplicate, or reroute an in-flight Tox transfer.

Multiple independently authenticated route workers remain the mechanism for additional aggregate
capacity. Each route retains its own qualified headroom and Ratox is never moved implicitly. This ADR
does not infer physical-host capacity from two local VMs and does not turn the earlier four-route
construction cells into release qualification.

The frozen R7 64-stream gate is not weakened or removed after observing its failure. The complete
matrix is measured, but R7 remains unqualified at 64 accepted transfers. A future change must use a
new ADR and clean direct-UDP plus forced-TCP A/B evidence; it may not relabel lifecycle verification
as latency qualification.

## Consequences

- 8, 16, and 32 are qualified single-Agent load points on both route classes; 64 is a measured
  rejected point on both.
- Ordinary defaults already enforce the evidence-backed boundary. No wire/framing change or queue
  enlargement is selected.
- Operators can still reproduce the 64-stream science by explicitly raising both active-transfer
  limits, with the CLI making its experimental status visible.
- Work above the ceiling becomes an admission/scheduling problem, not a reason to keep more live Tox
  transfer state inside one Agent.
- A future excess-work scheduler needs its own crash, retry, fairness, cancellation, and two-route
  gates before it can claim 64 total queued objects with at most 32 accepted concurrently.

## Evidence

The accepted 32-stream direct/forced proofs are `pair.ktcwivx_` and `pair.lanpv3u7`. The rejected
64-stream direct/forced proofs are `pair.t736zqqh` and `pair.swij6mj9`. All four compact artifacts
independently pass exact route, lifecycle, provenance, counter, and content-free verification. The
canonical measurements and digest bindings are recorded in
`docs/evidence/2026-08-24-sandwurm-ratox-matrix.md`.
