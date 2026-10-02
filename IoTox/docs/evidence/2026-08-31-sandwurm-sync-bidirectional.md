# Sandwurm pairwise bidirectional synchronization evidence

Date: 2026-08-31

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests completed the ordinary reciprocal read-write ceremony
and then synchronized without a manual `sync-publish` or `sync-pull`. Both daemons were stopped at a
host-coordinated barrier before each guest wrote a different value to the same pathname. After
restart the pair converged on the same deterministic ordinary projection and retained the other
value under its exact writer/generation provenance. A later ordinary edit causally resolved that
conflict. A deletion and a zero-byte file then converged, and both peers passed `sync-repair`.

The host did not merely observe two guest receipts in sequence. The pair manifest binds two
simultaneous cloud-hypervisor/Sandwurm chains, reciprocal guest checkpoints, exact receipt digests,
the same source-linked IoTox binary on both roles, and a monotonic rendezvous span of
246,626,895,259 ns.

## Accepted cell

| Route | Compact proof | Allocated size | Binary SHA-256 |
|---|---|---:|---|
| direct UDP | `.sandwurm/exports/pairs/pair.ms5zsk9l` | 167,936 bytes | `6969b787587f4e66010385331b6d3aa09dcc1ed6067d7a7987076b7d5942b18e` |

The compact pair-manifest SHA-256 is
`5734230f2b429363c02627a20cb06df86c317366cf25525b363692eec86eac72`. Its compact-export manifest
SHA-256 is `c989185dab4b76f64f85c429fdc58fa830a70732a1ff61fd4da32baa35b77197`.
The omitted raw proof manifest was
`166b3c3c3dfe45458f15d928562c70b215a0752b4951d0264158be8d5160132f`.

The retained role bindings are:

| Role | Receipt SHA-256 | Sandwurm chain SHA-256 |
|---|---|---|
| client | `28f9d98ee06dd7b856e3f9abe87e8ab2dbf0c4d5cbdfc30377d2db1713a92190` | `b52567f352281cc09fba16599b517616e4819e4ada4e6b697dea3ff0f6dec876` |
| device | `b7b48ce26dcce43d60160ff6dc4269495104929c5a2f1867b37ef29d040926a7` | `ffb53c27efdb6766ba5db45b753ffbedcab547633a676bdfee1ee25d6671a548` |

Each receipt reports one bidirectional daemon restart, observed conflict preservation, observed later
resolution, and the final zero-byte SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The pair manifest reports two
converged roles and unchanged reused immutable identity baselines.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-bidirectional
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT \
  sync-bidirectional
./tools/iotox-sandwurm-lab.sh export-pair PROOF_ROOT
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.ms5zsk9l sync-bidirectional
```

The compact exporter omits the injected identities, bootstrap secret, runtime state, and writable
guest disks. The compact proof independently reverified after export. Its source raw root occupied
2.3 GB and was removed only after that verification; rerunning the fixture is the recovery path.

## Exact nonclaims

This is same-computer two-VM direct-UDP evidence, not a two-physical-host or hostile-network claim.
It does not prove recovered garbage collection, archive/restore, retention, revoked-writer cutoff,
malicious fork or conflict-storm bounds, long-offline behavior, large-tree performance, filesystem
watching, metadata portability, symlink handling, selective sync, encryption at rest, power-cut
recovery, or long-soak operation. It does not make the synchronized directory a safe sole copy of
important data. Those remain explicit roadmap gates.
