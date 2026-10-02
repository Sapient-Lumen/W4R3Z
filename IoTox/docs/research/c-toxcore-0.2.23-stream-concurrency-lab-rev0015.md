# c-toxcore 0.2.23 stream-concurrency laboratory — rev0015

Date: 2026-08-15. Status: founding-host capacity evidence, not a bonded-transport specification.

## Question and fixture

How do 8, 16, 32, and 64 simultaneous Tox file streams behave, and does distributing the same
stream population over four independent connections escape a limit seen on one connection?

For each stream total, the laboratory transfers a constant 16,777,216 bytes through both:

```text
1 independent Tox route x N files
4 independent Tox routes x N/4 files per route
```

It repeats every topology three times with reversed and alternating order. Eight source-linked
IoTox processes represent four routes between two logical device identities. Every destination is
compared byte-for-byte, required transport events are counted, and the report is published only
after clean shutdown. The UDP run requires all eight peer directions to report UDP. The TCP run
uses `--native-tcp-only` and requires all eight to report TCP. No fallback result is mislabeled.

IoTox normally admits 32 active sends and 32 active receives per agent. The laboratory explicitly
sets both limits to 64 so that it can measure the requested range without changing the product
default. c-toxcore 0.2.23 has 256 send and 256 receive file-pipe slots per friend. The experiment did
not attempt to qualify that hard provider boundary.

End-to-end time begins before file offers are created. The separately reported data window begins
after every remote offer is visible and includes destination admission plus transfer. Offer setup
and receive admission are also reported separately. This makes both user-visible cost and carrier
capacity inspectable.

## Limit discovered and removed before qualification

The first 64-stream UDP shakedown moved only 1 MiB but took 71.018 seconds on one route and 11.750
seconds on four. The one-route phase spent 39.218 seconds creating offers and 30.075 seconds
admitting destinations, consumed 9,719 CPU ticks, and performed 21.0 MB of process-visible writes.

The cause was IoTox, not Tox: every admission and terminal event atomically rewrote every live
transfer record in both runtime layouts. The growing and shrinking sets produced quadratic work.
ADR 0058 caches exact successfully projected records, skips unchanged real directories, and still
atomically publishes changed records and removes terminal ones. The same 1 MiB comparison became:

| Topology | Before | After | CPU ticks before/after | Offer setup after | Admission after |
|---|---:|---:|---:|---:|---:|
| 1 route / 64 streams | 71.018 s | 6.184 s | 9,719 / 549 | 3.397 s | 1.621 s |
| 4 routes / 64 streams | 11.750 s | 4.025 s | 4,389 / 762 | 1.390 s | 1.398 s |

One earlier 32-stream attempt also timed out one of several simultaneous local control clients while
the server serialized those expensive projections. The final harness admits at most one local
client per route at once. That isolates Tox concurrency; it does not serialize the active file set.

## Replicated direct-UDP result

All 24 phases completed byte-identically with zero dropped events.

| Total streams | 1-route elapsed | 1-route data MB/s | 4-route elapsed | 4-route data MB/s | Data-window speedup |
|---:|---:|---:|---:|---:|---:|
| 8 | 7.326 s | 2.341 | 4.892 s | 3.537 | 1.51x |
| 16 | 7.790 s | 2.268 | 4.911 s | 3.612 | 1.59x |
| 32 | 7.746 s | 2.399 | 5.338 s | 3.590 | 1.49x |
| 64 | 8.452 s | 2.340 | 5.752 s | 3.558 | 1.52x |

## Replicated TCP-only result

All 24 phases completed byte-identically with zero dropped events. One single-route 16-stream trial
took 26.913 seconds while its other two took 14.153 and 14.471 seconds; the table reports medians
and retains that relay-path tail in the raw evidence.

| Total streams | 1-route elapsed | 1-route data MB/s | 4-route elapsed | 4-route data MB/s | Data-window speedup |
|---:|---:|---:|---:|---:|---:|
| 8 | 14.145 s | 1.211 | 9.684 s | 1.787 | 1.47x |
| 16 | 14.471 s | 1.197 | 9.499 s | 1.852 | 1.54x |
| 32 | 14.734 s | 1.195 | 9.630 s | 1.864 | 1.56x |
| 64 | 15.291 s | 1.229 | 10.080 s | 1.863 | 1.51x |

## Interpretation: the useful limit is not stream count

Within each transport mode, one connection's aggregate payload rate is essentially flat from 8
through 64 streams. Adding files does not buy bandwidth. Four independent connections sustain
about 3.54–3.61 MB/s over direct UDP and 1.79–1.86 MB/s over TCP relays, while one connection
sustains about 2.27–2.40 MB/s and 1.20–1.23 MB/s respectively. Four routes therefore preserve an
approximately 1.5x aggregate advantage throughout the full requested range.

There is no c-toxcore file-transfer failure or event loss through 64 streams after removing local
projection amplification. The practical knee is earlier: more streams add offer, admission, file
descriptor, projection, and completion overhead without increasing one connection's carrier rate.
For a bonded prototype, a small number of disjoint ranges—initially one active range per route—is a
better starting point than 64 tiny stripes.

TCP-only capacity on this run is roughly half direct UDP capacity and has a heavier tail because it
depends on relay paths. Four routes improve both aggregate rate and exposure to a single route's
slow episode. This is still one-host evidence: shared kernel, storage, scheduler, Internet path,
and public relay selection remain confounders. The next performance gate is the same sweep across
two physical hosts and controlled local/private relays.

## Exact evidence identity

```text
base-repository-commit=8d03c1cc2449334fc7aba11f733d2d5b3d4622c7
harness-sha256=0a48dc2b21345c4db4cb31042a008632ca8e029eba7ad73a3764d6b1fe226ab0
standalone-binary-sha256=e8d0c7ee13ed44b447b3653a61ba24cd5c3b156dde4e8bab99be940cb2c94ffb
udp-report-sha256=6369566fd1ccda77c949e588c71e614151c6c5258d0d5013cb87175164c05d18
tcp-report-sha256=c7ebad6e6857667d0a5ec41083116ce7998193337b1c2b1629d67b0b1087904a
provider=c-toxcore-0.2.23 source-linked
host-kernel=Linux 6.12.34 x86_64
host-logical-cpus=12
clock-ticks-per-second=100
```

The exact run necessarily used uncommitted product and harness changes; hashes identify the
executed artifacts. The two files under `docs/evidence/` are exact retained copies of the redacted
atomic reports. Test identities remain private and ignored.
