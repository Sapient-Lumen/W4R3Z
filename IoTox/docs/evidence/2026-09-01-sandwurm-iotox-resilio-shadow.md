# Sandwurm IoTox/Resilio shadow evidence

Date: 2026-09-01

Status: accepted founding-machine evidence

## Claim

One networkless Sandwurm/KVM guest ran a private loopback c-toxcore bootstrap, two source-linked
IoTox 0.46.0 rev0046 Agents, and a real Resilio Sync 2.8.1 read-write/read-only pair with 2 virtual
CPUs and 2 GiB RAM. The harness applied the same deterministic mutation independently to the IoTox
and Resilio sources every 30 seconds. Every cycle required four canonical regular-file views—IoTox
source, IoTox verified activation, Resilio source, and Resilio replica—to be byte-equivalent.

The run completed 240 cycles over 7,200,096 ms. It restarted the IoTox publisher six times and the
replica six times in alternating 20-cycle barriers. No publish, pull, or activation command was
issued after setup. The publisher reported 356 bounded replay-window evictions, so the accepted run
crossed the former 256-result connection-lifetime failure rather than merely avoiding it.

The Cloud Hypervisor launch exposed no network device. Tox and Resilio traffic remained within the
guest. No public bootstrap, relay, route, service, or host-network synchronization participated.

## Accepted cell

| Proof | Allocated size | Evidence bytes | Compact-manifest SHA-256 |
|---|---:|---:|---|
| `.sandwurm/exports/sync-shadow/run.XXdpLNPh` | 100 KiB | 87,163 | `d2a201caa0ccd3d5d90b39d9a34eaa4031f26111cb7c35c2765168eeea763654` |

The generic VM-smoke verifier and dedicated sync-shadow verifier accept both the raw proof and the
six-file compact tree (five copied receipts plus its export manifest). The source-linked binary was
built from commit `c24686f5229c1ed6a9b1d6822cd9cab85f011aa6` and has SHA-256
`89ab69299e22b6c97b165f148ff6aaf7426ac3dca29eb4e771cd2e271cc78717`.

The content-free guest receipt records:

| Observation | Result |
|---|---:|
| duration floor / elapsed | 7,200,000 / 7,200,096 ms |
| exact convergence cycles | 240 |
| interval | 30 seconds |
| publisher / replica restarts | 6 / 6 |
| publisher replay-window evictions | 356 |
| final canonical files / bytes | 26 / 105,037 |
| post-setup manual publish/pull/activate commands | 0 |
| IoTox nodes / VM vCPUs / VM memory | 2 / 2 / 2 GiB |

The final canonical manifest commitment is
`ea197e41a8907a55b7cac11aed25cd04217e979306e56d3d68c2515109ecac59`.
The Resilio binary commitment is
`254705d95efc9e814217803129359bcfa68f575cb1d3e2cfd69c70c6050d2c1f`; its version-output
commitment is `23881874b96a9eb0c12c16ac49362cf802b656bdd4c756f4ad86b2eb07ae87b9`.

Directory content, Tox savedata, RecallRoot phrases, authority private material, Resilio secrets,
runtime state, and the writable guest disk are absent from the compact proof.

## Reproduction, export, and verification

```bash
./tools/iotox-sandwurm-lab.sh up-sync-shadow
./tools/iotox-sandwurm-lab.sh verify-sync-shadow RAW_PROOF_ROOT
./tools/iotox-sandwurm-lab.sh export-sync-shadow RAW_PROOF_ROOT
python3 tools/verify-sandwurm-vm-smoke.py COMPACT_PROOF_ROOT device
python3 tools/verify-sync-shadow-sandwurm.py COMPACT_PROOF_ROOT
```

## Exact nonclaims

This is same-computer, networkless KVM evidence for bounded private Linux regular-file directories.
It is not independent-machine, public-network, mobile, case-folding, symlink, sparse-fetch, rich
metadata, physical power-cut, or at-rest-encryption evidence. It does not make synchronization a
backup, qualify permanent purge, establish production readiness, or replace an independent copy of
important data. It compares canonical end states every 30 seconds; it is not a latency or throughput
service-level guarantee.
