# Sandwurm fresh Ratox admission after content backlog — 2026-08-30

## Claim

A new Ratox terminal controller opens and becomes immediately usable after reliable completion of an
8 MiB cap-8 content-v2 transfer on the same authenticated IoTox session. Direct UDP and forced TCP
both send OPEN within one second of the exact content-completion boundary, receive canonical OPENED
within the ordinary five-second deadline, retain online epoch 1 and the expected carrier, start one
fresh terminal at generation/input/output position 1, and complete 40 exact echo/render/ACK samples.

This is one fixed-order observation per route in two Sandwurm VMs. It is not admission during active
bulk, a repeated distribution, a public-network result, or an argument for changing Ratox framing or
the default content-lane ceiling.

## Construction and verifier

`sync-content-ratox-post-bulk-admission` reuses the source-linked ADR 0263 lane workload: artifact
SHA-256 `6d85b492f8385941c8af029d21d2e9783df212550046f4dc1f4f397936934e5f`,
8,388,608 bytes, 24 chunks, 26 content objects, 4 Mbit/s subscriber shaping, one cap-8 process, and
signed namespace ceilings `1,2,4,8`. Before cap 8, the client proves three stable confirmed,
capability-bearing, claimant-authenticated observations on the expected carrier. Once cap 8 becomes
reliably complete, the next terminal operation is a new OPEN; no post-completion readiness poll may
pre-warm or delay admission.

The reusable probe emits `iotox-ratox-admission-evidence-v1`. The independent verifier requires exact
field order, monotonic timestamps and derived intervals, expected carrier, unchanged positive epoch,
fresh session shape, one capture digest, 40 ordered samples, and all three receipt digests. Compact
proofs contain 17 secret-free files and allocate 204,800 bytes each.

## Invocation

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-ratox-post-bulk-admission
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-ratox-post-bulk-admission

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.614f4nje \
  sync-content-ratox-post-bulk-admission
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.oengulmm \
  sync-content-ratox-post-bulk-admission
```

## Results

| Route | Cap-8 duration | Cap-8 rate | Completion to OPEN | OPEN to OPENED | Completion to OPENED | Echo RTT p50 | Echo RTT p95 | Echo RTT max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct UDP | 18,564 ms | 451,875 B/s | 148.942 ms | 41.131 ms | 190.073 ms | 16.371 ms | 18.137 ms | 21.395 ms |
| forced TCP | 21,970 ms | 381,821 B/s | 824.342 ms | 74.139 ms | 898.481 ms | 110.762 ms | 142.980 ms | 161.105 ms |

Both cells retain carrier-specific epoch 1 from the pre-backlog snapshot through the observation made
immediately after OPENED. Every terminal has generation 1, input sequence 1, output sequence 1, one
nonzero incarnation, one session commitment, and 40 consecutive samples. The new sessions are usable,
not merely admitted. TCP remains a materially slower interactive route class, consistent with the
idle and persistent-load evidence.

## Accepted bindings

Direct UDP compact proof `pair.614f4nje` binds:

- readiness/capture/admission SHA-256
  `fc283cd0dd1eff3c7f4e3fc98e99d2a13f866154f1e2ed014ef6e5d5bf4cbafa` /
  `3e48c9d2e48335f397df859da3d53dfd898523a1b1064fef5933686484b73616` /
  `c6612df4d2d0d47caaf71c1a0440dc0c84c10b4590900cb8b0c3b12f339982bf`;
- client/device receipt SHA-256
  `7d9f787797c20ba496242531a37178c12216857178982be6440ec24e8cc60861` /
  `fec219803300fd212f4c2241fca6a49c1a8a720081a02c093fe7e91ba0a2a05b`;
- pair-manifest SHA-256
  `9c638eeb1f7ae8fdcc69772daeaca1acb39643b9b34918919a37a529d4ae579b`; and
- compact-export SHA-256
  `760290b8060318d785467e4d20e046d1a1227b22c0c6cd1466b79deb2e042eaf`.

Forced TCP compact proof `pair.oengulmm` binds:

- readiness/capture/admission SHA-256
  `d29dc6a11fe9c26ae471c8bcba89950909d571d0a53a429c0cc9e55f73112a57` /
  `b9d5d8c956e675fda6522fa182bef7701c153dc3d0c942c8e26eba9c103749bd` /
  `e9dff5b9e2a18b3e4566cbb1a3cc285e91bdfd7a626dcf7535eac2977fffad1c`;
- client/device receipt SHA-256
  `229705a21729ebbb41b00a3f3f24b0c247e3d8e35848a7dcfedc07ff17f79027` /
  `f159533520b2b2ecdc63fab4e771285d65d65a8fe70d7cb335c6a56331fb086b`;
- pair-manifest SHA-256
  `ec606a902c1ec9321379cb1e946193e57e7af3941e7db6347bd3939197483249`; and
- compact-export SHA-256
  `b5c6ae957d7dc10bc2d8b1db55b0faf2fa588264f2ff85f10b62a28d76423b59`.

Both bind source-linked binary SHA-256
`8296219d64ece148355610a04a7b83a04c509fbaf61eabf4b16312a631f4b3a7`.

## Decision and next gate

Close fresh post-bulk OPEN admission for the controlled native carriers and keep Ratox framing frozen.
The earlier failure is retained as rejected harness evidence, not a product failure. Next, reverse and
repeat lane/load order before selecting an automatic bulk profile; separately test admission during
active reliable backlog only if the product requires that stronger lifecycle promise.
