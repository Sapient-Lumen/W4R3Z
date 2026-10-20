# Sandwurm whole-object daemon-restart resume evidence

Date: 2026-08-29

Status: accepted direct-UDP and forced-TCP qualification

## Claim

After an unclean subscriber daemon death during two concurrent immutable-object receives, a fresh
IoTox process retained only the strict canonical prefixes named by stable-device-signed attempt
truth. It restored no old job or transport handle. A fresh authorized pull verified the same signed
HEAD, allocated fresh attempts and FileIds, resumed both objects at their exact retained byte counts,
verified their complete digests, accepted the HEAD last, and explicitly activated the revision.

## Accepted cells

| Route | Compact proof | Interrupted = resumed | Resumed attempts | Pair span |
|---|---|---:|---:|---:|
| direct UDP | `.sandwurm/exports/pairs/pair.f20ma62y` | 115,164 | 2 | 359,201,636,312 ns |
| forced TCP | `.sandwurm/exports/pairs/pair.lj0pdz6a` | 159,036 | 2 | 481,099,445,066 ns |

Both cells use source revision `99227ceb17b3adccd13fcc5df9953c973c18d37b`, product revision
`rev0045`, c-toxcore 0.2.23, libsodium 1.0.22, and binary SHA-256
`4ad91d8bb943acdfd5cc9f3c28abb629488541618a96c54952cfd1d979e32162`.

The fixture joins an 8,388,608-byte artifact and 786,496-byte manifest. At the crash boundary each
guest assertion requires one or two canonical attempt files, zero disposable transport temporaries,
a present signed attempt journal, and no accepted HEAD or activation. After startup, the exact
canonical file count and byte sum are unchanged. The fresh pull then requires:

- two restart-resumed attempts and exact `interrupted = restart-resumed = total-resumed` bytes;
- one unclean client stop and one client daemon restart, with stable Tox/device identity;
- restart retention/recovery reported by both roles;
- complete object convergence, signed-HEAD-last acceptance, and explicit activation; and
- UDP or TCP connection truth matching the selected cell.

The common immutable identities are:

- artifact SHA-256: `628137e2ec82540d278434e5214ec1f96765183ad6b8666d4a61fe1a91e2cea5`;
- manifest SHA-256: `4808af6e0e0fc52d19060299854af2a0937bc8b56532471df5b4b854f1ae9fd1`;
- signed HEAD record: `e47ab54d788d82b86e5b6ea4ab5c47732c9b3f0a6a15bb8138a252671dd4b62c`.

Direct client/device receipt SHA-256 values are
`6dbb6470b4f19884923e951936d7600bc57f6d403374558e2a67b47b2d2639f0` and
`dd451b17124fa56f96d7c92ae74a3238386b7f23bf59006f081cebb703146b3e`.
Forced-TCP values are
`02d018a4f2484c7677263855a7260b66045e3934dac42c8d3b188e88aab952d4` and
`6614999eae34e458e2ed6ab04e9d70e20b52f94678fd7f9d7c2a9e0e2e21d424`.

Each secret-free compact root allocates 155,648 bytes and independently passes strict replay.
Direct pair-manifest/compact-export SHA-256 values are
`0840d7bb02ceb925082e60d2eb4acc581f98345ffe5e9131ca18aabc58d2bca1` and
`7477c96551ba95c8fb9ddf48909bc86d90eadbfd13df9f410aa6db7c93a2915b`.
Forced-TCP values are
`c18126c0fe35139898ea9a3d67f259c6a9e5247686a8fbc07a98ae77681b1b13` and
`0d7f6caceb66cfdf5504859d0018590b65ec7859c70a69142906ed0bd13a0304`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-restart-resume
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-restart-resume

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.f20ma62y sync-file-restart-resume
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.lj0pdz6a sync-file-restart-resume
```

The raw accepted roots were removed only after compact export and independent strict verification.
The compact forms retain manifests, launch/chain commitments, content-free receipts, and exact
postconditions; they omit guest disks, injected identities, and runtime secrets.

## Exact nonclaims

This evidence does not prove old-job or old-handle resurrection, range-bundle restart continuation,
guest/kernel power loss, clean-shutdown checkpointing, final-chunk crash linearization, disk-full
behavior during retention/handoff, I2P/Tor continuation, concurrent multi-source striping, two
physical hosts, or a performance bound.
