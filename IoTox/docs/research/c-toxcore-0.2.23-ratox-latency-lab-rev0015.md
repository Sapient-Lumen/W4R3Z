# c-toxcore 0.2.23 Ratox carrier latency laboratory — rev0015

Date: 2026-08-15 America/New_York
Host: founding bare-metal Linux host
Provider: pinned source-linked c-toxcore 0.2.23
Scope: same-client/same-host carrier isolation; not terminal, two-host, cross-client, or impaired-link qualification

## Question

Which existing Tox carrier should Ratox-first latency work use, and is local toxcore owner admission
the current bottleneck?

The experiment compares:

```text
ordinary normal text -> remote Tox observation -> local read-receipt callback
10-byte custom-lossless request -> confirmed peer 10-byte echo
10-byte custom-lossy request -> confirmed peer 10-byte echo
```

Each measurement starts in the daemon immediately before local transport admission and ends on its
monotonic callback. It includes both IoTox processes and the Tox path. It does not include local
keypress capture, PTY service, terminal emulation, or rendering.

## Construction required for the gate

- Added official c-toxcore custom-lossy send and callback symbols to the linked/runtime ABI table.
- Added fixed diagnostic IDs `0xA1` (lossless) and `0xC8` (lossy application range), request/reply
  kind, and random nonzero nonce. Echo is fixed-size, confirmed-session-only, and unadvertised.
- Added interactive/control/bulk owner queues with an 8:4:1 schedule and a 16-command iteration
  bound. File chunks are bulk; human/diagnostic interaction is interactive.
- Added a configurable maximum toxcore owner sleep, 20 ms by default, plus requested/effective
  interval, iteration, queue, CPU, and context-switch evidence.
- Added attachment fencing, bounded cumulative byte replay, and monotonic RTT estimation as
  transport-independent prerequisites. They are not wired or advertised.
- Extended the reusable-key four-route laboratory to verify all eight route directions, sample
  idle and one active 64 MiB transfer, and report a miss when a custom reply exceeds the deadline.

The normal mode required all routes to report direct UDP. TCP-only mode disabled UDP, local
discovery, DHT announcements, and hole punching and required all routes to report TCP.

## Corrected full gate

Forty attempts per carrier/state used a 20 ms maximum owner interval and nominal 250 ms custom
deadline. A timestamp bug found during the first full run waited for the latency observer before
freezing transfer elapsed time. The harness was repaired to freeze timestamp/counters when the last
payload arrived, then wait for the observer. The following is the corrected rerun.

### Observed direct UDP

| Carrier/state | Success/miss | median | p95 | p99/max |
|---|---:|---:|---:|---:|
| text idle | 40/0 | 83.084 ms | 984.762 ms | 1,001.474 ms |
| lossless idle | 40/0 | 20.532 ms | 24.755 ms | 40.595 ms |
| lossy idle | 40/0 | 20.545 ms | 26.052 ms | 43.936 ms |
| text + bulk | 40/0 | 31.180 ms | 63.828 ms | 76.838 ms |
| lossless + bulk | 40/0 | 11.960 ms | 30.748 ms | 39.412 ms |
| lossy + bulk | 40/0 | 12.484 ms | 26.030 ms | 32.574 ms |

The 64 MiB payload arrived in 10.434 s (last completion 10.419 s), 6.43 MB/s end-to-end. No
transport events were reported dropped. Sender maximum owner-queue wait was 5.632 ms interactive
and 13 us bulk. The idle window consumed 462 CPU ticks and 8,868 context switches across eight
agents over 21.881 s, with 8,915 toxcore iterations.

### Forced TCP-only

| Carrier/state | Success/miss | median of successes | p95 | max success |
|---|---:|---:|---:|---:|
| text idle | 40/0 | 223.849 ms | 262.333 ms | 342.149 ms |
| lossless idle | 38/2 | 201.413 ms | 221.433 ms | 223.300 ms |
| lossy idle | 16/24 | 201.676 ms | 241.850 ms | 241.850 ms |
| text + bulk | 40/0 | 273.925 ms | 342.658 ms | 1,063.051 ms |
| lossless + bulk | 29/11 | 201.565 ms | 215.470 ms | 238.011 ms |
| lossy + bulk | 24/16 | 209.232 ms | 247.320 ms | 249.059 ms |

The 64 MiB payload arrived in 20.427 s (last completion 20.415 s), 3.29 MB/s end-to-end. No
transport events were reported dropped. Sender maximum owner-queue wait was 793 us interactive and
56 us bulk. c-toxcore requested 50 ms at the final sample and IoTox applied 20 ms. The idle window
consumed 549 CPU ticks and 11,973 context switches across eight agents over 29.667 s, with 12,040
toxcore iterations.

### No-extra-cap control

A smaller 10-attempt/8 MiB control set `--max-iterate-ms 1000`. This does not force one second;
c-toxcore can request less. Direct-UDP custom idle medians were 50.556 ms lossless and 50.660 ms
lossy. Forced-TCP custom-lossless idle median was 250.889 ms; lossy met the nominal deadline on only
4/10 attempts. At the final TCP sample c-toxcore requested/effectively used 50 ms.

The control differs in sample count, payload, time, and public relay path, so it is directional
evidence rather than an isolated causal estimate. It supports retaining the 20 ms cap, not claiming
one universal percentage improvement.

## Findings

1. The ordinary text/read-receipt path is not a terminal carrier. Its direct-UDP p95 was almost one
   second while both custom carriers remained below 44 ms.
2. Custom lossless is the Ratox-first sweet spot. On direct UDP its latency was effectively tied
   with lossy, with no misses and no duplicate/reorder/loss burden.
3. Lossy remains valuable research for replaceable future screen state, but this gate found no
   direct-route advantage and materially more forced-TCP deadline misses.
4. The local owner queue is not the dominant tail. Its worst observed wait was 5.632 ms while text
   or forced-TCP delays were hundreds of milliseconds.
5. A bounded owner wake interval matters, especially on idle/relay paths, and the measured idle
   iteration/counter cost did not form a busy loop. It remains a configurable power/latency trade.
6. Bulk traffic changes toxcore/path cadence. It improved direct-UDP probe medians in this run but
   degraded forced-TCP deadline completion. A separate authenticated route may ultimately be needed
   for latency isolation, but the current data does not authorize bonding or route multiplication.

## Evidence files

Corrected full gate:

```text
UDP  ../evidence/2026-08-15-ratox-latency-udp.tsv
     SHA-256 4deb7a0f3a3fd958e49aa22bad0bb46ac1f18eae8bdc0b719227cbee4b89b689
TCP  ../evidence/2026-08-15-ratox-latency-tcp.tsv
     SHA-256 dd123269c150e7fe66a48af468538cfcc8ae9266418c77e617e930ecb0d7cc59
```

No-extra-cap control:

```text
UDP  SHA-256 f57943c97943727ba1a6b19a55680eb3806def89fbe05afa314d3c8dfdbfea46
TCP  SHA-256 09c30d24a73c60214d67b610c12aa728e12104595d14d1fcfc12d0e22d57a8d7
```

The full gate's client-to-daemon timeout calculation gave the daemon 251 ms while the report named
250 ms; all recorded successes were below 250 ms, so classifications above are unchanged. The
formula was immediately corrected to map the configured deadline exactly for future runs.

## Remaining boundary and next gate

This host does not provide controlled loss, duplication, reorder, delay, bandwidth, NAT, roaming,
or independent clocks. Carriers were sampled sequentially, so each can perturb subsequent toxcore
cadence. TCP used whatever public relay/path the fixture acquired and changed between runs.

The next scientific gate is controlled network impairment with isolated and randomized carrier
order. It must measure lossless head-of-line delay, lossy duplication/reorder/loss, adaptive RTO,
and application-level replaceable state. Only then may a protocol ADR decide whether any terminal
state belongs on lossy packets. The Ratox-first implementation proceeds on custom lossless.
