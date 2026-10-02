# Sandwurm signed-update lifecycle evidence

Date: 2026-08-26

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same default-off signed-update
construction lifecycle over observed direct UDP and forced TCP. Each cell used stable reusable test
identities, the pinned local c-toxcore 0.2.23 bootstrap/relay fixture, one accepted signed sync HEAD,
and one production binary.

The publisher created a canonical `signed-update-bundle-v1` containing a 320-byte signed manifest
and a 4 MiB inert payload. The subscriber accepted the exact sync HEAD, joined it to the immutable
artifact, independently verified the release signature under owner-local policy, staged the payload
in a mode-`0400` digest-named inactive slot, applied it, and restarted its Agent once. The successor
Agent observed `health-window-opened`, accepted the exact one-use health token, committed sequence 1
as confirmed, and selected bytes with the exact payload digest. Feature bit 20 remained absent.

For this lab only, the device identity also signs the release manifest so no additional private key
must cross the guest rendezvous. The update signature domain, owner-local update policy, sync policy,
and device state remain distinct. A deployment should use an independently operated release key.

## Accepted compact cells

| Route | Compact proof | Span | Binary SHA-256 | Source manifest SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.7vmazf5b` | 393,643,386,897 ns | `c3fe27569d07092c6fde2876ed43fcff1db8eb520ed94645001970cb027d1ada` | `1cf7ffbd2b7aadedbcb36238bd0b16d2c70f148f848254163ffad40d9052910c` |
| forced TCP | `.sandwurm/exports/pairs/pair.wrrfloqd` | 336,433,136,568 ns | `c3fe27569d07092c6fde2876ed43fcff1db8eb520ed94645001970cb027d1ada` | `f1f05abaf124052b1221d63d86acdadad944014c279a015de6027b508c109788` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates
147,456 bytes. Its compact-manifest SHA-256 is
`4b739334e1df95c6999cd7d0fa0afe180fd254ff9d6604c086fdf19fca984939` for UDP and
`7838c0f89116d0629c34dfba7deacf9ed34fc6d6878ec594fc2c66060fe069ed` for TCP.

Both binaries report IoTox 0.40.0 rev0040 and source revision
`823482e147ee156dcfee0195ac367587a2b88478-dirty`; the source-manifest hashes above bind the exact
staged tree used to construct each role-specific closure.

Both cells bind:

- payload SHA-256 `2e4d71c644b5ae7bdee7692bde8c50b24abe2b58cc7a81150cd79159bbff4e26`;
- update manifest record `2715da7101e923dce3b245bbb1d8c7163a54b5eaa5279aabfdb818afac864e4c`;
- 4,194,624-byte sync artifact SHA-256
  `5abe1e66a09f118310e27cd21cb259d7eaf66f94fb6411dfe52bc52d3d0caf6c`;
- sync manifest SHA-256 `6e7489bbe9530fd325f102749fa339bc9442083d26c2d025418ddc746b4a9e42`;
- accepted HEAD `e2433e7cf1e737708db83f74ee0f3369acfda930fe2fa8fd16f22b74e0e95032`.

The UDP client/device receipt SHA-256 values are
`16b964312734d783e0fbc442bfa0115f49e092bea8ccdea191fd270d7bd56fe0` and
`cff53ac30d84af065e2f8d842d2a5b84b9a9a6e4c2927585cdcc1f7f12b0fc9b`;
the TCP values are
`b94adc76b5fe2d06e3e98f51a8d1e79982280e07d916f533b6ea0ab66cf2fa33` and
`a62fd418a08f2a45338bdd77066f264f9898af367e4f216508c27ac8094bc68c`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp signed-update
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp signed-update

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.7vmazf5b \
  --route direct-udp --scenario signed-update
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.wrrfloqd \
  --route forced-tcp --scenario signed-update
```

The private source proofs contained writable guest disks, injected identities, the bootstrap secret,
and mutable runtime state. They were verified before compaction and are intentionally not the durable
distribution surface. The compact exports retain only the strict verifier allowlist and bind their
source manifests.

## Exact nonclaims

This proves one inert opaque payload, one release sequence, one successful health confirmation, one
Agent restart, one local filesystem, two guests on one physical construction host, and the named
native carrier classes. It does not prove remote `install.firmware` authorization, executable or
bootable installation, a real bootloader, hardware anti-rollback, secure boot, coordinated-snapshot
resistance, release-key rotation/revocation operations, slot collection, power-cut behavior, recovery
media, representative hardware, multi-host behavior, public bootstrap, fleet rollout, or a safety-
critical effect. ADRs 0184 and 0185 freeze the interpretation.
