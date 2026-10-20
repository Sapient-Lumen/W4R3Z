# Sandwurm content lane counterbalance — 2026-08-31

## Claim

One finalized Sandwurm harness passes both `1,2,4,8` and `8,4,2,1` signed content-lane orders over
direct UDP and forced TCP. All four compact proofs independently verify the exact same source-linked
IoTox binary, immutable identity baseline, 8 MiB content graph, one-session process lifetime, four
activations, and zero restarts.

The paired construction data support cap 2 as the efficient explicit mixed/relay-heavy bulk setting,
cap 4 as the fixed-direct-UDP throughput setting, and cap 8 only as a stress bound. The product
default remains one. This is an order-balanced two-sample distribution per carrier, not a confidence
interval, physical-host benchmark, public-network result, or automatic-profile qualification.

## Frozen construction

The publisher generates artifact SHA-256
`6d85b492f8385941c8af029d21d2e9783df212550046f4dc1f4f397936934e5f`, exactly 8,388,608 bytes,
24 chunks, one manifest page, and 26 content objects. The subscriber process ceiling is eight. The
base namespace is signed at the first cap in each order; three isolated roots are signed for the
remaining caps. The process, authenticated Tox session, artifact, object graph, source, 4 Mbit/s
subscriber shaping, and activation rules remain fixed.

The ascending scenario is `sync-content-lane-science`; the descending scenario is
`sync-content-lane-science-reverse`. Every phase observes one source, distinct request/FileId rows,
no root lane, an exact maximum equal to the signed cap, complete content, explicit activation, and a
fresh resource interval.

The first TCP attempt after generalizing the harness was rejected before transfer science. It
redundantly republished the already-packed initial cap and the publisher exited with CLI status 3
during the extra setup work after emitting cap-1/cap-2 temporary HEAD evidence. That root is not
accepted data. The finalized harness reuses the already-signed base HEAD and publishes only the
three counterphases. Both final orders per carrier use that implementation.

## Invocation

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-lane-science
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-lane-science-reverse
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-lane-science
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-lane-science-reverse

python3 tools/analyze-content-lane-counterbalance.py \
  .sandwurm/exports/pairs/pair.t6b6exf1 \
  .sandwurm/exports/pairs/pair.ku2fxml0 \
  .sandwurm/exports/pairs/pair.70p2plez \
  .sandwurm/exports/pairs/pair.o_6q_m1n \
  --verify-report artifacts/rev0045/content-lane-counterbalance.json
```

The analyzer returns `content-lane counterbalance report verification: PASS` only after the strict
pair verifier accepts every root and the recomputed canonical JSON exactly matches the retained
report.

## Exact order results

| Route/order | Cap 1 | Cap 2 | Cap 4 | Cap 8 |
| --- | ---: | ---: | ---: | ---: |
| direct UDP ascending | 410,200 B/s | 417,967 B/s | 434,642 B/s | 446,915 B/s |
| direct UDP descending | 403,686 B/s | 428,427 B/s | 444,311 B/s | 439,194 B/s |
| forced TCP ascending | 300,021 B/s | 359,255 B/s | 354,698 B/s | 286,790 B/s |
| forced TCP descending | 291,777 B/s | 382,343 B/s | 354,548 B/s | 301,423 B/s |

The row presentation is cap-sorted; the retained TSV order is genuinely descending in each reverse
proof.

| Route | Cap | Mean artifact rate | Mean CPU ticks | Mean HWM KiB |
| --- | ---: | ---: | ---: | ---: |
| direct UDP | 1 | 406,943 B/s | 253.5 | 13,184 |
| direct UDP | 2 | 423,197 B/s | 286 | 13,248 |
| direct UDP | 4 | 439,476.5 B/s | 297.5 | 13,376 |
| direct UDP | 8 | 443,054.5 B/s | 361 | 13,312 |
| forced TCP | 1 | 295,899 B/s | 425.5 | 13,440 |
| forced TCP | 2 | 370,799 B/s | 407 | 13,440 |
| forced TCP | 4 | 354,623 B/s | 515.5 | 13,504 |
| forced TCP | 8 | 294,106.5 B/s | 747 | 13,824 |

Direct UDP's cap 8 mean exceeds cap 4 by 0.814%, but uses 21.345% more CPU ticks. Forced TCP's cap 2
mean exceeds cap 4 by 4.562% and uses 21.048% fewer CPU ticks. Across all four route/order samples,
cap 4 averages 397,049.75 B/s and cap 2 averages 396,998 B/s: a 51.75 B/s or 0.013% cap-4 edge.
Cap 2 uses 346.5 mean CPU ticks versus cap 4's 406.5, 14.760% fewer.

These observations are internally consistent with ADR 0264: cap 8 is not a latency-sensitive
candidate. They do not fill ADR 0264's missing simultaneous-Ratox cap-2 row.

## Accepted bindings

Every compact root contains 14 secret-free files including `compact-export.json`, allocates 192,512
bytes, and binds IoTox binary SHA-256
`8296219d64ece148355610a04a7b83a04c509fbaf61eabf4b16312a631f4b3a7`.

| Proof | Route/order | Summary SHA-256 | Pair manifest SHA-256 | Compact export SHA-256 |
| --- | --- | --- | --- | --- |
| `pair.t6b6exf1` | UDP ascending | `955651ced1db164b8019b9972c518bca684633276554b5ddf8bb2ff5f673e76f` | `272862f53dfbdfab6afc2f8c160b86a843970c4dea36c860add1a522696c91fa` | `9404b21636d8ff3692f7e40fffa7f8abf35cd9387838e7e6414071d3a685b1e6` |
| `pair.ku2fxml0` | UDP descending | `a913852ffbba20314ec5ace44388be935eea75ed96c57f5e8f2a31e83cf8111b` | `cab8f9a275a806ad77804be1c5534c0794a68cf6269991cfb143f46864141aab` | `ed2ccd5fa62d11dbf27a713ff653b01875e48a44c7da8540c75414f3525000be` |
| `pair.70p2plez` | TCP ascending | `85c693193ce2dc73be5e356283c5a50c275386ddd4a23c09f4d4e055b8ea94f7` | `f72ce9a648a83a77d192fe74ad4fc9f833a77b7750c7d11573c39bd0eff21a4f` | `1f259bf9d17084e9e60ec25df2b9c24d6152a6c0ac254e56043690ac6fee35f7` |
| `pair.o_6q_m1n` | TCP descending | `01e1de848b16b93ee56e9b58dd4a3137c62c62e2e9f783876c5fe2748c3a0fd0` | `cb9a8b5a0e1bfd27edfdb64f97238203b1bad9ddd7d546aef0df4665000dba58` | `d15c63157f11aeb5ced94deaac7a9cfa86db1c1d72efe53efee257f4449c3b69` |

The canonical 21,079-byte report has SHA-256
`91ed161964e6a190e59ac6e976db6565fd93af44591ffb786aa6eea5f763d1e5` and is bound by
`artifacts/rev0045/SHA256SUMS`.

## Decision and remaining gates

Keep the default process cap at one. Recommend explicit cap 2 for latency-insensitive
mixed/unknown/relay-heavy bulk and cap 4 for controlled fixed direct UDP. Do not recommend cap 8.
Do not implement automatic route selection from this evidence.

Before any interactive bulk profile, measure cap 2 with a persistent Ratox attachment and freeze an
interactive SLA. Separately qualify client-daemon restart with multiple active content lanes and
same-source object distribution over independently authenticated auxiliary paths. Later repeated
pairs may enlarge this analyzer's distribution, but this four-proof corpus alone establishes no
confidence interval, Internet behavior, physical diversity, or fleet default.

## Later qualification

ADR 0267 later closes the multi-lane client-restart gate. ADR 0268 closes the cap-two persistent-
Ratox gate against a threshold frozen before either carrier cell; compact proofs `pair.rpblreul`
and `pair.rwiyixfh` pass. The remaining scheduler gate from this section is same-source object
distribution over independently authenticated auxiliary paths.
