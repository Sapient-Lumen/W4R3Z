# Sandwurm Ratox bounded route-impairment evidence

Date: 2026-08-27

Status: accepted two-guest bounded-impairment evidence; not total-loss recovery, automatic migration,
actual Tor, or a latency service-level objective

## Claim

Two simultaneous source-linked IoTox guests kept one authorized Ratox terminal attachment and its
PTY session identity alive through 120 exact observations over each of direct UDP, forced TCP, and
strict generic SOCKS. Samples 1–20 establish a local baseline. Samples 21–100 cross independently
seeded `netem delay 75ms 15ms loss 2%` qdiscs on both guest TAP egress paths. Samples 101–120 follow
exact qdisc removal. Every sample completes one Ratox PING/PONG and then one PTY byte/echo through the
installed private terminal controller.

All three cells completed without detach, resume, route migration, session reopen, sequence gap, or
identity change. Both TAPs recorded positive packet drops in every impaired cell. The strict SOCKS
cell additionally retained 2,624 IPv4 guest-egress packets: every packet was TCP to the configured
proxy, with zero UDP, direct-bootstrap, or direct-peer packet and zero denied SOCKS admission.

The six guests bind source revision `f5d526c8c7461277b7ad57277fc5ee2177c59386` and identical binary
SHA-256 `511b29744b5e0477e8da3277e109c998b030fb1d5890aebde3bddab28d41936f`.

## Measurements

Times below are median / nearest-rank p95 / maximum in milliseconds. Each baseline and recovery row
contains 20 samples; each impaired row contains 80.

| Route | Phase | Ratox heartbeat | PTY input-to-output |
|---|---|---:|---:|
| direct UDP | baseline | 11.063 / 12.634 / 13.283 | 16.331 / 16.521 / 16.582 |
| direct UDP | impaired | 165.327 / 210.737 / 291.541 | 176.650 / 434.486 / 2,157.729 |
| direct UDP | recovery | 6.131 / 11.206 / 13.010 | 16.334 / 18.256 / 18.279 |
| forced TCP | baseline | 46.640 / 52.180 / 87.679 | 49.546 / 93.138 / 94.459 |
| forced TCP | impaired | 324.064 / 396.669 / 658.955 | 289.133 / 540.188 / 666.877 |
| forced TCP | recovery | 46.459 / 51.772 / 52.068 | 46.996 / 53.087 / 93.142 |
| strict SOCKS | baseline | 47.181 / 53.862 / 97.141 | 52.791 / 89.817 / 89.977 |
| strict SOCKS | impaired | 304.005 / 561.421 / 668.195 | 277.522 / 380.984 / 619.354 |
| strict SOCKS | recovery | 47.026 / 87.947 / 227.769 | 46.958 / 52.300 / 52.472 |

The impaired median heartbeat/terminal multipliers over local baseline were 14.944/10.817 for
direct UDP, 6.948/5.836 for forced TCP, and 6.443/5.257 for strict SOCKS. Those ratios include the
configured artificial delay and the scenario's sequential heartbeat-before-PTY schedule; they are
not cross-network throughput rankings.

The Agent-side measurements stay far below the network observations:

| Route | Impaired local-render median / p95 / max | Impaired interactive-queue median / p95 / max |
|---|---:|---:|
| direct UDP | 0.084 / 0.886 / 6.199 ms | 0.015 / 0.060 / 0.150 ms |
| forced TCP | 0.064 / 0.161 / 0.629 ms | 0.013 / 0.051 / 0.255 ms |
| strict SOCKS | 0.068 / 0.147 / 0.771 ms | 0.013 / 0.086 / 0.200 ms |

This locates the large observed tails in carrier/retransmission behavior rather than ordinary
interactive queueing. Direct UDP's 2.158-second PTY maximum also shows why a heartbeat and PTY
progress cannot be treated as interchangeable or why a single delayed sample cannot safely trigger
session mutation.

| Route | Impairment active | TAP packets / drops | Compact proof |
|---|---:|---:|---|
| direct UDP | 34.009 s | 1,238 / 18 | `pair.tscy1yrt` (372 KiB allocated) |
| forced TCP | 51.737 s | 1,303 / 19 | `pair.gf5mxexc` (372 KiB allocated) |
| strict SOCKS | 49.741 s | 1,313 / 19 | `pair.p3dt6g9c` (1.7 MiB allocated) |

## Evidence binding

| Route | Manifest SHA-256 | Terminal capture SHA-256 | Heartbeat capture SHA-256 |
|---|---|---|---|
| direct UDP | `6dcda45fc3c4c69b4f4b243367c017c9a4456f4908ec45d6a7ae10a6d6ea9812` | `f16d00577ea90753410912432b5bc88422abcfc6d5b93e1c9f2febbec30ce4d6` | `37bb2ec09af199dac3e141dd8be9a9923da52532aef7db53ca6d97f260708ce0` |
| forced TCP | `acd40e9b188f522427a3581f7fee05f60d27fe38fe3c93a54ba0d88a8015a2dc` | `ecd7c0aba9a1f9564acdfd006910b5c49ca9845d48b299c429830b285969da83` | `61c8495d0754d4e0ee779b6232042fe4e6027504588de87701af3458ecc181d2` |
| strict SOCKS | `a0dcda3f11e9d579557b4f891a57143e7317eba4f54e4005ac6d9d2fb8f894d7` | `aa213abdf3434ac7988816c4b525059d133704a35c57ede193b250123a5068ea` | `467060277f1ec2d98dedd8dc630001669c5602d650e3c880ccda388c6028f0d9` |

Each private raw proof was independently verified, exported through the scenario-specific allowlist,
and independently reverified before the multi-gigabyte guest disks and private state were removed.
The ignored compact roots remain under `.sandwurm/exports/pairs/` and contain the canonical receipts,
captures, launch chain, and omission inventory needed by the verifier, not keys or guest disks.

## Reproduction and verification

Run the three exact cells:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-route-impairment
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-route-impairment
./tools/iotox-sandwurm-lab.sh up-pair tox-tor ratox-route-impairment
```

For each returned private `PROOF_ROOT`, verify and compact it before cleanup:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair ROUTE PROOF_ROOT ratox-route-impairment
python3 tools/export-sandwurm-pair.py PROOF_ROOT
python3 tools/verify-sandwurm-pair.py \
  --route ROUTE --scenario ratox-route-impairment COMPACT_ROOT
```

Then recheck the measurement-specific schema and regenerate exact statistics:

```sh
python3 tools/analyze-ratox-route-impairment.py \
  .sandwurm/exports/pairs/pair.tscy1yrt \
  .sandwurm/exports/pairs/pair.gf5mxexc \
  .sandwurm/exports/pairs/pair.p3dt6g9c
```

## Exact nonclaims

This is one construction host, one pair of guests per cell, one provider build, one impairment
profile, one short sequential run, and one sample per route. It does not establish a latency SLO,
capacity distribution, total-outage behavior, detached PTY retention, automatic route migration,
multi-route session handoff, Mosh-style state synchronization, fairness under concurrent bulk load,
or production hardware behavior. The `tox-tor` cell is strict generic SOCKS containment through the
laboratory forwarder, not actual Tor, anonymity, circuit evidence, or a two-IoTox public-network
route. The separate operator-Tor gate cannot be combined with this cell to claim an unrun topology.
