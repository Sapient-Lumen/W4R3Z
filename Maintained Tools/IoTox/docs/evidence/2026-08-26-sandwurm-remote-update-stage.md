# Sandwurm remote signed-update staging evidence

Date: 2026-08-26

Status: accepted construction evidence

## Claim

One exact source-linked IoTox 0.41.0 rev0041 binary passed the peer-authorized signed-update staging
and local health-gated lifecycle between two simultaneous Sandwurm guests over observed direct UDP
and forced TCP.

In each cell, the publisher created the same canonical 4,194,624-byte signed update bundle and the
subscriber accepted its exact synchronization HEAD. The remote device then issued one public
`iotox command ... update.stage HEAD high` request. The receiver required confirmed bilateral
`signed-ota-v1`, current `install.firmware` authority, the exact accepted HEAD, owner-private update
policy, and the verified release signature before committing the mode-`0400` inactive slot and
`IUS1` terminal evidence. Sender and receiver receipts agree on the durable sender epoch, message
ID, release sequence, accepted HEAD, and update manifest record.

Only after remote staging succeeded did the receiving guest invoke its same-user local apply,
restart the Agent once, open the health window in the successor incarnation, confirm the exact
one-use token, and rehash the selected inert bytes. The sender never obtained apply, restart,
health-token, confirmation, local-path, or execution authority.

For this lab only, the device identity also signs the release manifest so no additional private key
crosses the guest rendezvous. Release signing, sync publication, sync acceptance, update policy,
`install.firmware`, and stable update-state signing remain independent gates.

## Accepted compact cells

| Route | Compact proof | Span | Sender epoch | Message ID |
|---|---|---:|---:|---:|
| direct UDP | `.sandwurm/exports/pairs/pair.6ebmw2t_` | 302,745,201,717 ns | 4,426,065,537,146,736,101 | 12,336,859,572,333,012,671 |
| forced TCP | `.sandwurm/exports/pairs/pair.m_1e_fio` | 448,027,088,693 ns | 465,081,159,866,483,825 | 5,638,349,814,874,731,704 |

Both cells use binary SHA-256
`bd950320270ac7c40e9cdf197f33cd8ec20181fecfa83e7697bb5f4c7c49380d` and report
`IoTox 0.41.0 rev0041`. Their staged source revision is
`3690a718e178e9801953dfbf8b83e08dfe0b5961-dirty`; compact source-manifest SHA-256 values are
`d1bc03d267aead6ec5a6a8c5ad5efeade32985991b95803bb2541a2a11f36f3e` for UDP and
`ae8b17d2f013a06397f344cc53eeeb41325d683f0ae6fb3a87f3c473937c9a93` for TCP.

Each compact export independently verifies, contains no secrets or guest disks, and allocates
147,456 bytes. Its `compact-export.json` SHA-256 is
`cf421ff5af8a5a1f8132b3fac85efcf5c347fb96db970e52375097d44149e072` for UDP and
`2f478032ca4cd44f269d543daba6b5e3f09c04d22bd623bada9fc814a21d93d8` for TCP.

Both cells bind:

- payload SHA-256 `2e4d71c644b5ae7bdee7692bde8c50b24abe2b58cc7a81150cd79159bbff4e26`;
- update manifest record `2715da7101e923dce3b245bbb1d8c7163a54b5eaa5279aabfdb818afac864e4c`;
- sync artifact SHA-256 `5abe1e66a09f118310e27cd21cb259d7eaf66f94fb6411dfe52bc52d3d0caf6c`;
- sync manifest SHA-256 `6e7489bbe9530fd325f102749fa339bc9442083d26c2d025418ddc746b4a9e42`;
- accepted HEAD `e2433e7cf1e737708db83f74ee0f3369acfda930fe2fa8fd16f22b74e0e95032`;
- release sequence 1, one Agent restart, two feature-advertised receipts, two remote-stage-observed
  receipts, and two confirmed-lifecycle receipts.

The UDP client/device receipt SHA-256 values are
`c8a14318621b075168b14e1264f45e411dab81ae6e1fddf18090ac1e95fb20ae` and
`706b4aecb3e6d8cb380d48b1b91a2cf614f81376a9b591dd5d109daadbda1ae6`;
the TCP values are
`20143d360beaa348a7bc1aafe9e5cd4ffaf30e4b57453c78d3a40a0b9d37bc73` and
`82a6873f2957a6a04e740d24b608f2b4e8a535caa1704e9929fa9deebb937f55`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp signed-update
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp signed-update

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.6ebmw2t_ signed-update
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.m_1e_fio signed-update
```

The private source proofs contain writable guest disks, injected test identities, bootstrap secret,
and mutable runtime state. They were verified before compaction and are not the durable distribution
surface. Compact exports retain only the strict verifier allowlist and bind their source manifests.

## Exact nonclaims

This proves one direction of remote staging, one inert opaque payload, one release sequence, one
successful health confirmation, one Agent restart, one local filesystem, two guests on one physical
construction host, and the named native carrier classes. It does not prove remote apply or restart,
executable or bootable installation, a deployment adapter, bootloader integration, hardware
anti-rollback, secure boot, coordinated-snapshot resistance, release-key rotation/revocation,
destructive slot retention, power cuts, recovery media, representative hardware, multi-host or
public-network behavior, fleet rollout, or a safety-critical effect. ADRs 0184 through 0186 freeze
the interpretation.
