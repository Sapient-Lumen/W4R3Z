# Sandwurm Ratox matrix evidence, 2026-08-24

## Scope

These are content-free two-guest observations from the sole-machine Sandwurm laboratory. Each cell
uses the source-linked production binary in two distinct NixOS/Cloud Hypervisor guests, reused
immutable private identities, an ephemeral pinned c-toxcore 0.2.23 bootstrap/relay fixture, 1,000
serialized one-byte INPUT/output/render trials, exact remote stage/commit/output joins, and complete
client/device process-resource intervals. Strict proof verification establishes receipt shape and
digests; it does not turn a failed latency threshold into a pass.

## Accepted idle observations

| Route | Proof | Render p50 | p95 | p99 | Maximum | Owner p99 | >=250 ms |
|---|---|---:|---:|---:|---:|---:|---:|
| direct UDP | `pair.__2xivp6` | 16.345 ms | 23.943 ms | 31.308 ms | 52.402 ms | 0.136 ms | 0 |
| forced TCP | `pair.hg_asq62` | 88.810 ms | 99.010 ms | 128.852 ms | 131.091 ms | 0.077 ms | 0 |

Direct UDP remote stage-to-output p50/p95/p99 was 8.613/12.764/16.612 ms. Forced TCP was
8.626/11.515/13.960 ms. The near-equal remote distributions, beside a 72 ms controller median
difference, mean forced-TCP idle behavior is a separate route class; it is not remote Ratox owner or
PTY congestion.

The direct cell observed 20.366 seconds, 31.57% of one client CPU and 31.87% of one device CPU,
stable descriptor counts, and under 0.4 MiB resident growth per role. The forced-TCP cell observed
about 87 seconds and 9.13%/9.83% of one CPU. These are process observations, not quotas or energy
measurements.

The compact export manifests have SHA-256
`3e7305c2daca3457258129cbf225c33efe2c751b3f3e09e73ecb5c985b4e8880` (UDP) and
`667fc58b65fe63ed62e658627e246c9f9924205c00e24a408721144525a2e51b` (TCP).

## First loaded cell after ADR 0157

Source commit: `731fdfb53fcc3fc9f74fc2f8e33387a62836caf9`  
Proof: `.sandwurm/exports/pairs/pair.1cfwnkj6`  
Scenario: direct UDP, `ratox-matrix-bulk-1`  
Binary SHA-256: `dd2bb4ac9869575c61af1788c73699cb97e3920a6a3ce69076be700a4f37a17e`

The cell ran one simultaneous 1 GiB finite transfer per role. Both progressed, terminal sampling
completed 1,000/1,000, cancellation reached empty in one round, terminal close completed, both
resource intervals were present, and raw plus compact strict verification passed.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 6.348 ms | 27.617 ms | 71.698 ms | 96.588 ms | 220.327 ms | 32.287 ms |
| keypress to controller OUTPUT | 6.313 ms | 27.391 ms | 71.542 ms | 96.530 ms | 220.137 ms | 32.063 ms |
| local OUTPUT to render | 0.032 ms | 0.081 ms | 1.001 ms | 2.207 ms | 5.696 ms | 0.224 ms |
| interactive owner wait | 0.002 ms | 0.019 ms | 2.888 ms | 7.114 ms | 19.074 ms | 0.566 ms |
| remote stage to commit | 0.459 ms | 2.203 ms | 4.277 ms | 5.586 ms | 22.402 ms | 2.331 ms |
| remote commit to output | 0.008 ms | 4.630 ms | 12.407 ms | 16.261 ms | 47.215 ms | 4.640 ms |
| remote stage to output | 0.470 ms | 6.599 ms | 15.654 ms | 19.735 ms | 50.223 ms | 6.970 ms |

There were 130 renders at or above 50 ms, seven at or above 100 ms, and zero at or above 250 ms.
The formal cell fails because direct-UDP p95 exceeds 50 ms and owner p99 is not strictly below 2 ms;
p99 remains inside 100 ms and semantic/loss bounds pass.

The client interval lasted 39.398 seconds and used 31.58 CPU-seconds (80.2% of one CPU), 20,158
transport iterations, 1,943 voluntary/12 involuntary context switches, 783 minor/one major fault,
9,696 to 11,856 KiB resident pages, 12,256 KiB final high-water, and 35 to 34 descriptors. The
device interval lasted 39.874 seconds and used 38.80 CPU-seconds (97.3%), 9,243 iterations, 1,970/8
context switches, 30,579/3 faults, 10,880 to 12,288 KiB resident pages, 13,696 KiB high-water, and
34 to 33 descriptors. The transfer workload wrote about 1.12 GiB and 0.408 GiB through the two
processes during their sampled intervals.

Compact export allocation is 1,581,056 bytes. Its manifest SHA-256 is
`236f2d536ee61a83923ee45f23e3d656d37b61b97487936209ec35af3d435fd1`; pair manifest is
`1ee3952d51c02fbef3e9f6c7f374e32f8f839989b56da57ebc75b0fba494f26d`; client/device resource
records are `f1b7f4b73c9f37b3d87889a7a0b4751a383b37b6445ed4abec35a623d3379577` and
`fd3d4aa5195ded769a6cecad8f69159a8bc2f67ea5b805767317febfdf241f21`.

## Rejected outgoing-coalescing A/B

Source commit: `1d4792fb5e325250d7109639a204642ba2680b88`

Proof: `.sandwurm/exports/pairs/pair.bmar1y5q`

Scenario: direct UDP, `ratox-matrix-bulk-1`

Binary SHA-256: `bd66c651eb5a931c121c5a337db46e5ad8b05e9207156a0ae6a6762469dfa4b1`

This cell coalesced successful outgoing callback bookkeeping while retaining the receive descriptor
optimization. It completed 1,000/1,000 samples, cancellation, close, both resource intervals, and
strict raw/compact verification. It is a valid failed experiment, not a latency pass.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 165.300 ms | 473.704 ms | 505.064 ms | 508.521 ms | 665.246 ms | 464.008 ms |
| keypress to controller OUTPUT | 165.143 ms | 473.432 ms | 504.998 ms | 508.471 ms | 665.121 ms | 463.853 ms |
| local OUTPUT to render | 0.029 ms | 0.067 ms | 0.778 ms | 1.490 ms | 2.644 ms | 0.155 ms |
| interactive owner wait | 0.002 ms | 0.013 ms | 0.044 ms | 0.103 ms | 1.984 ms | 0.022 ms |
| remote stage to commit | 0.360 ms | 1.621 ms | 4.288 ms | 10.113 ms | 13.683 ms | 1.943 ms |
| remote commit to output | 0.012 ms | 5.844 ms | 7.050 ms | 8.460 ms | 12.712 ms | 4.732 ms |
| remote stage to output | 0.563 ms | 7.195 ms | 10.759 ms | 13.610 ms | 26.108 ms | 6.675 ms |

All 1,000 renders reached 50 and 100 ms; 991 reached 250 ms. The device ended with zero pending
events, event high-water five, zero required-event backpressure, and only 238,554 observable bulk
bytes. The client/device intervals lasted about 476/477 seconds but used only 5.32%/5.38% of one CPU.
Those facts jointly reject local Agent congestion as the cause: unconstrained synchronous file
production filled c-toxcore's shared reliable path and interactive output waited behind it.

Compact export allocation is 1,585,152 bytes. Its manifest SHA-256 is
`fecb6bed871e5aa06cfcf76465f26ad08c0a464e8c6f89eb39ed818d025f990d`; pair manifest is
`fcf7f3d10815621126ed223d9a52b0881bcb0217ce11dd394be013bb0d1533c9`; client/device resource
records are `fa1369122e177b5f64caf6553895a48dd1487408ca7c1b5d9b6d4d2c577b15f2` and
`df9a48cad881ae56818a4ea9b52a3a1efead8265369909cb9b2fb9e863fbbb9a`.

## Descriptor-only requalification

Source commit: `b76c1f7`

Proof: `.sandwurm/exports/pairs/pair.y__zgt1p`

Scenario: direct UDP, `ratox-matrix-bulk-1`

Binary SHA-256: `6ee9549a776f22ae79a3f5c99e18185914ed6c833ac6c79ffa414cd16354cc2d`

This cell restores per-chunk outgoing bookkeeping, retains the pinned incoming descriptor, and binds
final Agent status for both roles. It completed 1,000/1,000 samples, observed 541,816,458 bulk bytes,
cancelled to empty in one accepted control, closed, and passed strict raw and compact verification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 4.593 ms | 19.918 ms | 51.146 ms | 73.048 ms | 231.738 ms | 23.426 ms |
| keypress to controller OUTPUT | 4.564 ms | 19.768 ms | 51.057 ms | 72.992 ms | 231.388 ms | 23.282 ms |
| local OUTPUT to render | 0.025 ms | 0.064 ms | 0.664 ms | 1.356 ms | 2.616 ms | 0.144 ms |
| interactive owner wait | 0.001 ms | 0.014 ms | 1.484 ms | 3.972 ms | 13.423 ms | 0.276 ms |
| remote stage to commit | 0.352 ms | 1.611 ms | 3.326 ms | 4.569 ms | 16.227 ms | 1.754 ms |
| remote commit to output | 0.006 ms | 5.525 ms | 9.784 ms | 12.809 ms | 20.170 ms | 4.279 ms |
| remote stage to output | 0.388 ms | 6.407 ms | 12.179 ms | 15.138 ms | 21.472 ms | 6.033 ms |

There were 53 renders at or above 50 ms, four at or above 100 ms, and none at or above 250 ms. This
is a major recovery from the rejected coalescing cell, but still fails direct p95 and owner p99.

The client event queue reached 1,024 and recorded 1,227 required waits totaling 248.625 ms, maximum
108.002 ms. The device reached 765 with zero waits. Client/device intervals were 28.564/29.165
seconds and used 77.2%/92.0% of one CPU, kept descriptors at 35-to-34/34-to-33, and wrote about
0.959/0.396 GB. These bilateral counters select an explicit pre-saturation file pacer.

Compact export allocation is 1,601,536 bytes. Its manifest SHA-256 is
`ca7eb7f1254b742b429dc29b7846d974758e3236883035fad42b7fec80c4c987`; pair manifest is
`cf47814a0ca6159a03b66ffb7d32911179e8d2ba6fdd58610cd81500f1838ef8`; client/device resource
records are `4daad77ac53942383d4dd25a26e4b9ad9cebe2852e41bea420e8aca079a24dc4` and
`c7467a3a11ead6218552d6ed8a857b128d5adae25b219f8003c6d4c4d6e010b7`; final status records are
`f5c22c3084cf672750e19bffad3aaede102b845dd7a21882886e41ddbee5e6a1` and
`8b553c920d4319db4660069756010b90154f098f2eb5f233b6d01689ea9f4eef`.

## Accepted explicit-pacing qualification

Source commit: `5305e7d2c9083e99e3ece619f7a35e22c3c34b40`

Proof: `.sandwurm/exports/pairs/pair.a4j1uirz`

Scenario: direct UDP, `ratox-matrix-bulk-1`

Binary SHA-256: `3a5e12184631e986fdc93fe6d0c56bd0b9efc5d459d6ecb0683964d98cda9cfc`

ADR 0160 pauses synchronous incoming/outgoing file callbacks at 64 queued events, resumes below 16
after at least 5 ms, and keeps the 1,024-entry queue as semantic reserve. The exact cell completed
1,000/1,000 samples, one simultaneous 1 GiB transfer per role, cancellation to empty in one accepted
round, terminal close, bilateral resource/status capture, and strict raw plus compact verification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 8.427 ms | 21.481 ms | 42.727 ms | 50.730 ms | 67.881 ms | 24.168 ms |
| keypress to controller OUTPUT | 8.217 ms | 21.270 ms | 42.673 ms | 50.416 ms | 66.453 ms | 24.014 ms |
| local OUTPUT to render | 0.035 ms | 0.079 ms | 0.493 ms | 1.438 ms | 3.570 ms | 0.155 ms |
| interactive owner wait | 0.003 ms | 0.016 ms | 0.352 ms | 1.499 ms | 3.828 ms | 0.075 ms |
| remote stage to commit | 0.464 ms | 2.299 ms | 4.221 ms | 5.130 ms | 30.867 ms | 2.404 ms |
| remote commit to output | 0.009 ms | 6.015 ms | 11.454 ms | 14.462 ms | 39.906 ms | 5.476 ms |
| remote stage to output | 0.560 ms | 7.690 ms | 15.088 ms | 18.982 ms | 42.683 ms | 7.880 ms |

Thirteen renders reached 50 ms; none reached 100 or 250 ms. Render p95 is below the 50 ms direct
budget and exact owner p99 is below 2 ms, so this is the first accepted loaded R7 cell.

Client/device event high-water was 180/130 rather than 1,024/765, and both recorded zero required
waits. They made 853/876 matched pause/resume cycles with zero control failures and zero transfers
left scheduler-paused. Total successful hold was 7.741/7.841 seconds; maximum individual hold was
49.268/57.328 ms. The bulk observation advanced 172,630,836 bytes before one-round cancellation.

The client interval lasted 29.689 seconds, used 24.03 CPU-seconds (80.9% of one CPU), wrote
887,017,472 bytes, held descriptors at 35-to-34, and grew resident pages from 9,816 to 10,200 KiB.
The device interval lasted 30.432 seconds, used 27.67 CPU-seconds (90.9%), wrote 742,395,904 bytes,
held descriptors at 34-to-33, and grew from 11,008 to 11,652 KiB with an 11,904 KiB high-water.

Compact export allocation is 1,601,536 bytes. Its manifest SHA-256 is
`640b7b1074b66f54d90b3b6410c6e1371d956fef282d4c8a144e361a26d327b8`; compact pair manifest is
`59cd4e9fb2bacd980db4694053a1c03be22fa41aee062a512ffb04d5f84311e3`; client/device resource
records are `9530d3d8ec8ae445d8d293656a0e85d83581d1f617d6c36a9c9713103ff248ff` and
`918ac0e8caf3ecbf659f93608de4706dd1f045382e9ec3378404b00516d095f5`; final status records are
`e1a6ecca245fc66d8bd070dd2dcf0c044ca03f651cc5e07f9d5326fce4c8ac9f` and
`89043a4bd75e830711f4dedf5aa03dfb32d8cfe0b1e59ee84c15dfa69202377a`. The audited cleaner then
reclaimed exactly the 2.4 GiB private raw VM root and the compact proof strictly reverified.

## Accepted forced-TCP one-stream qualification

Source commit: `d7c881ce60863f73577af54dd9ce6ab6aa11c4b8`

Proof: `.sandwurm/exports/pairs/pair.0vkhkq96`

Scenario: forced TCP, `ratox-matrix-bulk-1`

Binary SHA-256: `3a5e12184631e986fdc93fe6d0c56bd0b9efc5d459d6ecb0683964d98cda9cfc`

The matched relay-only cell completed 1,000/1,000 samples, one simultaneous 1 GiB transfer per role,
one-round cancellation, terminal close, bilateral status/resource capture, and strict raw/compact
verification. Forced-TCP latency is reported separately; only completeness, zero semantic loss, and
owner p99 below 2 ms are common qualification thresholds.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 6.266 ms | 18.838 ms | 57.594 ms | 70.044 ms | 103.892 ms | 22.741 ms |
| keypress to controller OUTPUT | 6.184 ms | 18.757 ms | 57.497 ms | 69.953 ms | 103.718 ms | 22.590 ms |
| local OUTPUT to render | 0.030 ms | 0.063 ms | 0.574 ms | 1.401 ms | 5.213 ms | 0.150 ms |
| interactive owner wait | 0.001 ms | 0.012 ms | 0.440 ms | 1.452 ms | 4.603 ms | 0.088 ms |
| remote stage to commit | 0.377 ms | 1.839 ms | 3.123 ms | 4.085 ms | 18.723 ms | 1.780 ms |
| remote commit to output | 0.008 ms | 6.065 ms | 8.125 ms | 10.890 ms | 21.929 ms | 5.034 ms |
| remote stage to output | 0.543 ms | 7.481 ms | 10.678 ms | 13.825 ms | 24.233 ms | 6.814 ms |

Sixty-eight renders reached 50 ms, one reached 100 ms, and none reached 250 ms. Exact owner p99 is
1.452 ms, so the route-independent gate passes.

Client/device event high-water was 183/102 with zero required-event waits. They made 248/278 matched
pause/resume cycles, recorded zero control failures, and ended with no scheduler-owned pause. Total
successful hold was 1.682/1.727 seconds and maximum hold was 21.420/19.518 ms. Bulk advanced
157,335,960 bytes before one-round cancellation.

The client interval lasted 27.013 seconds and used 16.96 CPU-seconds (62.8% of one CPU), wrote
660,422,656 bytes, held descriptors at 35-to-34, and grew resident pages from 9,956 to 10,340 KiB.
The device interval lasted 27.525 seconds and used 17.55 CPU-seconds (63.8%), wrote 515,940,352 bytes,
held descriptors at 34-to-33, and grew from 10,752 to 11,548 KiB with an 11,848 KiB high-water.

Compact export allocation is 1,605,632 bytes. Its manifest SHA-256 is
`edd5514852ecfbcfaf249badf8aa7429262ef5af031b5ef2ba0864db32eb9140`; compact pair manifest is
`6fc8f114a224fe3bc9d90c0cc7dd5c165953ead7680dd3d77eacab80ace79342`; client/device resource
records are `16c5706011252ad258233a4b2d714ae0c22575dd9ef7f8ebb93365537ee31a11` and
`54b1564170ad23c683cacd9b257870a3a7c03197747dbca3e6f3a5004e1703f6`; final status records are
`faf0c967893ec990dd82f9512785825fce0630cabc24082ba69314dcbdb20992` and
`084c1ae85a9702d6a477defd7dba291f26e181799d1cd9995369350b30a691fa`. The audited cleaner reclaimed
exactly its 2.3 GiB private raw VM root, after which the compact proof strictly reverified.

## Incomplete first direct-UDP eight-stream attempt

Private diagnostic root: not retained

Scenario: direct UDP, `ratox-matrix-bulk-8`

This attempt is not a pair proof and will not be compact-exported. It completed and atomically wrote
all 1,000 exact terminal rows, but the guest then asserted that all eight incoming transfers were
`state=active`. ADR 0160 makes `state=paused` an intentional live pacing phase, so the assertion
mistook scheduler state for transfer loss before recording bulk progress, cancellation, resource
intervals, receipts, or a pair manifest.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 17.451 ms | 50.090 ms | 194.160 ms | 499.049 ms | 1,012.296 ms | 77.211 ms |
| keypress to controller OUTPUT | 17.312 ms | 49.949 ms | 194.120 ms | 498.971 ms | 1,010.771 ms | 77.072 ms |
| local OUTPUT to render | 0.031 ms | 0.069 ms | 0.403 ms | 1.527 ms | 5.799 ms | 0.139 ms |
| interactive owner wait | 0.001 ms | 0.014 ms | 0.097 ms | 1.023 ms | 2.269 ms | 0.044 ms |

There were 502 renders at or above 50 ms, 181 at or above 100 ms, and 37 at or above 250 ms. Thus
the measurement defect does not make this a latency pass. Copy-on-write journal recovery of the
stopped client disk found event high-water 137, zero required-event waits, 2,705 matched pacing
pause/resume cycles, zero control failures, and no scheduler-owned pause at final status. ADR 0161
introduces observation v6 with exact `present = active + paused` accounting. Only a clean committed
rerun that completes lifecycle evidence and strict verification may classify the cell.

## Retained direct-UDP eight-stream performance failure

Source commit: `cbd8844708e152c36238555ac820305acc65e4e7`

Proof: `.sandwurm/exports/pairs/pair.y0d97_ng`

Scenario: direct UDP, `ratox-matrix-bulk-8`

Binary SHA-256: `3a5e12184631e986fdc93fe6d0c56bd0b9efc5d459d6ecb0683964d98cda9cfc`

The committed ADR 0161 rerun completed 1,000/1,000 exact terminal exchanges and the entire file
lifecycle. Observation v6 proved eight present transfers before sampling and seven active plus one
paused afterward, with all eight progressed, 107,365,752 aggregate position bytes, and a 19 ms
progress checkpoint. One cancellation round accepted all eight controls and reached empty in
340 ms. Terminal close, both resource/status captures, raw verification, compact export, and compact
reverification all passed.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 9.441 ms | 47.629 ms | 144.120 ms | 179.491 ms | 264.277 ms | 60.872 ms |
| keypress to controller OUTPUT | 9.408 ms | 47.574 ms | 144.029 ms | 179.446 ms | 263.995 ms | 60.771 ms |
| local OUTPUT to render | 0.028 ms | 0.068 ms | 0.262 ms | 0.615 ms | 1.695 ms | 0.101 ms |
| interactive owner wait | 0.003 ms | 0.013 ms | 0.057 ms | 0.420 ms | 1.529 ms | 0.030 ms |
| remote stage to commit | 0.358 ms | 1.201 ms | 3.086 ms | 3.762 ms | 19.720 ms | 1.533 ms |
| remote commit to output | 0.008 ms | 6.105 ms | 10.692 ms | 24.676 ms | 29.940 ms | 5.836 ms |
| remote stage to output | 0.569 ms | 7.314 ms | 13.581 ms | 27.285 ms | 33.063 ms | 7.369 ms |

There were 455 renders at or above 50 ms, 162 at or above 100 ms, and one at or above 250 ms. The
cell passes exact semantics and the owner p99 budget but fails direct-route p95, p99, and miss
limits.

Client/device event high-water was 134/138 with zero required-event waits. They recorded 2,917/2,996
matched pacing cycles, zero control failures, and zero final scheduler-owned pauses. Total hold time
was 129.448/129.639 seconds and maximum individual hold was 187.468/176.869 ms. This isolates the
tail beyond the Agent owner and semantic queues: eight bilateral transfer schedulers repeatedly
pause and resume the same shared reliable carrier, where synchronized release remains a candidate.

The client interval lasted 64.983 seconds, used 49.99 CPU-seconds (76.9% of one CPU), wrote
3,018,768,384 bytes, moved from 42 to 34 descriptors, and grew from 9,792 to 10,176 KiB resident.
The device interval lasted 65.574 seconds, used 51.36 CPU-seconds (78.3%), wrote 2,678,779,904 bytes,
moved from 41 to 33 descriptors, and grew from 11,008 to 11,544 KiB with an 11,648 KiB high-water.

Compact export allocation is 1,601,536 bytes. Its manifest SHA-256 is
`829a00132acf7edd77af0bb842d9cfa90b0d24dcb4b795d6728bac9e936400fe`; compact pair manifest is
`743ea481b313cecd639ef87026092d0c7051023a0c341a8e901bf4c9f914aba4`; client/device resource
records are `8aac665b380e8be66afda53dd887dd505b642bafb54b7ae1f9939e30d1ba96bc` and
`58a2b7c174f2d5f58cf16f684450078168758c7a617514a09315f84cea7d910b`; final status records are
`cf65314739af7514c6249d83d0354abd256cb13fbb754c9ed7184f7748dac90d` and
`3589e3cb4684843da020264ac83cb3963ae388ef4d15204213fa98bdce192f6f`. The audited cleaner reclaimed
exactly the 2.4 GiB private raw root and the compact proof strictly reverified.

## Retained ADR 0162 zero-activation carrier-starvation run

Source commit: `dbcba873c2a03b81017290d11dbcab1060347820`

Proof: `.sandwurm/exports/pairs/pair.dwo77gs0`

Scenario: direct UDP, `ratox-matrix-bulk-8`

Binary SHA-256: `3ff2cec4b16ad0266bcd4a523a3878ace49234a5a6cec7f7fb00e0692219edad`

This clean run passes the complete v6 workload lifecycle but does not exercise ADR 0162. Eight
transfers are present and active before and after sampling and all report positive progress, but
aggregate position is only 375,654 bytes. Neither role reaches the event high-water pacing trigger:
pause, resume, batch, failure, and required-event-wait counts are all zero. One cancellation round
accepts all eight controls and reaches empty in 286 ms; terminal close, resources/status, strict raw
verification, compact export, and compact reverification pass.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 9.617 ms | 468.734 ms | 504.428 ms | 506.962 ms | 510.656 ms | 377.762 ms |
| keypress to controller OUTPUT | 9.495 ms | 468.571 ms | 504.312 ms | 506.904 ms | 510.600 ms | 377.661 ms |
| local OUTPUT to render | 0.029 ms | 0.065 ms | 0.213 ms | 1.059 ms | 1.419 ms | 0.101 ms |
| interactive owner wait | 0.003 ms | 0.013 ms | 0.038 ms | 0.117 ms | 1.470 ms | 0.020 ms |
| remote stage to commit | 0.430 ms | 1.704 ms | 3.530 ms | 9.265 ms | 12.783 ms | 1.928 ms |
| remote commit to output | 0.018 ms | 5.914 ms | 6.813 ms | 7.833 ms | 11.260 ms | 4.786 ms |
| remote stage to output | 0.776 ms | 7.437 ms | 9.999 ms | 12.523 ms | 19.378 ms | 6.714 ms |

There are 919/856/804 renders at or above 50/100/250 ms. The client interval lasts 388.216 seconds,
uses 20.68 CPU-seconds (5.3%), writes 295,034,880 bytes, moves from 42 to 34 descriptors, and grows
from 9,860 to 10,116 KiB resident. The device lasts 388.733 seconds, uses 21.38 CPU-seconds (5.5%),
writes 334,827,520 bytes, moves from 41 to 33 descriptors, and grows from 10,880 to 11,168 KiB with
an 11,392 KiB high-water. Low CPU, negligible file progress, healthy owner/remote service, and delay
before the remote input stage identify a shared-carrier starvation state below the reactive pacer.

Compact allocation is 1,609,728 bytes. Compact export/pair manifests are
`56904fe53760960497fa17abcca9dd4df8b65685470d09a5f0b85b1d008792b3` and
`72046ea34a19fc93465524c7314b69478b96376ca5c099b486ab81ed9d4872e6`; client/device resources are
`ec82fb1f7a91f8526634948c8a4287ea0dff8f102113451074f7106582e4ba03` and
`87a4b367225cf00a717091376cc12398b49833824ee340c15d985c33cf432471`; final statuses are
`2c1adda87b52a55df076c65b0f6735560d72e210e1dd99466885c2c4ef945dab` and
`9527255ae59e7785a7bc2a93e40efbd7df1421af7c5752e4a7262c1b0fac9f64`.

## Retained ADR 0162 activated singleton-batch run

Source commit: `dbcba873c2a03b81017290d11dbcab1060347820`

Proof: `.sandwurm/exports/pairs/pair.xs9phpya`

Scenario: direct UDP, `ratox-matrix-bulk-8`

Binary SHA-256: `3ff2cec4b16ad0266bcd4a523a3878ace49234a5a6cec7f7fb00e0692219edad`

This replicate activates the treatment and passes every semantic/lifecycle gate. All eight transfers
remain present and active, progress by 132,238,434 aggregate bytes, and reach the progress checkpoint
in 32 ms. One cancellation round accepts eight controls and reaches empty in 363 ms. The
client/device execute 3,167/2,658 pause-resume cycles and the same number of singleton batches, with
observed batch maximum one, zero control failures, zero final scheduler ownership, and zero required
event waits.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 19.383 ms | 56.349 ms | 124.811 ms | 161.242 ms | 188.401 ms | 64.892 ms |
| keypress to controller OUTPUT | 19.181 ms | 56.307 ms | 124.706 ms | 161.059 ms | 188.367 ms | 64.769 ms |
| local OUTPUT to render | 0.028 ms | 0.075 ms | 0.337 ms | 0.737 ms | 2.229 ms | 0.123 ms |
| interactive owner wait | 0.002 ms | 0.015 ms | 0.092 ms | 0.716 ms | 1.371 ms | 0.038 ms |
| remote stage to commit | 0.375 ms | 1.358 ms | 3.269 ms | 4.390 ms | 16.586 ms | 1.704 ms |
| remote commit to output | 0.010 ms | 6.284 ms | 9.713 ms | 13.928 ms | 26.833 ms | 5.359 ms |
| remote stage to output | 0.617 ms | 7.459 ms | 12.398 ms | 17.625 ms | 31.413 ms | 7.064 ms |

There are 614 renders at or above 50 ms, 140 at or above 100 ms, and none at or above 250 ms.
Relative to `pair.y0d97_ng`, p95/p99/maximum improve by 19.309/18.249/75.876 ms and the one 250 ms
miss disappears; p50 worsens by 8.720 ms. Event high-water is 156/134. Total client/device pacing
hold is 127.305/163.144 seconds, and individual maxima are 158.594/244.801 ms.

The client interval lasts 69.501 seconds, uses 54.07 CPU-seconds (77.8%), writes 2,875,174,912
bytes, moves from 42 to 34 descriptors, and grows from 9,808 to 10,192 KiB resident. The device lasts
70.134 seconds, uses 56.76 CPU-seconds (80.9%), writes 2,790,449,152 bytes, moves from 41 to 33
descriptors, and grows from 11,008 to 11,388 KiB with an 11,648 KiB high-water.

Compact allocation is 1,605,632 bytes. Compact export/pair manifests are
`8780836c48857fb6a7fd3ef7a6ae437393bab4c3c9d8a43b660b527ed74e9baa` and
`c652651895b21e4a332a9b604a5114c2b44c0b2b6182bdb48b3c54fc694b2028`; client/device resources are
`a5ca97a54cf2de21e891b53b7504c449130858442889504798fa9a9eaf4ed0ff` and
`3dab4a1e07ddf93d5164366413a4b22efe37adcae5f9f010ae63ad932785f25d`; final statuses are
`b66fe001381873e3de73efacd82a4bfc3921e6a166a3891a10a048aec6cf8108` and
`17924de58cdec090ee3899f48ede24e79b723d3783cb9d2fc04779d32b7cf825`.
The audited cleaner reclaimed exactly both private raw roots (4.8 GiB); both compact proofs strictly
reverified afterward.

## Rejected ADR 0163 proactive-carrier near-pass

Source commit: `328f3a3dbf56c45c9f791268fe1a4ead9f96dd0c`

Proof: `.sandwurm/exports/pairs/pair.qrggya8w`

Scenario: direct UDP, `ratox-matrix-bulk-8`

Binary SHA-256: `53f046a0029f1a20de5e12d4226ec8e0fcad378a7658ba2cf1927c8f93e60e33`

This is the first exact clean-commit test of the receiver-owned one-file carrier window. It completes
all 1,000 terminal samples, observes all eight transfers as one active plus seven paused before and
after sampling, advances every file by 17,705,094 to 19,476,426 bytes for 151,114,362 aggregate
bytes, cancels to empty in one round, closes, captures both resource intervals, and passes strict raw
plus compact structural verification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 4.134 ms | 24.619 ms | 56.247 ms | 86.550 ms | 137.970 ms | 27.727 ms |
| keypress to controller OUTPUT | 3.802 ms | 24.317 ms | 55.774 ms | 86.456 ms | 137.913 ms | 27.616 ms |
| local OUTPUT to render | 0.023 ms | 0.063 ms | 0.350 ms | 1.016 ms | 2.287 ms | 0.111 ms |
| interactive owner wait | 0.001 ms | 0.011 ms | 0.127 ms | 1.488 ms | 3.683 ms | 0.056 ms |
| remote stage to commit | 0.271 ms | 1.456 ms | 3.590 ms | 4.709 ms | 5.859 ms | 1.731 ms |
| remote commit to output | 0.007 ms | 5.961 ms | 10.004 ms | 12.466 ms | 18.359 ms | 5.424 ms |
| remote stage to output | 0.285 ms | 7.099 ms | 12.826 ms | 15.698 ms | 21.271 ms | 7.155 ms |

Seventy-five renders reach 50 ms, six reach 100 ms, and none reaches 250 ms. Exact owner p99 passes
the common 2 ms gate. Direct render p95 is 56.247 ms, so the cell remains rejected. Relative to ADR
0162's activated `pair.xs9phpya`, p95/p99/max improve by 68.564/74.692/50.431 ms and p50 improves by
31.730 ms. The proactive window is therefore useful, but its first quantum is not the final default.

The receiving client records 1,456 carrier admissions, 1,454 rotations/pauses, zero carrier-control
failures, 227.661 seconds of aggregate wait, and 173.737 ms maximum wait. The sending device has no
incoming carrier state, as intended. Client/device event high-water is 577/297 with zero required
event backpressure. The reactive pacer records 999 pauses, 539 resumes, and 141 pause failures on the
carrier-owning client versus 1,130 matched pause/resume cycles and zero failures on the sender. The
client's final projection also contains one already-queued post-cancel chunk diagnostic. These facts
select typed scheduler-ownership coordination and terminal cancellation classification rather than a
Ratox framing change.

The client interval lasts 32.155 seconds, uses 26.14 CPU-seconds (81.3% of one CPU), writes
1,221,808,128 bytes, moves from 42 to 34 descriptors, and grows from 9,884 to 10,908 KiB resident.
The device interval lasts 32.839 seconds, uses 30.97 CPU-seconds (94.3%), writes 1,219,244,032 bytes,
moves from 41 to 33 descriptors, and grows from 11,008 to 11,540 KiB with an 11,648 KiB high-water.

Compact allocation is 1,601,536 bytes. Compact export/pair manifests are
`f1df8b62776e8edeb966ed887be22d699c7671292026676492e099caff2157ae` and
`2c9c8e3022b53aa90d65d1bbbb19886b65eeff213643aef20c2cd311bec57806`; client/device resources are
`e37079b28e6d8a24e82c2bd18f46275c45b2ed24372c3ff7e3dcfe495d81a7c1` and
`6cced11581939d94b7bd19a2e6de3e70013565c1a20ca0bf2bd1b20fc3d13e8f`; final statuses are
`e93e11a11bacea172792bc9d5f2b55afbeabfdba8ece1fda13e84805c54de18e` and
`138a1a2dcc17c6f8286d33c5eec1b96adc07ab233730aee109c4f57975478bec`.
The audited cleaner selected exactly the 2.5 GiB private raw root after strict export, reclaimed it,
and the compact proof strictly reverified afterward.

## Accepted ADR 0164 direct-UDP eight-stream qualification

Source commit: `63e845b904d4a7dbd85c9e11d92b58965314b4f4`

Proof: `.sandwurm/exports/pairs/pair.bo6l0der`

Scenario: direct UDP, `ratox-matrix-bulk-8`

Binary SHA-256: `dc69b043f3c5d023ada6ed748ef2656009a067978a383a1eaca4bae6ea166993`

This matched A/B uses the 50 ms carrier quantum, exact already-paused ownership handoff, and bounded
post-cancel event classification. It completes 1,000/1,000 terminal samples, observes all eight
files as one active plus seven paused before and after sampling, advances every file by 20,833,716 to
21,852,369 bytes for 170,498,931 aggregate bytes, cancels all eight to empty in one round, closes,
captures both resource intervals, and passes the stricter raw and compact verifier generation.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 4.932 ms | 19.934 ms | 39.634 ms | 55.093 ms | 81.084 ms | 22.318 ms |
| keypress to controller OUTPUT | 4.865 ms | 19.826 ms | 39.421 ms | 54.795 ms | 81.045 ms | 22.212 ms |
| local OUTPUT to render | 0.026 ms | 0.060 ms | 0.327 ms | 0.928 ms | 2.370 ms | 0.106 ms |
| interactive owner wait | 0.001 ms | 0.012 ms | 0.588 ms | 1.917 ms | 3.624 ms | 0.091 ms |
| remote stage to commit | 0.363 ms | 1.822 ms | 3.258 ms | 4.609 ms | 40.621 ms | 1.877 ms |
| remote commit to output | 0.005 ms | 6.272 ms | 9.961 ms | 12.580 ms | 16.865 ms | 5.558 ms |
| remote stage to output | 0.380 ms | 7.893 ms | 12.788 ms | 16.447 ms | 46.542 ms | 7.435 ms |

Seventeen renders reach 50 ms and none reaches 100 or 250 ms. Direct render p95 is 39.634 ms and
owner p99 is 1.917 ms, so both strict gates pass. Relative to `pair.qrggya8w`, render
p50/p95/p99/max improve by 4.685/16.613/31.457/56.886 ms. Remote p95 remains essentially flat,
confirming that the improvement is carrier scheduling rather than changed PTY execution.

The receiving client records 512 admissions, 507 rotations, 77 typed external-pause handoffs, zero
carrier failures, and zero reactive pause/resume failures. The sender records 1,001/1,000 reactive
pause/resume successes and zero failures. Both pacers and carrier windows end unowned and both event
queues end empty. Event high-water falls from 577/297 to 228/168 with zero required waits. The final
client event is an ordinary file chunk rather than a file-transfer failure, proving the cancellation
tombstone removes the prior false terminal diagnostic.

The client interval lasts 26.433 seconds, uses 21.64 CPU-seconds (81.9% of one CPU), writes
1,020,465,152 bytes, moves from 42 to 34 descriptors, and grows from 9,792 to 10,176 KiB resident.
The device interval lasts 26.991 seconds, uses 24.96 CPU-seconds (92.5%), writes 908,218,368 bytes,
moves from 41 to 33 descriptors, and grows from 10,880 to 11,552 KiB with an 11,904 KiB high-water.

Compact allocation is 1,605,632 bytes. Compact export/pair manifests are
`8827a927bfc4f54d0d0ed1d601d7b617d8ea36e5a1c0385b9dd6b47f65af0892` and
`34814ee45dd11e3427e856b44a17cedaf986a312095af7f4b45cc6df19f5cb00`; client/device resources are
`731d7dac8d6f1dd1be6d8c55dcfb31e34886d4282c2c8e2b0506a18875abfd5c` and
`916400276e4e301e2fccf920ea6b8603111662c0aa2f2c4ab94ba80e9d458b3d`; final statuses are
`fe4153f2eaeba1f670357fbf70fdb0ace2fac78938b751c39477724ed09d8448` and
`2125b885f31606eb255cd4a19b546f06fed3130503e117dcab5665a798fb193c`.
The audited cleaner reclaimed exactly the 2.4 GiB private raw root after strict export, and the
compact proof strictly reverified afterward.

## Accepted ADR 0164 forced-TCP eight-stream qualification

Source commit: `1823531e10e2f62d460fb58fa72fd2ea9bc8d97f`

Proof: `.sandwurm/exports/pairs/pair.pitcu1pk`

Scenario: forced TCP, `ratox-matrix-bulk-8`

Binary SHA-256: `dc69b043f3c5d023ada6ed748ef2656009a067978a383a1eaca4bae6ea166993`

This is the matched relay-only route cell using the identical binary as the accepted direct proof.
The manifest and strict verifier observe TCP with native UDP disabled. The run completes 1,000/1,000
terminal samples, keeps all eight files present as one active plus seven paused, advances every file
by 16,435,548 to 18,777,216 bytes for 139,548,606 aggregate bytes, cancels to empty in one round,
closes, captures both resource intervals, and passes strict raw plus compact verification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 9.415 ms | 24.636 ms | 76.249 ms | 98.314 ms | 119.607 ms | 33.602 ms |
| keypress to controller OUTPUT | 9.225 ms | 24.455 ms | 75.859 ms | 98.249 ms | 119.531 ms | 33.465 ms |
| local OUTPUT to render | 0.026 ms | 0.068 ms | 0.461 ms | 1.406 ms | 2.550 ms | 0.138 ms |
| interactive owner wait | 0.001 ms | 0.014 ms | 0.235 ms | 1.525 ms | 6.591 ms | 0.074 ms |
| remote stage to commit | 0.362 ms | 2.052 ms | 3.480 ms | 4.430 ms | 23.595 ms | 2.024 ms |
| remote commit to output | 0.006 ms | 5.755 ms | 10.026 ms | 11.698 ms | 16.436 ms | 4.839 ms |
| remote stage to output | 0.623 ms | 7.044 ms | 12.848 ms | 15.208 ms | 30.349 ms | 6.864 ms |

Two hundred ten renders reach 50 ms, eight reach 100 ms, and none reaches 250 ms. Exact owner p99 is
1.525 ms, so both common route gates pass. The forced-TCP distribution remains its own class: p95 is
18.655 ms above the accepted one-stream forced-TCP cell, while remote stage-to-output p95 remains
12.848 ms and owner p99 changes by only 0.073 ms.

The receiver records 742 carrier admissions, 739 rotations, 58 typed external-pause handoffs, and
zero carrier/reactive failures. The sender records 541/540 reactive pause/resume successes and zero
failures. Both event queues end empty at high-water 141/139 with zero required waits, both scheduler
ownership counts end zero, and neither final status is a file-transfer failure.

The client interval lasts 38.523 seconds, uses 25.01 CPU-seconds (64.9% of one CPU), writes
861,769,728 bytes, moves from 42 to 34 descriptors, and grows from 9,780 to 10,164 KiB resident. The
device interval lasts 39.166 seconds, uses 28.70 CPU-seconds (73.3%), writes 853,028,864 bytes, moves
from 41 to 33 descriptors, and grows from 10,880 to 11,420 KiB with an 11,620 KiB high-water.

Compact allocation is 1,609,728 bytes. Compact export/pair manifests are
`b5a005901d3a63de85d20308e3424a3a66222005045993318b9226b3cabea0a2` and
`877e32349454ccf764af43dda964f8bb83fb0fc73e138d5f71e6d87bc824ec0c`; client/device resources are
`8e2f594bf7a8f2e503f4755786a1b9015983026fb7c33ba07d507e9274ba6e7e` and
`696a7b3ccd800ed57f827a4f8fb0f8b390c2123e429f98208c1fb5ba12fdba1f`; final statuses are
`3626571b0a0051d412442fafde7b3d2a2dc80c340d138b6667b0ea7319bf6544` and
`858721e79ef15df0b2daf535fa438b83f12af8ee9b8df5fe5920d7e5821eeb7c`.
The audited cleaner reclaimed exactly the 2.4 GiB private raw root after strict export, and the
compact proof strictly reverified afterward.

## Accepted ADR 0164 direct-UDP sixteen-stream qualification

Source commit: `37d654f9d62b3240fc7aee0019c3e38ab3d87b1e`

Proof: `.sandwurm/exports/pairs/pair.xphist_e`

Scenario: direct UDP, `ratox-matrix-bulk-16`

Binary SHA-256: `dc69b043f3c5d023ada6ed748ef2656009a067978a383a1eaca4bae6ea166993`

This first 16-stream cell uses the accepted ADR 0164 binary unchanged. It completes 1,000/1,000
terminal samples, keeps all 16 files present as one active plus 15 paused, advances every file by
9,614,823 to 11,342,283 bytes for 169,803,834 aggregate bytes, cancels all 16 to empty in one round,
closes, captures both resource intervals, and passes strict raw plus compact verification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 5.463 ms | 20.276 ms | 40.591 ms | 51.960 ms | 75.043 ms | 22.737 ms |
| keypress to controller OUTPUT | 5.439 ms | 20.124 ms | 40.500 ms | 51.885 ms | 74.981 ms | 22.638 ms |
| local OUTPUT to render | 0.024 ms | 0.059 ms | 0.301 ms | 0.880 ms | 1.954 ms | 0.099 ms |
| interactive owner wait | 0.001 ms | 0.012 ms | 0.649 ms | 1.894 ms | 3.778 ms | 0.102 ms |
| remote stage to commit | 0.389 ms | 1.819 ms | 3.682 ms | 4.733 ms | 39.515 ms | 1.860 ms |
| remote commit to output | 0.007 ms | 6.280 ms | 9.968 ms | 11.892 ms | 29.325 ms | 5.558 ms |
| remote stage to output | 0.705 ms | 7.745 ms | 12.781 ms | 16.121 ms | 41.124 ms | 7.418 ms |

Fourteen renders reach 50 ms and none reaches 100 or 250 ms. Direct p95 is 40.591 ms and owner p99
is 1.894 ms, so both strict gates pass. Relative to direct `bulk-8`, the distributions are nearly
flat: p50/p95/p99 change by +0.342/+0.957/-3.133 ms. Aggregate progress is also nearly equal, while
each of twice as many files receives a fair smaller share.

The receiver records 529 admissions, 524 rotations, 60 typed handoffs, and zero carrier/reactive
failures. Maximum wait grows from 425.861 to 890.887 ms, consistent with doubling one 50 ms round;
the nonzero per-file minimum rejects starvation. Both event queues end empty at high-water 203/183
with zero required waits, and both final statuses remain ordinary file events/controls.

The client interval lasts 27.040 seconds, uses 22.18 CPU-seconds (82.0% of one CPU), writes
1,036,013,568 bytes, moves from 50 to 34 descriptors, and grows from 9,720 to 10,232 KiB resident. The
device interval lasts 27.581 seconds, uses 25.69 CPU-seconds (93.1%), writes 932,016,128 bytes, moves
from 49 to 33 descriptors, and grows from 10,752 to 11,428 KiB with an 11,648 KiB high-water.

Compact allocation is 1,601,536 bytes. Compact export/pair manifests are
`23cfea62cf1952779c0ec6e505c7767a7aebcea444c247370ac457cbd2121f57` and
`74965ccee7c3125cfd0b6eb5e8475b6b6a8bb3cb2362a84626c0ee20c20c8bcc`; client/device resources are
`b3a2c728e2dce18b8d0184fe477eb0a24dfd4bb7c983950ce8f3a424d1c297d4` and
`1144c14b575b0289655285811dc8ca7dacc43ec38325f3b3539dd5d339e42817`; final statuses are
`2250acda9768c4f4a2dfcfdb27ad93f61be06f0f383f23ca92cd6d52a0fabf73` and
`2e816261a8558bd4062f5e4e365e8cd7c80a9a888637a996da0b76289d1f4b48`.
The audited cleaner reclaimed exactly the 2.4 GiB private raw root after strict export, and the
compact proof strictly reverified afterward.

## Accepted ADR 0164 forced-TCP sixteen-stream qualification

Source commit: `0cbaa2c6e3e55a010e2eb3c76c4e330da2574656`

Proof: `.sandwurm/exports/pairs/pair.qk3d51k6`

Scenario: forced TCP, `ratox-matrix-bulk-16`

Binary SHA-256: `dc69b043f3c5d023ada6ed748ef2656009a067978a383a1eaca4bae6ea166993`

This matched cell changes only the route class from the accepted direct-UDP 16-stream cell. It
completes 1,000/1,000 terminal samples, keeps all 16 files present as one active plus 15 paused,
advances every file by 7,896,960 to 9,642,243 bytes for 140,818,152 aggregate bytes, cancels all 16
to empty in one round, closes, captures both resource intervals, and passes strict raw plus compact
verification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 9.145 ms | 26.565 ms | 75.704 ms | 87.867 ms | 106.025 ms | 35.542 ms |
| keypress to controller OUTPUT | 9.067 ms | 26.319 ms | 75.636 ms | 87.802 ms | 105.868 ms | 35.380 ms |
| local OUTPUT to render | 0.035 ms | 0.076 ms | 0.614 ms | 1.426 ms | 3.451 ms | 0.161 ms |
| interactive owner wait | 0.002 ms | 0.015 ms | 0.225 ms | 1.013 ms | 10.814 ms | 0.069 ms |
| remote stage to commit | 0.515 ms | 2.179 ms | 3.723 ms | 4.904 ms | 23.127 ms | 2.207 ms |
| remote commit to output | 0.008 ms | 5.730 ms | 9.953 ms | 12.486 ms | 32.424 ms | 4.829 ms |
| remote stage to output | 0.947 ms | 7.018 ms | 13.066 ms | 15.811 ms | 34.220 ms | 7.036 ms |

Two hundred thirty-one renders reach 50 ms, four reach 100 ms, and none reaches 250 ms. Exact owner
p99 is 1.013 ms, so the common forced-route gates pass. Relative to forced-TCP `bulk-8`, render
p50/p95/p99 changes by +1.929/-0.545/-10.447 ms: doubling stream count does not create a new terminal
tail. The forced-route p95 remains classified separately from the direct-route 50 ms target.

The receiver records 786 admissions, 782 rotations, 84 typed handoffs, and zero carrier/reactive
failures. Maximum fair wait is 885.574 ms, the expected order for a 16-file 50 ms round, and nonzero
minimum progress rejects starvation. Both event queues end empty at high-water 190/136 with zero
required waits, and both final statuses are ordinary `file-control` events.

The client interval lasts 40.952 seconds, uses 27.58 CPU-seconds (67.3% of one CPU), writes
916,189,184 bytes, moves from 50 to 34 descriptors, and grows from 9,944 to 10,456 KiB resident. The
device interval lasts 41.483 seconds, uses 31.35 CPU-seconds (75.6%), writes 876,027,904 bytes, moves
from 49 to 33 descriptors, and grows from 10,624 to 11,548 KiB with an 11,640 KiB high-water.

Compact allocation is 1,605,632 bytes. Compact export/pair manifests are
`138a7d54c247e2d640f521587c06e565c2d7c51f3a9429af41c5d230fd946034` and
`c83c60571b264864268e6be753c3b0e4dbcf91a6caabfda7db67b5be2bec3aff`; client/device resources are
`a7c06e2291ac9a963c804fa58fac43dfe5419f7ccd2f87e9e8dc4cb7d9576c6a` and
`a220526c0105379fd95839554d9d8406db009af510f5d6626019dd3a00cb4f4a`; final statuses are
`ad2400657fa32a7b3a79513b27dde3675bc8071971ffb0ff3d1738a77459f93d` and
`d0bbe4844e9ed34696fd46db81b7b1757deb1e44183b2a28aae697bc0ad255db`.
The audited cleaner reclaimed exactly the 2.5 GiB private raw root after strict export, and the
compact proof strictly reverified afterward.

## Accepted ADR 0164 direct-UDP thirty-two-stream qualification

Source commit: `7c394f099e275667ffa4868f2989df3a1206b1e3`

Proof: `.sandwurm/exports/pairs/pair.ktcwivx_`

Scenario: direct UDP, `ratox-matrix-bulk-32`

Binary SHA-256: `dc69b043f3c5d023ada6ed748ef2656009a067978a383a1eaca4bae6ea166993`

This first 32-stream cell uses the accepted ADR 0164 binary unchanged. It completes 1,000/1,000
terminal samples, keeps all 32 files present at the second observation, advances every file by
4,097,919 to 5,001,408 bytes for 147,315,321 aggregate bytes, cancels all 32 to empty in one round,
closes, captures both resource intervals, and passes strict raw plus compact verification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 6.476 ms | 23.589 ms | 47.765 ms | 58.319 ms | 75.984 ms | 26.012 ms |
| keypress to controller OUTPUT | 6.430 ms | 23.447 ms | 47.617 ms | 58.254 ms | 75.916 ms | 25.902 ms |
| local OUTPUT to render | 0.025 ms | 0.064 ms | 0.251 ms | 0.985 ms | 2.596 ms | 0.110 ms |
| interactive owner wait | 0.002 ms | 0.011 ms | 0.618 ms | 1.811 ms | 3.734 ms | 0.091 ms |
| remote stage to commit | 0.456 ms | 1.562 ms | 3.660 ms | 4.687 ms | 31.512 ms | 1.871 ms |
| remote commit to output | 0.010 ms | 5.967 ms | 9.871 ms | 11.827 ms | 17.452 ms | 5.478 ms |
| remote stage to output | 0.603 ms | 7.307 ms | 12.900 ms | 15.232 ms | 33.412 ms | 7.349 ms |

Thirty-seven renders reach 50 ms and none reaches 100 or 250 ms. Direct p95 is 47.765 ms and owner
p99 is 1.811 ms, so both strict gates pass. Relative to direct `bulk-16`, render p50/p95/p99 changes
by +3.313/+7.174/+6.359 ms. Latency grows but remains inside the frozen budget, while aggregate
progress remains in the same broad range and every one of twice as many files receives a fair share.

The receiver records 605 admissions, 590 rotations, 78 typed handoffs, and zero carrier/reactive
failures. Maximum wait grows from 890.887 ms to 1.744 seconds, consistent with doubling one 50 ms
round; the nonzero per-file minimum rejects starvation. Both event queues end empty at high-water
162/152 with zero required waits, and both final statuses are ordinary `file-control` events.

The client interval lasts 30.857 seconds, uses 25.81 CPU-seconds (83.6% of one CPU), writes
1,056,735,232 bytes, moves from 66 to 34 descriptors, and grows from 9,948 to 10,332 KiB resident. The
device interval lasts 31.448 seconds, uses 29.81 CPU-seconds (94.8%), writes 974,622,720 bytes, moves
from 65 to 33 descriptors, and grows from 11,008 to 11,636 KiB with an 11,776 KiB high-water.

Compact allocation is 1,605,632 bytes. Compact export/pair manifests are
`20bc35dd69cfd968b4d01e888cbe0d6922b21125e012c3f2f2a44e91b7e691ee` and
`f15c0cac54d25aae9eb80c5e44cbc655666c83ac524e5bd4a97710f2e88bb384`; client/device resources are
`6b29972f214ba5413f36a94e68f5eb1a3dc549fb3cc1f7dd31c3c2a5904c815a` and
`ed6d5f2cc12414fc337981dd2d983eb7b4f8a89f01716ebe1c62cac0782107d5`; final statuses are
`a4ebea80fe1ad2a9334800be270b98771cb5a95ae0fcfc3bd8b37d48f2d47bbe` and
`2bb5c5c7d462afd1c466012ef2fb95da9cbc2a7161e633e33b9fc7eddb47651d`.
The audited cleaner reclaimed exactly the 2.5 GiB private raw root after strict export, and the
compact proof strictly reverified afterward.

## Accepted ADR 0164 forced-TCP thirty-two-stream qualification

Source commit: `18b8817c9e05951f31a90024fb14d0e2886b14f8`

Proof: `.sandwurm/exports/pairs/pair.lanpv3u7`

Scenario: forced TCP, `ratox-matrix-bulk-32`

Binary SHA-256: `dc69b043f3c5d023ada6ed748ef2656009a067978a383a1eaca4bae6ea166993`

This matched cell changes only the route class from the accepted direct-UDP 32-stream cell. It
completes 1,000/1,000 terminal samples, keeps all 32 files present as one active plus 31 paused,
advances every file by 3,175,236 to 4,287,117 bytes for 122,955,393 aggregate bytes, cancels all 32
to empty in one round, closes, captures both resource intervals, and passes strict raw plus compact
verification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 7.921 ms | 21.324 ms | 76.331 ms | 95.608 ms | 163.533 ms | 30.375 ms |
| keypress to controller OUTPUT | 7.629 ms | 21.254 ms | 76.247 ms | 95.567 ms | 163.497 ms | 30.259 ms |
| local OUTPUT to render | 0.025 ms | 0.060 ms | 0.399 ms | 1.023 ms | 2.838 ms | 0.116 ms |
| interactive owner wait | 0.001 ms | 0.011 ms | 0.154 ms | 0.798 ms | 3.909 ms | 0.047 ms |
| remote stage to commit | 0.310 ms | 1.508 ms | 3.450 ms | 5.042 ms | 34.120 ms | 1.744 ms |
| remote commit to output | 0.007 ms | 5.920 ms | 9.362 ms | 11.232 ms | 17.322 ms | 5.370 ms |
| remote stage to output | 0.353 ms | 7.111 ms | 12.065 ms | 15.164 ms | 39.561 ms | 7.114 ms |

One hundred seventy-one renders reach 50 ms, nine reach 100 ms, and none reaches 250 ms. Exact owner
p99 is 0.798 ms, so the common forced-route gates pass. Relative to forced-TCP `bulk-16`, render
p50/p95/p99 changes by -5.241/+0.627/+7.741 ms. The tail remains in the same route class rather than
growing with doubled load; forced-route p95 remains classified separately from the direct target.

The receiver records 675 admissions, 670 rotations, 56 typed handoffs, and zero carrier/reactive
failures. Maximum fair wait is 1.736 seconds, the expected order for a 32-file 50 ms round, and
nonzero minimum progress rejects starvation. Both event queues end empty at high-water 185/147 with
zero required waits; final statuses are ordinary `file-chunk`/`file-control` events.

The client interval lasts 34.958 seconds, uses 22.25 CPU-seconds (63.6% of one CPU), writes
817,836,032 bytes, moves from 66 to 34 descriptors, and grows from 9,976 to 10,360 KiB resident. The
device interval lasts 35.520 seconds, uses 25.34 CPU-seconds (71.3%), writes 807,993,344 bytes, moves
from 65 to 33 descriptors, and grows from 10,880 to 11,664 KiB with an 11,752 KiB high-water.

Compact allocation is 1,609,728 bytes. Compact export/pair manifests are
`7d8d351cc4e7ce3059039c7dd194655120de97c9efc24fa86b8368e1117d266a` and
`ecf32bdba461c4022ff9596c1eb10ae5650fe958049fa539c8c846aff60d3e2f`; client/device resources are
`2e63537e5e0fd6bdc77779d487419d197a05880dfb366cfd7f8b74b478c1ce80` and
`32e572033158da9d718e33a905133d0c739d0f86c52d2841b9fb5313cdf1cfb6`; final statuses are
`4728eec43172d538c881ff15b583431bd0b4acd7174371cbd16c82ad3cd9e321` and
`8370933d139e0ea58336699fc671402ef4f8b69e56ccf2b7147937b4d93f7245`.
The audited cleaner reclaimed exactly the 2.5 GiB private raw root after strict export, and the
compact proof strictly reverified afterward.

## Rejected ADR 0164 direct-UDP sixty-four-stream qualification

Source commit: `0cc72a41eb8a53c32162a5faf416f566c0886877`

Proof: `.sandwurm/exports/pairs/pair.t736zqqh`

Scenario: direct UDP, `ratox-matrix-bulk-64`

Binary SHA-256: `dc69b043f3c5d023ada6ed748ef2656009a067978a383a1eaca4bae6ea166993`

This maximum-load cell uses the accepted ADR 0164 binary unchanged. It completes 1,000/1,000
terminal samples, keeps all 64 files present as one active plus 63 paused, advances every file by
6,855 to 109,680 bytes for 1,549,230 aggregate bytes, cancels all 64 to empty in one round, closes,
captures both resource intervals, and passes strict raw plus compact lifecycle verification. It
does not pass the frozen direct-route latency qualification.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 12.617 ms | 220.897 ms | 331.081 ms | 446.692 ms | 8,053.730 ms | 229.976 ms |
| keypress to controller OUTPUT | 12.590 ms | 220.813 ms | 331.005 ms | 446.449 ms | 8,053.561 ms | 229.879 ms |
| local OUTPUT to render | 0.027 ms | 0.069 ms | 0.226 ms | 0.662 ms | 1.028 ms | 0.097 ms |
| interactive owner wait | 0.001 ms | 0.013 ms | 0.043 ms | 0.118 ms | 0.800 ms | 0.018 ms |
| remote stage to commit | 0.326 ms | 1.709 ms | 3.487 ms | 4.615 ms | 11.797 ms | 1.840 ms |
| remote commit to output | 0.009 ms | 5.978 ms | 7.426 ms | 9.433 ms | 22.171 ms | 5.400 ms |
| remote stage to output | 0.574 ms | 7.653 ms | 10.293 ms | 12.972 ms | 27.224 ms | 7.240 ms |

Nine hundred ninety-seven renders reach 50 ms, 980 reach 100 ms, and 108 reach 250 ms. Direct p95
exceeds its 50 ms limit by 281.081 ms, p99 exceeds 100 ms by 346.692 ms, and the miss count is
nonzero. Owner p99 remains only 0.118 ms, local render work remains below 1.1 ms, and remote
stage-to-output p95 is 10.293 ms. The delay is therefore before remote owner admission or after
remote output production on the shared Tox transport, not in the owner queue, PTY, or renderer.

The receiver records 4,641 admissions, 4,624 rotations, zero typed handoffs, and zero true failures.
Maximum fair wait is 3.837 seconds, consistent with a 64-file 50 ms round, and nonzero minimum
progress rejects starvation, but aggregate progress is two orders of magnitude below the 32-stream
cell and needs an 8.036 second progress wait. Both event queues end empty at high-water only 50/50
with zero required waits; reactive pacing never activates. This is the low-utilization failure mode,
not the earlier event-pressure mode.

The client interval lasts 242.224 seconds, uses 27.91 CPU-seconds (11.5% of one CPU), writes
758,501,376 bytes, moves from 98 to 34 descriptors, and grows from 10,264 to 10,648 KiB resident. The
device interval lasts 242.846 seconds, uses 53.54 CPU-seconds (22.0%), writes 1,754,349,568 bytes,
moves from 97 to 33 descriptors, and grows from 11,264 to 11,692 KiB with an 11,904 KiB high-water.

Compact allocation is 1,609,728 bytes. Compact export/pair manifests are
`306bfed593375643454bfa1e775247b1b32ad0d56c3a9df32df50d6e6bb69ade` and
`7a4ef1ee91b7daa968ae03b89f596388e74239be00f94537cbf1ba430a24f19d`; client/device resources are
`6bfd5e7aa232134bbdc125b343cd9f5905ad35624759a1049b0ab8c4be6d5224` and
`0f678992a7845b80bfb046902b9ac50dd0bfe34cb0d6232db7a6e8f50ca64bd7`; final statuses are
`b7dd0ef92f2e4b2f5a0371f58f8a5ceefcebeaf7f644c6de709da9c80614c253` and
`7a219e26d0396745614d7de243bddf628cf18145c8841a5ebda51943e1c5e3c5`.
The audited cleaner reclaimed exactly the 2.4 GiB private raw root after strict export, and the
compact proof strictly reverified afterward.

## Rejected ADR 0164 forced-TCP sixty-four-stream qualification

Source commit: `0403ccc45d6f347d251e79a55afed57bb600ada0`

Proof: `.sandwurm/exports/pairs/pair.swij6mj9`

Scenario: forced TCP, `ratox-matrix-bulk-64`

Binary SHA-256: `dc69b043f3c5d023ada6ed748ef2656009a067978a383a1eaca4bae6ea166993`

This matched maximum-load cell uses the accepted ADR 0164 binary unchanged. It completes 1,000/1,000
terminal samples, keeps all 64 files present as one active plus 63 paused, advances every file by
2,177,148 to 3,206,769 bytes for 168,951,072 aggregate bytes, cancels all 64 to empty in one round,
closes, captures both resource intervals, and passes strict raw plus compact lifecycle verification.
It does not pass the common owner/miss qualification gates.

| Distribution | Minimum | p50 | p95 | p99 | Maximum | Mean |
|---|---:|---:|---:|---:|---:|---:|
| keypress to local render | 12.868 ms | 49.829 ms | 93.790 ms | 109.944 ms | 560.528 ms | 53.862 ms |
| keypress to controller OUTPUT | 12.826 ms | 49.530 ms | 93.488 ms | 109.534 ms | 560.473 ms | 53.666 ms |
| local OUTPUT to render | 0.034 ms | 0.091 ms | 0.798 ms | 1.743 ms | 3.154 ms | 0.196 ms |
| interactive owner wait | 0.002 ms | 0.018 ms | 0.512 ms | 2.199 ms | 5.442 ms | 0.114 ms |
| remote stage to commit | 0.600 ms | 2.156 ms | 4.238 ms | 5.160 ms | 31.201 ms | 2.458 ms |
| remote commit to output | 0.011 ms | 5.475 ms | 12.006 ms | 14.465 ms | 20.886 ms | 5.388 ms |
| remote stage to output | 0.632 ms | 7.567 ms | 15.579 ms | 19.442 ms | 31.222 ms | 7.846 ms |

Four hundred ninety-seven renders reach 50 ms, 27 reach 100 ms, and one reaches 250 ms. Exact owner
p99 is 2.199 ms, failing the strict less-than-2 ms common gate, and the one 560.528 ms render fails
the common miss gate. Forced-route p95 remains separately classified rather than compared to the
direct 50 ms target.

The receiver records 1,212 admissions, 1,183 rotations, 215 typed handoffs, and zero true failures.
Maximum fair wait is 3.486 seconds, all files progress after only 38 ms, and aggregate progress is
healthy. Client/device event high-water is 711/162 with zero required waits. Reactive pacing records
735/502 client pause/resume operations plus the 215 carrier handoffs and 1,071/1,070 device
pause/resume operations with zero failures. Forced TCP therefore reaches a high-pressure mode rather
than reproducing direct UDP's low-use stall.

The client interval lasts 61.713 seconds, uses 45.30 CPU-seconds (73.4% of one CPU), writes
1,203,093,504 bytes, moves from 98 to 34 descriptors, and grows from 10,356 to 11,636 KiB resident.
The device interval lasts 62.410 seconds, uses 54.24 CPU-seconds (86.9%), writes 1,135,370,240 bytes,
moves from 97 to 33 descriptors, and grows from 11,136 to 11,864 KiB with a 12,040 KiB high-water.

Compact allocation is 1,605,632 bytes. Compact export/pair manifests are
`98d6d4882f7019df8e42cb70c3b21f1467338c6b6069dd902fce1b67c902f8f5` and
`58d0e6c45e941a2f308e466e030a03e206b64f54c320588611649b0e6f7581bd`; client/device resources are
`474492183e561f4cdceb63e8ba9a66029758a370811a541adeeadb53a0214609` and
`8e3c11be489f2966c2f191a4f4c3c7ad1da8c1468717e6170998e2eed1924b82`; final statuses are
`81fc6037b363c2888031afccc3f1efa340c9167ca8d63b4faf88ab2c0e2493b2` and
`8d1725df7bf04d33008b8b182db38e07763c616a736227f04cb5e65aba9ea552`.
The audited cleaner reclaimed exactly the 2.4 GiB private raw root after strict export, and the
compact proof strictly reverified afterward.

## Interpretation and next gate

### Post-freeze one-stream regression

Source commit: `fc029f9cfd454ca67fccd1458698d5275b626f15`

Proof: `.sandwurm/exports/pairs/pair.zy91h9m3`

Scenario: direct UDP, `ratox-matrix-bulk-1`

Binary SHA-256: `05d7e844ffb78942060fb4414af5c3ac3ce4875a6e544b14039932ddb04b3abe`

After ADR 0165 froze 32 as the qualified single-Agent default, a clean two-guest regression again
completed 1,000/1,000 exact samples beside one live 1 GiB stream. Render
minimum/p50/p95/p99/maximum/mean was 4.267/22.816/41.671/50.394/77.333/24.219 ms; owner-wait p99 was
1.764 ms. Eleven renders reached 50 ms and none reached 100 or 250 ms. The file advanced
163,875,630 bytes and cancelled to empty in one round. Raw and compact strict verification passed;
compact allocation is 1,605,632 bytes. Compact export/pair manifest SHA-256 is
`d6a416511b28b3a83fc6b3f7706da514dcb8d9a4db5148ba4baa6bc2cc9822f5` and
`dbaedc1a225c3ce9371c75cda18d75d26abc5706cc7d9610f2bf26ed5755c2d2`. This is a regression check,
not an eleventh decision cell and not grounds to weaken any retained 64-stream failure.

ADR 0157 is accepted as a liveness repair: the exact prior failure point at sample 599 no longer
stalls and the cell closes. The cell is not an R7 latency pass. Because the owner queue itself misses
its target, the roadmap did not jump directly to a dedicated route. The exact ADR 0158 A/B then
proved that removing callback bookkeeping without replacement pacing is unsafe. ADR 0159 restores
required per-chunk events, retains the cheaper receive descriptor and diagnostics, and adds bilateral
final-status proof. The descriptor-only rerun still misses owner p99 and proves client-side event
saturation, selecting an explicit bounded file pacer. ADR 0160 meets both direct latency targets and
removes ordinary event saturation in the exact `bulk-1` rerun. Route isolation is therefore not
selected for that cell. ADR 0161 makes paced workload accounting exact at higher concurrency. Its
valid direct-UDP `bulk-8` rerun keeps owner p99 at 0.420 ms and event high-water below 140, yet render
p95 rises to 144.120 ms with one 250 ms miss and bilateral maximum pacing holds near 180 ms. The next
experiment is multi-transfer pause/resume fairness and burst desynchronization on the shared carrier,
not more Agent queue capacity. ADR 0162's activated A/B safely narrows the tail but does not meet the
latency gate. Its zero-activation replicate also exposes the deeper limitation: callback-event
pressure is not a carrier-load signal. The next experiment must proactively admit and fairly rotate
a bounded number of runnable file transfers per peer before toxcore's shared reliable carrier enters
either the high-CPU pacing state or the low-CPU starvation state. ADR 0163 now implements a
receiver-owned one-file window. Its first clean two-guest result strongly improves latency but misses
direct p95 by 6.247 ms and exposes typed ownership plus cancellation races between the proactive and
reactive layers. ADR 0164 gives already-paused transfers to the external owner, retains true failures,
makes only exact post-cancel events harmless, and accepts a 50 ms quantum. More Agent queue capacity
and Ratox framing changes remain rejected. The eight-, sixteen-, and thirty-two-stream route rows all
pass without load-dependent latency growth. At 64 streams, fairness survives but direct UDP enters a
low-throughput transport stall, while forced TCP enters a high-throughput pressure state and fails
owner/miss gates. ADR 0165 therefore freezes the existing 32-send/32-receive default as the qualified
single-Agent ceiling, keeps higher explicit values experimental, and leaves the frozen 64-stream R7
gate failed. Future aggregate capacity belongs in bounded excess-work/multi-route scheduling with new
two-route evidence, not in larger queues or Ratox framing changes.
