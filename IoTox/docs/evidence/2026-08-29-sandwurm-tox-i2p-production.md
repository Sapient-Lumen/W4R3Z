# Sandwurm production Tox/I2P evidence

Date: 2026-08-29

Status: accepted production-spelling VM qualification

## Claim

Two independent source-linked IoTox microVMs can select the canonical `tox/i2p` route and complete
the baseline peer/application lifecycle through two actual i2pd routers and three persistent,
address-preserving I2P service fronts. The strict route cannot emit native UDP or connect directly
to a bootstrap record or peer.

## Accepted cell

- raw proof: `.sandwurm/lab/pairs/pair.btm5vwr9` (2.3 GiB; contains private guest disks);
- compact proof: `.sandwurm/exports/pairs/pair.btm5vwr9` (1,216,512 allocated bytes; secret-free);
- source revision: `5eee0051ab28cfbba24d30de1cc78cde5fe8727a-dirty`;
- product revision: `rev0045`;
- binary SHA-256: `21a8de96796e3d7549b77fa8ea2c82b0c9002b8c38dd7c0f3d844be176850317`;
- pair span: 1,002,433,335,294 ns; and
- topology/node-set commitments:
  `e72825651a18c04549099103c4ccb456a3d6ac4f959c50dd397733f56d6d12a4` and
  `cf040c3bc97197477a2b5e16e10a101c2b6505939924c04adfefd3de3bca9cc3`.

Both receipts report `route_mode=tox-i2p`, `network=Tox/I2P`, `observed_connection=tcp`, immutable
test-identity reuse, friendship, canonical session confirmation, and bidirectional text. Client and
device receipt SHA-256 values are
`6d6e053a29b4bc3a96ce08c22a6ea26b1966862fd1a606d1a01d4cafb7ddee95` and
`a08fe6ea211fa6137980361b8666dc821176f187c1cd32d02e29db68d986c271`.

The client capture records 658 IPv4 packets; the device records 1,091. Each has zero native UDP,
zero direct bootstrap packets, zero direct-peer packets, and only TCP to `10.0.0.1:39053`. Their
capture SHA-256 values are
`8d0ce2bece24576c5873299e6510df2ec64e082a43beddcf2a18f8a16ad22de8` and
`d4abe6b72e6b4f4ef6d753f07d15361f5730b206293089136b7ef12f11b28bfb`.

The compact pair-manifest, compact-export, and containment SHA-256 values are
`eeda9291840ade02ba6a8d07d27488b8953b62c3fb4f38ae312cc82c65b54eb4`,
`a6caef99e5484b09bbeb79f7f60411c6b1ed5ae62ded20c55547702323d18ceb`, and
`d30f37688d4b79339cf77081f7bc2128f76ba53307623938b8215f0cdb63336f`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-i2p baseline NODE1 NODE2 NODE3
./tools/iotox-sandwurm-lab.sh verify-pair tox-i2p \
  .sandwurm/lab/pairs/pair.btm5vwr9 baseline
./tools/iotox-sandwurm-lab.sh export-pair \
  .sandwurm/lab/pairs/pair.btm5vwr9
./tools/iotox-sandwurm-lab.sh verify-pair tox-i2p \
  .sandwurm/exports/pairs/pair.btm5vwr9 baseline
```

Each node is an explicit current `IPv4:PORT:64_HEX_KEY` input. IoTox compiles no I2P default node or
Destination catalog. The compact export omits guest disks, injected identities, runtime state, and
the bootstrap fixture secret key.

## Exact nonclaims

This evidence does not prove anonymity, resistance to global or local traffic analysis, I2P or
front availability, public relay quality, distinct front ownership, operator/geographic diversity,
two physical hosts, NAT variety, broad endpoint populations, later time windows, Ratox latency over
I2P, large-object performance, fleet behavior, or any ambient I2P SOCKS/outproxy configuration.
