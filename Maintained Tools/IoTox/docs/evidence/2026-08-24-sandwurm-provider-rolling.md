# Sandwurm c-toxcore 0.2.22 to 0.2.23 live rolling evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-defined NixOS guests ran under Sandwurm/Cloud Hypervisor KVM on the prepared
`sandwurm-vm` bridge. In each cell, both distinct Tox identities and their mutual friendship were
created by exact c-toxcore 0.2.22. The client remained live on 0.2.22 while the device loaded its
old-provider savedata and ran live on exact 0.2.23. Both roles sent a distinct fixed message, received
the peer's message, observed the requested friend route, rewrote savedata through their live
provider, and produced saves whose semantic snapshots were identical under both versions.

The accepted direct-UDP proof is `.sandwurm/exports/pairs/pair.bkvx0lo1`. Both friend connections
were UDP; both post-exchange saves were 3,472 bytes. Its end-to-end harness span, including Sandwurm
construction and boot, was 233,982,238,362 ns. The compact manifest SHA-256 is
`e4aa6983c6dfcf917daacae880590e4beba5b0a624b726dc46abb878a528d3eb`; its compact declaration
SHA-256 is `17758b4c74a747667ffe5b9238bfd6d075769d11b7c1033eb6fcecefe0544c46940a46d849d66a80`.

The accepted forced-TCP proof is `.sandwurm/exports/pairs/pair.lknnctzw`. UDP and local discovery
were disabled, and both friend connections were TCP through the pinned host relay; both
post-exchange saves were 3,238 bytes. Its end-to-end harness span was 284,585,889,197 ns. The compact
manifest SHA-256 is
`e0f174033c0f906f89fed757de8fa9b74118eafb364128738133aa4e95107ed6`; its compact declaration
SHA-256 is `36c6da1aa9ab59aef5b57d11b7c1033eb6fcecefe0544c46940a46d849d66a80`.

Both guests bound the same qualification fixture binaries: 0.2.22 SHA-256
`2b004edbce5ab3afac888f5d3b15eefcad75b240a0307589e9b4c0753e154170` and 0.2.23 SHA-256
`eaa939abd47271baca75bd6ca3d41cea3aa8e8f3121f25be23c3a7442b336bd3`.

## Reproduction

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp provider-rolling
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp provider-rolling

./tools/export-sandwurm-provider-rolling.py .sandwurm/lab/pairs/PAIR_ID
./tools/verify-sandwurm-provider-rolling.py \
  .sandwurm/exports/pairs/PAIR_ID --route direct-udp
./tools/verify-sandwurm-provider-rolling.py \
  .sandwurm/exports/pairs/PAIR_ID --route forced-tcp
```

Each raw proof root contains private guest disks, provider savedata, disposable Tox keys, runtime
journals, and the bootstrap secret key. It is not shareable. The atomic compact exporter admits only
the exact manifest, two content-free guest receipts, two Sandwurm live-chain receipts, and two
planned-launch records, binds every digest, records the source manifest digest and omitted private
classes, then invokes the strict verifier again.

## Exact nonclaims

This is a qualification-fixture wire test, not an old-IoTox product test: no 0.2.22 IoTox release
exists. It does not prove public bootstrap/relay behavior, production rolling orchestration, reverse
new-client/old-device sequencing, arbitrary historical savedata, future provider compatibility,
safe downgrade, NAT diversity, packet loss during upgrade, or an independent machine. The complete
current transition claim requires this evidence together with the savedata/real-current-product
evidence recorded by ADR 0152.
