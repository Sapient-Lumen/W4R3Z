# Sandwurm content lane-count science — 2026-08-30

## Claim

One stable IoTox subscriber can consume the same 8 MiB content-v2 revision with signed effective
lane ceilings `1`, `2`, `4`, and `8` over both direct UDP and forced TCP. Every cell reaches its
ceiling, converges the exact object graph, and activates the signed HEAD. Under the founding-host
4 Mbit/s shaped fixture, forced TCP improves through four lanes and then plateaus; direct UDP is
non-monotonic and does not justify a default change.

This is one ordered observation per route on two Sandwurm guests on the founding host. It is not a
confidence interval, physical-host result, Internet benchmark, byte-striping result, or proof that
more lanes preserve Ratox latency.

## Construction

The `sync-content-lane-science` scenario uses the repository's reused immutable private identity
baseline and source-linked c-toxcore 0.2.23 binary. The publisher deterministically generates one
high-entropy 8 MiB artifact with SHA-256
`6d85b492f8385941c8af029d21d2e9783df212550046f4dc1f4f397936934e5f`.
Its content-v2 graph has 24 chunks, one page, and 26 objects.

The subscriber starts once with process ceiling 8. Four separately published namespaces have
independent CAS roots and signed lane/outstanding-request ceilings `1/1`, `2/2`, `4/4`, and `8/8`.
The fixed phase order is `1,2,4,8`; no daemon restarts or reconnects occur between cells. Each phase
begins a fresh process-resource interval immediately before `sync-pull`, observes coherent admitted
non-root lane rows against one source, stops duration at content completion, then explicitly
activates and verifies the artifact from that namespace root. Subscriber ingress is shaped to
4 Mbit/s by the pair runner.

The first harness draft restarted the subscriber between caps. Direct UDP completed, but forced TCP
spent more than eight minutes reacquiring the relay session before cap 2, making reconnection the
dominant variable. That trial was stopped and is not accepted evidence. The final contract requires
zero phase restarts and varies only signed namespace policy.

## Invocation

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-lane-science
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-lane-science

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.amcrp0_3 \
  sync-content-lane-science
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.805kzu4a \
  sync-content-lane-science
```

## Results

| Route | Cap | Duration | Artifact rate | Relative to cap 1 | Max live lanes | User/system ticks | HWM KiB | Transport iterations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct UDP | 1 | 22,190 ms | 378,035 B/s | baseline | 1 | 132 / 194 | 12,604 | 15,115 |
| direct UDP | 2 | 25,750 ms | 325,771 B/s | -13.825% | 2 | 199 / 414 | 13,244 | 8,761 |
| direct UDP | 4 | 20,980 ms | 399,838 B/s | +5.767% | 4 | 143 / 278 | 13,500 | 12,197 |
| direct UDP | 8 | 18,930 ms | 443,138 B/s | +17.221% | 8 | 140 / 204 | 13,884 | 15,511 |
| forced TCP | 1 | 27,830 ms | 301,423 B/s | baseline | 1 | 159 / 300 | 12,672 | 14,107 |
| forced TCP | 2 | 22,320 ms | 375,833 B/s | +24.686% | 2 | 135 / 278 | 13,312 | 11,626 |
| forced TCP | 4 | 19,950 ms | 420,481 B/s | +39.499% | 4 | 127 / 183 | 13,568 | 16,430 |
| forced TCP | 8 | 20,210 ms | 415,072 B/s | +37.704% | 8 | 147 / 215 | 14,080 | 16,428 |

The direct result is noisy and non-monotonic. The forced-TCP result has a useful knee at cap 4:
cap 8 is 1.286% slower than cap 4 while reaching the higher live-lane count. HWM rises modestly in
both routes, but CPU and transport-iteration counts are not monotonic in this single sample and are
retained as observations rather than causal claims.

## Accepted bindings

Both compact roots contain 14 secret-free files, allocate 188,416 bytes, and bind source-linked
binary SHA-256 `8296219d64ece148355610a04a7b83a04c509fbaf61eabf4b16312a631f4b3a7`.

Direct UDP compact proof `pair.amcrp0_3` binds:

- lane summary SHA-256
  `709c6535fedc160d77a872217ea46076663baa387e713d0b406b5aeb8b6badd1`;
- client receipt SHA-256
  `afe0f3284c0849235e9b8682d974156092f151c5ddd2d48c45a7a0ef68f80248`;
- device receipt SHA-256
  `4edd3b4b01daa54addc0274c4903b742da547878a2a53c6b8e35366f9e88c735`;
- pair-manifest SHA-256
  `126c90c1c5abc43b311fbd63a1dd6525abfcc69b1f17432c23ccbc8b8864ea64`; and
- compact-export SHA-256
  `f230dd7c533815525b8c571c62cbfed15cbf96a55c4ad30b464ec88577293465`.

Forced TCP compact proof `pair.805kzu4a` binds:

- lane summary SHA-256
  `394c6a2d5247239d91392157f0f2bd56119e39dc5ec3499d265a677f587b2706`;
- client receipt SHA-256
  `8cc634b69fd17890af65765136b4b594e47369d8be921c9884569565adf483b7`;
- device receipt SHA-256
  `2300b9beafb125102136c2fcdd7c16a6c01c0ac3d245c73f60117bfb9672fcc7`;
- pair-manifest SHA-256
  `a8e70b0dd135b735b1fdc9705a383b7dd37884e32e1c0dd673a819305ba51675`; and
- compact-export SHA-256
  `b41525956ae3675eb47e81c271cfd5e1d108fd6030bc5e2a9edaecfac31eb1f8`.

The independent verifier checks exact route/connection mode, reused identity continuity, artifact
and HEAD bindings, zero phase restarts, four activations, requested-cap bounds, per-phase throughput
arithmetic, all resource-interval digests, summary/receipt agreement, and compact inventory.

## Decision and next gate

Keep the product default at one lane. Cap 4 is the smallest promising forced-TCP bulk profile, not a
new default. Repeat the cells with counterbalanced phase order before treating the observed rates as
stable estimates. More importantly, run cap 1 versus cap 4 (and cap 8 as a stress bound) while Ratox
terminal probes share the same shaped session. A bulk gain is acceptable only if p95/p99 terminal
latency and tail stalls remain within an explicitly frozen budget. Multi-lane daemon-restart
recovery remains separately unqualified.
