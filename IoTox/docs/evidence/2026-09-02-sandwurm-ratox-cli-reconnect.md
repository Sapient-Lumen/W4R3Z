# Sandwurm production-CLI Ratox reconnect evidence

Date: 2026-09-02

Status: accepted two-guest production-client route-loss evidence on direct UDP and forced TCP

## Claim

One real `iotox terminal PEER --reconnect` process opened an authority-bound PTY, exchanged exact
terminal input/output, survived seeded 100% loss on both guest TAPs, waited through authoritative
offline, and automatically resumed the same device-side PTY after route recovery. The process PID
and start ticks remained unchanged, its restart count stayed zero, session and incarnation remained
exact, attachment generation advanced 1-to-2, and authenticated online epoch advanced 2-to-3.

During loss, the production heartbeat warning occurred while the client Agent still reported the
original confirmed carrier and epoch. The later toxcore-offline transition detached the controller;
the device then reported exactly one live/running session, zero attachments, the same byte positions,
and a matching `peer-detached` event. Recovery completed the next exact input/output sequence and a
second healthy heartbeat interval before the probe used the public `~d` escape and observed exit
status zero.

Both routes used IoTox 0.46.0 rev0046, source-linked from the ADR 0299 commit plus the pending ADR
0300 working tree, and identical binary SHA-256
`7007faf6254a7763344e2e4221a6a6702fe06f67bcb21780e75d200f707ef666`.

## Measurements

| Route | Heartbeat warning after loss | Authoritative offline after loss | Restore to resumed OPENED | Retry attempts | Forced TAP drops | CLI lifetime |
|---|---:|---:|---:|---:|---:|---:|
| direct UDP | 3.440 s | 27.280 s | 1.081 s | 3 | 167 + 134 | 36.140 s |
| forced TCP | 3.553 s | 27.761 s | 2.083 s | 5 | 17 + 21 | 37.506 s |

Initial and recovered terminal sequences are exactly 1 and 2 on both routes. Initial and recovered
attachment generations are exactly 1 and 2. The verifier binds the actual session through a
content-free SHA-256 rather than publishing it from the compact receipt.

## Evidence binding

| Route | Compact proof | Manifest SHA-256 | Lifecycle SHA-256 | Terminal capture SHA-256 | Heartbeat capture SHA-256 |
|---|---|---|---|---|---|
| direct UDP | `pair.h3wylill` (248 KiB allocated) | `d97751c349999410201839cbf69bad713a637e5de09a0d8e3fbe0c4371243588` | `27e68324a4a735e58384644137b41b83608e4e5e0fe3452da08848bb589d9ac8` | `c0480f087bab150026a9df47e02b91430cac01c8f64ecbf7cde9062ffdb59362` | `3781d414b3db899b7bc7d8ec8176a9926a10e39eb3576fc729b9f7fa279023ec` |
| forced TCP | `pair.6bf75b_4` (248 KiB allocated) | `4d467b528d21dc4fb92da3cfa85fb8e8ac516ac04ceef5ba215f67e240ce77fc` | `f7da409e026eea562069c638e8c75c27df2fe3f4ff22baeba9c70963c9b910b2` | `6047d9ccef98eccb6df8a95947d080b13f1d976266fac541e3e7bc69afaa5417` | `649f319bfc2c0d1f3fcc828b31a187dba6cd965f4a75e17804b5128ca9da15b9` |

## Reproduction and verification

Build guest images serially when the host cannot populate two sparse images concurrently, then run
the exact cells:

```sh
nix build '.#nixosConfigurations.iotox-sandwurm-client-forced-tcp.config.system.build.image' --no-link
nix build '.#nixosConfigurations.iotox-sandwurm-device-forced-tcp.config.system.build.image' --no-link

./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-cli-reconnect
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-cli-reconnect
```

Verify each raw root, export only the allowlisted content-free evidence, and verify that compact root
again:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair ROUTE PROOF_ROOT ratox-cli-reconnect
python3 tools/export-sandwurm-pair.py PROOF_ROOT
python3 tools/verify-sandwurm-pair.py \
  --route ROUTE --scenario ratox-cli-reconnect COMPACT_ROOT
```

## Exact nonclaims

This is one complete-loss interval per route, one construction host, two NixOS KVM guests, one echo
profile, and one provider binary. It does not prove repeated interruptions, hours-long PTY retention,
daemon/host-restart survival, public relay behavior, physical path diversity, Tor/I2P route
continuity, PAM prompt usability, general SSH compatibility, Mosh prediction/screen convergence,
fleet resource policy, independent security review, or production readiness.
