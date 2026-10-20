# Sandwurm sealed Linux service update evidence

Date: 2026-08-27

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox 0.44.0 rev0044 guests passed the default-off
`linux-service-v1` remote-stage and local deployment lifecycle over observed direct UDP and forced
TCP. Both cells used the same reusable private Tox identity baseline, one pinned local c-toxcore
0.2.23 bootstrap/TCP-relay fixture, and the same production IoTox binary SHA-256
`6c9b22c1a316871fd617692f8ea7bc261e536ce058808f766926b5773c47d7e1`.

The publishing guest created a dedicated release-role Ed25519 identity, exposed only its public key
to the subscriber, signed a canonical sequence-1 `linux-service-v1` bundle, published it through
the accepted synchronization HEAD, and issued the authority-gated public `update.stage` command.
The subscriber independently verified and staged the bundle, then exercised four owner-local
deployment paths against the real sealed-memfd/helper adapter:

1. kill the candidate service before its delayed readiness record and require immediate signed
   rollback;
2. restage, accept exact readiness, kill the Agent with `SIGKILL`, require the helper's parent-death
   contract to remove the service, and require startup rollback;
3. restage, accept exact readiness, withhold confirmation through the health deadline, and require
   automatic rollback;
4. restage, accept exact readiness, confirm the same live candidate with the one-use local token,
   restart the Agent cleanly, and require the confirmed service to relaunch ready from the exact
   signed slot.

Each role's content-free receipt records six Agent restarts, three rollbacks, all six service
observations, `update_service_payload_kind=linux-service-v1`, and
`update_service_image_sealed=true`. Both roles agree on the route, binary, release sequence, remote
sender epoch/message ID, signed bundle identities, and terminal confirmation.

## Accepted compact cells

| Route | Compact proof | Source revision | Span | Update manifest record |
|---|---|---|---:|---|
| direct UDP | `.sandwurm/exports/pairs/pair.pwpgv4si` | `ad2776ccdfb8a24f8c6c50d0815e036a8b1bf2dc` | 382,248,642,786 ns | `38a680f2725f3276ec3527538dae1a45b70047f14e90be8ffbb0e43376e0e956` |
| forced TCP | `.sandwurm/exports/pairs/pair.rntpawny` | `8bbb66364453d76e414f529b7e4ba150932b4a6a` | 481,899,848,690 ns | `6d606c693d77a26b14cdef515af870b75745caef53f77a749c8b91d7ebad070b` |

Both cells bind payload SHA-256
`be4913e5bff82353915488a8a32ef2a796f4394d028a4db908a193b458e57ece`. Their complete signed
bundle, sync-manifest, and HEAD digests differ because each cell generates a distinct release key
and signature:

| Route | Sync artifact | Sync manifest | Accepted HEAD |
|---|---|---|---|
| direct UDP | `711119e55f579e2e30f5d65af4d5e229a98e3a0829b00aaadc369218166448e5` | `20bb7753bb0d82c5cfa392cb32e071e49d05487fb751e5b855418b56ae920757` | `cf8133389d181488515ee34bd3118d0ad4a0ebf0e667e81114ec6ca5b2274262` |
| forced TCP | `fab02625b3558a18a23c02cabf1d0ed001b350bec372aaa7744123823cb79efd` | `e45a0e0c62c49749cdf96b06fa627ca8a68c164c4152371f12d9f3e53a398861` | `0cd26afed909779e4d4324782cb191eec6d6e130533bd40c22c4bec9abc7a917` |

The UDP client/device receipt SHA-256 values are
`bbd654e47567fab60f4e2851a7ec6c9a766fdd1cf21be763cf364239b0d905a7` and
`794ab53e09edec5261f35ca040ceee23b994b74b17373ef8b3d1e107794bd0b1`; the TCP values are
`c545ff8ef693c406953cba55d20e08d366d6c2fb7ace4d968c6cc728dd666ca3` and
`5f9da1c233247c6c2a180b7b4f107369fb437614ab9e6f5916f528c7b9cf66ce`.

Each compact export independently passes the repository verifier, contains no guest disk or secret,
and allocates 147,456 bytes. `compact-export.json` hashes are
`cedd514fc32371f4430b830e2d4d3351a8c222c7362bed61cabd15b2d343eaca` for UDP and
`72971f863f9adee17bc53f0c2be08536f41da8a9df81f1cd017c931cee003223` for TCP. The records bind their
private source manifests as
`b991efd8e2eef80533510afbdc677930575181798d6faea94efa4865ad2199b4` and
`d65a8ccdca92de60854ee1dc12f8e4c60b199830eeb271f6c1f61d89f61a23bb` respectively.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp update-service
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp update-service

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.pwpgv4si update-service
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.rntpawny update-service
```

The first forced-TCP attempt reached self TCP connectivity but not peer/authority convergence before
the lab's historical 240-second synchronization barrier. Its preserved guest status showed both
Agents alive, one admitted peer each, and no established protocol session. The guest scenario was
already bounded at 900 seconds; rev0044 therefore gives only this service-update cell a 480-second
authority barrier and 960-second outer receipt bound. The next exact run crossed authority, remote
stage, all service faults, and final verification in 481,899,848,690 ns. This is a disclosed harness
timeout correction, not a discarded product failure.

Two earlier bring-up attempts stopped during release-signer rendezvous before address exchange: one
assumed uppercase CLI output, and one parsed the structured `identity=... public-key=...` line as a
single `key=value` record. The accepted source revisions normalize and token-parse the real
`update-signer-show` output. Neither rejected attempt reached update policy, payload creation,
transport, staging, or execution.

The private source proofs contained writable guest disks, injected reusable test identities, the
bootstrap secret, the release private key, and mutable runtime state. They were verified before
compaction and are not the durable distribution surface.

## Exact nonclaims

This proves a real native service fixture, one release sequence, three process/Agent interruption
rollback paths, one confirmed recovery, two simultaneous guests on one physical construction host,
and the named native Tox carrier classes. It does not prove an abrupt whole-VMM or host power cut,
distinct physical machines, a production systemd/cgroup policy, containment of a malicious service,
boot-partition replacement, recovery media, flash wear, secure boot, hardware anti-rollback,
coordinated-snapshot resistance, destructive retention, public-network routing, fleet rollout,
representative hardware, or remote apply/restart/confirm authority. ADRs 0184 through 0189 freeze
the interpretation.
