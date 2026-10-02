# Sandwurm content/Ratox latency science — 2026-08-30

## Claim

One authenticated Ratox terminal attachment remains exact and usable while the same IoTox client
consumes an 8 MiB content-v2 revision at signed lane caps 1, 4, and 8 over direct UDP and forced TCP.
All 720 keypress bytes return and render in order under one terminal-session identity and one Tox
online epoch; all content phases converge and explicitly activate. Cap 2 remains a transfer-only
control while the persistent probe is paused.

This is one fixed-order observation per route in two Sandwurm VMs on a busy founding host. It is not
a confidence interval, latency SLA, physical-host result, Internet benchmark, proof of byte
striping, or proof that a fresh Ratox session can always open behind reliable bulk backlog.

## Construction

The `sync-content-ratox-latency-science` scenario reuses the immutable private identity baseline and
the same source-linked binary and deterministic artifact as ADR 0263. The artifact SHA-256 is
`6d85b492f8385941c8af029d21d2e9783df212550046f4dc1f4f397936934e5f`; its content-v2 graph has
24 chunks and 26 objects. Subscriber ingress remains shaped to 4 Mbit/s.

One client starts with process lane ceiling 8. Four isolated namespaces sign effective lane and
outstanding-request ceilings 1, 2, 4, and 8. A single 720-sample Ratox probe requests one byte every
100 ms, pauses after samples 240 and 480, and resumes only when the harness releases the next phase.
Caps 1, 4, and 8 each own one exact 240-row segment and begin only after the segment's first echo has
completed. Cap 2 transfers while the attachment is paused. Readiness before every measured phase
requires three stable authenticated observations with the exact expected carrier and unchanged
online epoch.

The verifier hashes the one timeline, requires exactly one session commitment across all 720 rows,
reconstructs overlap from monotonic timestamps, independently calculates nearest-rank percentiles,
joins content duration/rate/lane truth to the ordinary content-science receipt, and checks Ratox
resource boundaries `0->1`, `1->1`, `1->1`, `1->0` across caps 1/2/4/8.

## Invocation

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-ratox-latency-science
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-ratox-latency-science

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.af873531 \
  sync-content-ratox-latency-science
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.a3nglkh3 \
  sync-content-ratox-latency-science
```

## Results

| Route | Cap | Duration | Artifact rate | Relative to cap 1 | Max lanes | Overlap samples |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| direct UDP | 1 | 21,750 ms | 385,683 B/s | baseline | 1 | 97 |
| direct UDP | 2 | 19,600 ms | 427,990 B/s | +10.969% | 2 | probe paused |
| direct UDP | 4 | 19,041 ms | 440,555 B/s | +14.227% | 4 | 63 |
| direct UDP | 8 | 22,424 ms | 374,090 B/s | -3.006% | 8 | 81 |
| forced TCP | 1 | 32,271 ms | 259,942 B/s | baseline | 1 | 100 |
| forced TCP | 2 | 20,680 ms | 405,638 B/s | +56.049% | 2 | probe paused |
| forced TCP | 4 | 20,066 ms | 418,050 B/s | +60.824% | 4 | 58 |
| forced TCP | 8 | 21,084 ms | 397,866 B/s | +53.060% | 8 | 48 |

| Route | Cap | p50 | p95 | p99 | Maximum | Queue p95 | Queue max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct UDP | 1 | 127.555 ms | 258.241 ms | 1,084.973 ms | 1,084.973 ms | 0.069 ms | 0.703 ms |
| direct UDP | 4 | 53.522 ms | 815.429 ms | 1,035.088 ms | 1,035.088 ms | 0.097 ms | 0.832 ms |
| direct UDP | 8 | 26.560 ms | 880.790 ms | 2,029.456 ms | 2,029.456 ms | 0.074 ms | 1.345 ms |
| forced TCP | 1 | 171.052 ms | 412.735 ms | 835.052 ms | 1,245.082 ms | 3.069 ms | 15.030 ms |
| forced TCP | 4 | 231.526 ms | 525.400 ms | 562.955 ms | 562.955 ms | 1.226 ms | 1.493 ms |
| forced TCP | 8 | 256.879 ms | 739.272 ms | 784.838 ms | 784.838 ms | 1.102 ms | 2.417 ms |

Direct UDP content rate peaks at cap 4 and falls 15.087% at cap 8. Forced TCP likewise peaks at cap
4 and falls 4.828% at cap 8. Interactive p95 worsens from cap 4 to cap 8 on both routes. The small
owner-queue measurements compared with end-to-end latency place most observed delay beyond local
owner-command scheduling; carrier and host effects are not separated by this experiment.

The cap-1 phase-transition delay was 554 ms on direct UDP and 2,647 ms on forced TCP; later releases
were 161--172 ms. These are bounded construction observations, not session-admission deadlines.

## Accepted bindings

Both compact roots contain 18 secret-free files and allocate 270,336 bytes. They bind source-linked
binary SHA-256 `8296219d64ece148355610a04a7b83a04c509fbaf61eabf4b16312a631f4b3a7`.

Direct UDP compact proof `pair.af873531` binds:

- latency summary SHA-256
  `1ef51dd5596087c9020bdadc773da1a6cec996e7461d89ee6fddb600935bba55`;
- 720-sample timeline SHA-256
  `19e4853cf0372d0d3fca51ee049d38104298986c38a6022f16186ac82e7069a9`;
- client/device receipt SHA-256
  `d9a070228a39405abccd6e3fc822d9a505522faae64710c1118668c0c47d4036` /
  `992a58d18c106baf3b05df72619440256a2ab20b5ec8e4cdd883a0ad317c8169`;
- pair-manifest SHA-256
  `de71cd55340e048e76e8c5b13139959c1ed5ac31afc6e1ec7245bd991602615a`; and
- compact-export SHA-256
  `a170da84725b8f72c37a8e988a58dc8b4dc1b693774605c818409de6d649aa21`.

Forced TCP compact proof `pair.a3nglkh3` binds:

- latency summary SHA-256
  `6b549b91b46f2dc66fbb9d6edbc33cd3ee20e2a038fdcb093e354ad214656774`;
- 720-sample timeline SHA-256
  `eeee305c99a50ed533216c102000a53e701d1b0cf592e428f774a753025fb26f`;
- client/device receipt SHA-256
  `68f7d215631ba275f4e666a27cf84e55f13529ffea74e972bc0d43b401fce508` /
  `3e9a0199c91d949d79ec867171a18cb201e8f48436a02acd56704a5011d9dcd8`;
- pair-manifest SHA-256
  `b290234e8be3c59b062d89d0032b60314c44dc8a8d6345e08b26f18b0ee3aeaa`; and
- compact-export SHA-256
  `9a3e802627450506ea3a2c4ac761c10f27198ac18d204a1a542893560d47330e`.

## Rejected construction attempts

The initial multi-session harness completed cap 1 and the cap-2 transfer before fresh cap-4 Ratox
OPEN attempts failed or exceeded their receive deadline. Those roots are not accepted evidence.
They reveal a separate fresh-session-after-bulk admission question and selected the persistent
timeline design.

The first persistent-timeline VM run exposed a Bash rendering error in the guest harness's
associative-array assignment. The client service exited and the local probe observed a broken pipe.
The product protocol was not implicated; the assignment was repaired and the generated Nix service
was syntax-checked before the accepted reruns.

## Decision and next gate

Keep the default at one lane. Cap 4 is the only current explicit bulk-profile candidate; cap 8 is
not a latency-sensitive default candidate. Repeat counterbalanced phase orders before treating
throughput or latency as a distribution. Separately qualify fresh Ratox admission behind completed
bulk backlog and multi-lane daemon-restart recovery. If the tail persists, test application-level
content pacing/reservation without changing frozen Ratox framing.
