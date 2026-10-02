# c-toxcore 0.2.23 Ratox pacing laboratory — rev0015

Date: 2026-08-15. Status: founding-host controlled-path evidence, not PTY, cross-client, or
two-physical-host qualification.

## Question

What emission/coalescing interval keeps paced custom-lossless Ratox traffic below c-toxcore
admission collapse while a bulk transfer occupies the same Tox route? Does the answer change for
small input-like packets versus the complete proposed frame ceiling, or for direct UDP versus a TCP
relay?

## Method

`tools/run-ratox-pacing-lab.sh` ran 20 independent cells: 2, 5, 10, 20, and 40 ms spacing crossed
with 64-byte and 1,200-byte size-symmetric diagnostic packets over observed direct UDP and forced
TCP. Every cell reused the two-private-namespace adversity profile: 40 ms delay with 10 ms normal
jitter, 2% random loss, 0.5% duplication, 5% reorder with 50% correlation, and netem limit 256 on
each endpoint namespace's `eth0` only. Identical netem seeds 151517/151518 were reapplied per cell.

Each idle and bulk state sent 64 lossless and 64 lossy probes with a 2.5 second final-response
window. The table below reports the Ratox-selected lossless bulk lane. `ok/local/path` partitions
all 64 attempts: local is a c-toxcore SENDQ rejection, while path means admitted but not echoed by
the deadline. Times are per-packet milliseconds. A 16 MiB exact transfer kept UDP bulk active for
the whole probe pair; TCP used 8 MiB and was already relay/impairment limited.

The TCP path necessarily includes a changing public relay outside the namespace boundary. Its
sequential cells are observations of complete relay epochs, not a controlled causal comparison of
spacing alone. That limitation is itself relevant to the product policy.

## Lossless bulk result

| Path | Packet bytes | Spacing ms | ok/local/path | median ms | p95 ms |
|---|---:|---:|---:|---:|---:|
| UDP | 64 | 2 | 30/34/0 | 188.8 | 224.9 |
| UDP | 64 | 5 | 41/0/23 | 243.3 | 393.4 |
| UDP | 64 | 10 | 62/0/2 | 249.5 | 407.1 |
| UDP | 64 | 20 | 64/0/0 | 217.1 | 401.9 |
| UDP | 64 | 40 | 64/0/0 | 180.1 | 319.4 |
| UDP | 1,200 | 2 | 26/38/0 | 250.0 | 269.2 |
| UDP | 1,200 | 5 | 51/10/3 | 259.1 | 356.3 |
| UDP | 1,200 | 10 | 56/0/8 | 248.0 | 347.4 |
| UDP | 1,200 | 20 | 64/0/0 | 173.1 | 340.6 |
| UDP | 1,200 | 40 | 64/0/0 | 189.8 | 362.9 |
| TCP | 64 | 2 | 27/37/0 | 282.2 | 336.9 |
| TCP | 64 | 5 | 5/59/0 | 712.7 | 844.8 |
| TCP | 64 | 10 | 64/0/0 | 521.7 | 674.8 |
| TCP | 64 | 20 | 64/0/0 | 488.3 | 585.6 |
| TCP | 64 | 40 | 51/13/0 | 746.9 | 884.6 |
| TCP | 1,200 | 2 | 29/35/0 | 306.1 | 368.1 |
| TCP | 1,200 | 5 | 50/14/0 | 399.1 | 430.2 |
| TCP | 1,200 | 10 | 64/0/0 | 491.3 | 538.1 |
| TCP | 1,200 | 20 | 64/0/0 | 563.4 | 712.6 |
| TCP | 1,200 | 40 | 64/0/0 | 427.3 | 617.5 |

All 20 finite-file phases completed byte-identically with zero dropped IoTox events. The gate moved
240 MiB of exact payload. Bulk throughput ranged from 45,120 to 493,418 bytes/s. The maximum
observed owner interactive queue wait was 3,166 microseconds; the admission failures therefore
remain at or below toxcore/path pressure rather than an unbounded IoTox FIFO.

## Decision supported by the result

Twenty milliseconds is the smallest tested spacing that admitted and returned all 64 lossless
packets for both packet sizes on controlled direct UDP. Forty milliseconds added no direct-route
reliability and consumes avoidable interactive latency. Packet count was the dominant pressure:
the 64-byte and 1,200-byte thresholds matched even though their byte rates differed greatly.

Twenty milliseconds was also the only interval whose four UDP/TCP and 64/1,200-byte cells were all
clean. It is not a relay guarantee. TCP was non-monotonic across external epochs: the 5 ms/64-byte
cell admitted only 5 packets, 10 and 20 ms admitted all, then the 40 ms cell admitted 51. A fixed
sleep cannot defeat relay head-of-line blocking or changing shared bulk pressure.

Ratox therefore starts at a 20 ms coalescing interval and reacts to actual admission evidence:

- one whole offered frame remains owned until c-toxcore accepts it;
- SENDQ rejection advances no sequence and discards no bytes;
- rejection doubles the interval through 40/80/160 to a 320 ms ceiling;
- eight consecutive accepted frames halve a backed-off interval toward 20 ms;
- an empty queue resets to 20 ms; and
- a full 1,076-byte Ratox payload still waits for its interval, preventing accidental bursts.

This is a correctness boundary, not the final latency claim. A local PTY gate must measure actual
keypress-to-render latency and ACK progress. If TCP relay remains outside budget beside the later
1/8/16/32/64 coexistence sweep, smaller/coalesced output or a separately authenticated Tox route is
the remaining isolation lever.

## Exact retained evidence

The outer manifest and all 20 nested manifests/reports are under
`docs/evidence/2026-08-15-ratox-pacing/`. Every nested hash was independently rechecked after the
copy, all nested manifests end in `matrix pass`, and cleanup left no generated namespace,
interface, or NAT rule.

```text
provider=c-toxcore-0.2.23 source-linked
science-binary-sha256=0b6117906db5260d97e6df48d09035beeaa9c6e7fd57a50f4decdc1875bede69
pacing-manifest-sha256=81bc41a5cac93e8b242353fea2ef0292d987c2468a2e1e633648e4d4299773b0
matrix-run-id=20260815T223446Z-37099
host-kernel=Linux 6.12.34 x86_64
host-physical-qdisc-touched=no
```

The science binary includes the sized-probe instrument and precedes the subsequently frozen Ratox
frame codec in the same work sequence. It carries no private identity material; reports contain
only public-key hashes. Reusable test identities remain in the ignored private cache.
