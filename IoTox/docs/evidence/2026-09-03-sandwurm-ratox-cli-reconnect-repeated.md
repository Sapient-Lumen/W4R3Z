# Sandwurm repeated production-CLI Ratox reconnect evidence

Date: 2026-09-03

Status: accepted bounded repeated-loss evidence on direct UDP and forced TCP

## Claim

One real `iotox terminal PEER --reconnect` process retained one authority-bound device PTY through
two sequential seeded 100% packet-loss intervals. The CLI PID/start ticks, Ratox session, host
incarnation, and shell remained exact; process restarts stayed zero; attachment generations advanced
1-to-2-to-3; authenticated online epochs advanced 2-to-3-to-4; and terminal input/output positions
advanced 1-to-2-to-3.

Each interruption first produced the normal heartbeat warning while the prior carrier and epoch
were still confirmed, then authoritative toxcore offline and a live/running zero-attached device
PTY. Both TAPs recorded dropped traffic in both intervals. Each recovery completed exact resume,
one new terminal byte in each direction, and a healthy heartbeat interval before the next fault or
clean `~d` detach.

Both routes used IoTox 0.46.0 rev0046 from the same source-linked binary, SHA-256
`ada08f7991a86a03a0341db857541f8870571816f1a00a59444e1f903646e033`.

## Measurements

| Route | Loss | Heartbeat warning | Authoritative offline | Resume after release | Retry attempts | TAP drops |
|---|---:|---:|---:|---:|---:|---:|
| direct UDP | 1 | 3.454 s | 26.572 s | 1.587 s | 6 | 180 + 133 |
| direct UDP | 2 | 3.421 s | 28.374 s | 1.237 s | 3 | 203 + 198 |
| forced TCP | 1 | 3.400 s | 27.185 s | 6.342 s | 14 | 19 + 27 |
| forced TCP | 2 | 3.514 s | 28.349 s | 3.359 s | 7 | 22 + 22 |

The complete CLI lifetimes were 70.315 seconds on direct UDP and 77.058 seconds on forced TCP.
These are observations from one construction run, not latency objectives or availability SLOs.

## Evidence binding

| Route | Compact proof | Manifest SHA-256 | Lifecycle SHA-256 | Terminal capture SHA-256 | Heartbeat capture SHA-256 |
|---|---|---|---|---|---|
| direct UDP | `pair.66mhbsl5` (252 KiB allocated) | `a022534ec275f53addb78eb2040d6c79385fa881f1e9827ba5be9e7614195ee9` | `aff041463542540ec0524fa0000fc9c60eb7731ac527927f0496901332c646a7` | `3d6e520daf53578f196639c1219fb70200a3286e53b5b18cf98c441be5aa07d7` | `30cd24c99320b8f625be333260fdc99ab8aac72ae651621603bdce0e7ac96bcd` |
| forced TCP | `pair.pvryy_am` (252 KiB allocated) | `b92b717362be1f08d0eb3b7c6cedb81d0cbdc40658e588df8a8fa9c01be599f0` | `24bc136e1ad5070f96b956ab70f21019868bb24a47557098f9f908ebb452cb52` | `c06f7e5297943644b5e8817d8dd342603d69c28e36d2c841792ec358a60e8253` | `b07e5a518594b8fc8d2d9bb3af8e418d0991d89bfca3312511189f54c247341e` |

The route-fault receipts are additionally bound by SHA-256
`29b2c5676e797effea540d73a675be5673ff0098ff7d693cdedab9de1a2ece17` for direct UDP and
`c92d78ddbef0b79253baf4cf973242662b0abdb3ae938d4568aeb9fa251b9dab` for forced TCP.

## Reproduction and verification

When these source-linked NixOS images are not already cached, build them serially. The 48 GiB value
is a sparse lab-image construction envelope needed by the current dependency closure, not an IoTox
installation-size claim.

```sh
nix build '.#nixosConfigurations.iotox-sandwurm-client-forced-tcp.config.system.build.image' --no-link -L
nix build '.#nixosConfigurations.iotox-sandwurm-device-forced-tcp.config.system.build.image' --no-link -L

./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-cli-reconnect-repeated
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-cli-reconnect-repeated
```

Verify each private raw root, export only the allowlisted content-free proof, and verify the compact
root again:

```sh
python3 tools/verify-sandwurm-pair.py \
  --route ROUTE --scenario ratox-cli-reconnect-repeated RAW_ROOT
python3 tools/export-sandwurm-pair.py RAW_ROOT
python3 tools/verify-sandwurm-pair.py \
  --route ROUTE --scenario ratox-cli-reconnect-repeated COMPACT_ROOT
```

The final local validation passed the 821-check owned registry, the complete 55-entry GCC CTest
surface, and the complete 70-entry Clang ASan/UBSan surface. Five positive delegated-cgroup/PSI
process tests were explicit skips in each applicable suite because this host does not delegate those
controllers to the test process. The original ADR 0300 direct-UDP and forced-TCP compact proofs also
re-verified under the additive harness.

## Exact nonclaims

This is two interruptions per route, one construction host, two NixOS KVM guests, one echo profile,
and one provider binary. Same-host guests prove protocol and process separation, not physical path
or administrative independence. This evidence does not establish hours-long retention, arbitrary
loss frequency, public relay diversity, Tor/I2P continuity, Agent/host-restart survival, terminal
screen prediction, PAM interaction, general SSH compatibility, fleet resource policy, independent
security review, or production readiness.
