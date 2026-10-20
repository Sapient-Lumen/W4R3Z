# Sandwurm two-node transport evidence — 2026-08-20

## Claim

Two distinct IoTox NixOS guests ran concurrently under Sandwurm's stock Cloud Hypervisor direct
runner on the founding machine. Each used 2 vCPUs, 2 GiB shared memory, a fresh writable sparse root,
one receipt/rendezvous virtiofs workspace, and a distinct TAP on the prepared `sandwurm-vm` bridge.

The same pinned source-linked IoTox binary positively established a genuine Tox friendship, a
confirmed IoTox application session, private L2 ping, and bidirectional text in two separate cells:

- native direct UDP with c-toxcore's ephemeral guest UDP socket permitted; and
- forced TCP with native UDP, local discovery, DHT announcements, and hole punching disabled.

This is a controlled two-VM transport-baseline claim. It is not Ratox terminal, synchronization,
latency, impairment, restart, public-bootstrap, routed-privacy, two-physical-host, or production
evidence.

## Exact accepted observations

Both cells used IoTox `0.39.0 rev0039`, c-toxcore `0.2.23`, libsodium `1.0.22`, Argon2 `20190702`, and
production binary SHA-256:

```text
b5e58a4bb0e0d723f4e353f1faf8a0a49034b632225682efb7d35cab97c5408b
```

The verified compact exports are:

```text
direct-udp  .sandwurm/exports/pairs/pair.hfmxed72
forced-tcp  .sandwurm/exports/pairs/pair.2s5659l0
```

Direct-UDP bindings:

```text
client IoTox receipt  9a71995cecfe8f555bf151bb5313b959917d68a31aa48f03af0de9a45d194bd1
device IoTox receipt  a5baae14864ecf222b48c9991ac189ef36145b21ffa796a2691da714431c8974
client Sandwurm chain 4c74b50b6cd11aec1a39e8205fa0275094ba32231e3f1b68b763d97bec79b3f9
device Sandwurm chain 5e09c0dcb6c1fb0889184e460b5b76cd1eba23d790831ed959b7ef2f96142b59
```

Forced-TCP bindings:

```text
client IoTox receipt  2b4089558ebf5958b3ad210c44e681f5f8b2d5928ad71a41a490150b01dd7437
device IoTox receipt  e918abac25fc672d02719706b8635f8148e897e51d7662d97612202514f7d9c9
client Sandwurm chain db9037bc15336e4ff65dfd59fae1f1a38f7d1a9ce41954be9706ac2b4d747b7e
device Sandwurm chain 4efe2b25ccfa93ec102182c47b97e08ace40867f2f00cd9893c9148c28ab15d0
```

Both manifests observed `vm-iotoxc` and `vm-iotoxd` simultaneously with
`master=sandwurm-vm`. Every guest receipt reported `virtualization=kvm`,
`cgroup_type=cgroup2fs`, `network_class=provider-egress`, the exact expected connection type,
positive friendship/session/text fields, and `contains_secrets=false`. Both pair runs rehashed the
private reusable key baseline before and after the complete experiment and reported it unchanged.

The manifests and their declared files are independently checked with:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.hfmxed72
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.2s5659l0
```

## Controlled fixture

The pair orchestrator builds c-toxcore's sample `DHT_bootstrap` from the same exact pinned source and
libsodium inputs as IoTox. A lab-only source patch removes the sample's privileged/collision-prone
443 and 3389 listeners, retaining TCP 33445 alongside UDP 33445. The process runs on the host and
the guests address it at `10.0.0.1`; upstream binds wildcard sockets, so the host firewall remains
the outer exposure boundary while the fixture is alive. Its key is fresh per cell and private. The
entire fixture process group is terminated after success or failure.

This fixture makes the experiment independent of public bootstrap availability. It is not shipped
with IoTox, not an authority root, and not evidence that IoTox operates production infrastructure.

## Findings and corrections

The construction sequence found four useful defects rather than hiding failed attempts:

1. Parallel cold image realization could consume the original 240-second workspace deadline before
   VM launch. Workspace creation now has a separate 900-second bound; guest protocol work retains its
   own 240-second bound.
2. Killing a departed `sudo` leader could leave its descendant Nix build alive in the original
   process group. Cleanup now signals and then reaps the entire deliberately created process group,
   even when the leader has already exited.
3. Co-locating the bootstrap/relay with one IoTox peer produced asymmetric self-connect behavior,
   while public bootstrap timing made the first diagnosis nondeterministic. The independent local
   fixture now serves both peers symmetrically.
4. IoTox retried bootstrap endpoints while offline but registered TCP relays only once. One forced-
   TCP guest connected and the other remained offline for the complete bound despite an accepted
   initial registration. The transport owner thread now re-adds configured relays at the same bounded
   offline retry interval; a mock-provider regression forces persistent offline state and requires a
   later `retry accepted` relay event. The subsequent real forced-TCP pair passed.

The direct-UDP cell was repeated after the relay fix so both accepted route cells bind the identical
final production binary rather than two nearby source states.

## Secret boundary

The original proof roots retained two private writable guest disks, the temporary fixture secret key,
and detailed runtime state. `export-sandwurm-pair.py` verified each original, copied only the exact
seven JSON files consumed by the verifier, recorded the original manifest digest and omitted-private
classes, and reverified the compact result before the original roots were deleted. Each compact export
is 96 KiB allocated, declares `contains_secrets=false`, and remains independently verifiable. It is the
shareable evidence subset; arbitrary files from an original proof root never are.
