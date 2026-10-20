# Sandwurm content/Ratox cap-two SLA — 2026-08-31

## Claim

One already-attached Ratox terminal meets the predeclared cap-two raw-echo construction SLA while
the same subscriber consumes an 8 MiB content-v2 revision over direct UDP and forced TCP. All 960
keypress bytes return and render in order under one terminal identity and one Tox online epoch; all
four ordered content phases converge and explicitly activate.

The SLA was frozen before either VM cell ran: at least 40 exact overlap samples, p50 at most 250 ms,
p95 at most 500 ms, p99 at most 1,000 ms, maximum at most 1,500 ms, and owner-queue p95 at most
10 ms. The same constants apply to both carriers.

This is a local two-VM, 4 Mbit/s shaped, already-attached raw-echo result. It is not an Internet,
physical-host, fresh-admission, bandwidth-independent, routed-privacy, or long-duration SLA.

## Frozen construction

The `sync-content-ratox-cap-2-sla` scenario reuses the immutable private identity baseline, the
source-linked final-tree binary, and the deterministic high-entropy artifact from ADRs 0263--0267.
The artifact SHA-256 is
`6d85b492f8385941c8af029d21d2e9783df212550046f4dc1f4f397936934e5f`;
it contains 8,388,608 bytes, 24 chunks, one manifest page, and 26 physical content objects.
Subscriber ingress remains shaped to 4 Mbit/s.

Four isolated namespaces sign effective caps `1,2,4,8`. A single 960-sample probe requests one byte
every 100 ms and pauses after rows 240, 480, and 720. Each release occurs only after three stable
confirmed/capable/authorized observations on the expected carrier. Each 240-row phase begins after
its first terminal response and before its content pull, then retains only rows whose input timestamp
falls inside the exact content interval. Process resources bind Ratox-active transitions `0->1`,
`1->1`, `1->1`, and `1->0` across the four content phases.

The guest checks the frozen cap-two constants. The host verifier independently reconstructs the
timeline, nearest-rank percentiles, session commitment, capture digest, content duration/rate/lane
truth, resource transitions, online epoch, receipt inventory, and compact-export allowlist.

## Invocation and replay

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-ratox-cap-2-sla
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-ratox-cap-2-sla

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.rpblreul \
  sync-content-ratox-cap-2-sla
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.rwiyixfh \
  sync-content-ratox-cap-2-sla
```

Each compact root contains 18 secret-free files, allocates 294,912 bytes, and independently returns
`status=passed`. Both bind binary SHA-256
`531dfb224e133b3fc0735455f1a5d077c02dbf6a6c2a91b0e0d85f766321d5b6`.

## Results

| Route | Cap | Duration | Rate | Overlap | p50 | p95 | p99 | Max | Queue p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct UDP | 1 | 20,616 ms | 406,897 B/s | 90 | 119.233 ms | 302.428 ms | 547.939 ms | 547.939 ms | 0.159 ms |
| direct UDP | 2 | 20,065 ms | 418,071 B/s | 83 | 83.680 ms | 479.100 ms | 876.158 ms | 876.158 ms | 0.298 ms |
| direct UDP | 4 | 19,845 ms | 422,706 B/s | 59 | 69.400 ms | 970.865 ms | 1,120.360 ms | 1,120.360 ms | 0.506 ms |
| direct UDP | 8 | 18,869 ms | 444,570 B/s | 32 | 106.303 ms | 1,836.902 ms | 1,929.880 ms | 1,929.880 ms | 1.311 ms |
| forced TCP | 1 | 22,967 ms | 365,246 B/s | 97 | 135.502 ms | 292.475 ms | 610.902 ms | 610.902 ms | 0.119 ms |
| forced TCP | 2 | 20,894 ms | 401,484 B/s | 68 | 199.264 ms | 401.813 ms | 531.662 ms | 531.662 ms | 0.083 ms |
| forced TCP | 4 | 20,314 ms | 412,947 B/s | 62 | 220.301 ms | 523.960 ms | 696.405 ms | 696.405 ms | 0.410 ms |
| forced TCP | 8 | 20,517 ms | 408,861 B/s | 55 | 233.623 ms | 553.267 ms | 836.610 ms | 836.610 ms | 1.364 ms |

Cap two passes every frozen bound on both carriers. In the same ordered cells, cap four and cap eight
both miss the 500 ms p95 ceiling on both carriers. Cap two improves rate over cap one by 2.75% on
UDP and 9.92% on TCP; cap four adds only another 1.11% and 2.86%, respectively, while failing the
interactive threshold.

The owner-queue p95 is 0.298 ms on UDP and 0.083 ms on TCP at cap two. As in ADR 0264, most measured
tail delay lies beyond local owner-command scheduling. This experiment does not assign the remainder
to one toxcore, reliable-channel, kernel, host, or network cause.

## Exact bindings

| Proof | Route | Summary SHA-256 | Timeline SHA-256 | Client receipt | Device receipt |
| --- | --- | --- | --- | --- | --- |
| `pair.rpblreul` | UDP | `86a7b75dbd49fc13036020cacd7b8b8c37af38c183a5ec1f43cce06502a0eb35` | `76a4c8309179fa1215a69436c97bbb46c0c5c0a08e5f3c4ba210441f45ca051f` | `c1df8e527697007da7747b544e51e23d6160e6e5b2c731bac7e3f1a9c68a3d9e` | `a4917163bae40d783f2f40a29bf050a82782d7acac6610c917e917a44a90cb59` |
| `pair.rwiyixfh` | TCP | `624e3ac18caecd79b011a2f641c2f78f5d035a72cea9e81948ce975f02b28173` | `07db5380fb75ada2d9e66eca14faa47aa3f3f8082a4a46c1b2ea4567b34901a2` | `26d6e2e2b4c97556962997a3723cb7b1995ef6a4fa40430473abca3213683ae5` | `7c4e777c29db86c5404c5ee7860545dc39b50e3a7191357d67fc3e26059de089` |

Direct UDP source pair-manifest SHA-256 is
`53150e6c8992c5272f6db3df52cc21a49430f97547e5095507c43b621707c9e1`; compact-export SHA-256 is
`545b0fd9c3346b8ce442a63b73e1fb4daa85c199dfcd836959cae5cad6c2338d`.
Forced TCP source pair-manifest SHA-256 is
`56f82e00fb1feaa1113443306f62eb0f13fcb6fb7585952ad3a6db7c6ec3e5f4`; compact-export SHA-256 is
`f20fe1d36d453ccb32f3266bcf1ab8162393417d3a274c77ff2da3f41b50fb3d`.

## Decision and nonclaims

Keep default one. Explicit cap two is the bounded native interactive-bulk construction profile under
the tested 4 Mbit/s shaping; it is never selected automatically. Cap four remains a controlled
direct-UDP throughput option only when this interactive SLA is not required. Cap eight remains
stress-only.

These two same-host VM cells do not establish a confidence interval, Internet or physical-host
latency, faster/unshaped-link behavior, Tor/I2P behavior, multiple terminal fairness, local echo,
fresh OPEN during active bulk, arbitrary payload distributions, or a permanent product-wide SLA.
See ADR 0268.
