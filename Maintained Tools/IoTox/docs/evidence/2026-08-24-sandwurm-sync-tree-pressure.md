# Sandwurm synchronization worker-pressure evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same bounded synchronization
worker-pressure and recovery gate over observed direct UDP and forced TCP. Both cells used one
production binary, stable reused test identities, a canonical 4 MiB treepack baseline, two additional
signed directory namespaces, and the pinned local c-toxcore 0.2.23 bootstrap/relay fixture.

The publisher was configured with `--max-sync-worker-queue 1`. The gate held namespace A's real
cross-process transaction lock while the device admitted A's artifact request as active work and its
manifest request as the sole queued job. The client then requested namespace B. The event pump
observed that third job while A remained blocked, preserved the hard queue bound, and increased the
rejection counter by exactly one. Releasing only A's lock let both A jobs drain. Namespace A
converged, and an exact retry of the retained B request then converged B. Both roles observed
saturation and retry recovery without changing the bound or evicting admitted work.

The first scientific attempts exposed indirect event-pump blocking behind publisher work. ADR 0141
records the resulting production rule: status uses a nonblocking publisher snapshot with an explicit
`publisher-busy` bit, best-effort Ratox maintenance never waits behind a synchronization authority
effect, and unrelated transport events leave the synchronization file hook before authority locking.

## Accepted compact cells

| Route | Compact proof | Span | Binary SHA-256 | Source manifest SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.c3qc5k28` | 470,479,478,489 ns | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `3e5b4d708143724803411c7ec7277f6734f490cd4aacbd8575a3ce2d8211b69b` |
| forced TCP | `.sandwurm/exports/pairs/pair.5nh407kh` | 394,233,205,703 ns | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `691814d7291699be304057cc9ec17af3f4684e01f9fa28101f09c7cc1d231018` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates 110,592
bytes. The compact pair-manifest/export-manifest SHA-256 pairs are
`b84c8e201f9283a413d4a3b5e16bfdaf340d9209ccae48ba823ff80d0193d003` /
`def0cc9381f7e873dcca0276fc53c8fec66ea0661458db5a054dbf9d18733044` for UDP and
`aa6d83dcb141062d764b33110118008dcbf29349ae4f512208b99a5353e7881d` /
`3fa61c5afdb91d93fe8e0b092209e4e8d8cdc644fdc2c6082f8e7292cd6ef0f3` for TCP.

Both cells bind queue bound 1, rejected delta 1, two saturation-observing roles, two retry-observing
roles, namespace-A HEAD
`fa3a32afb9a5de1e7cb672bb879e418e80716ab22227cfbca90a598fea79eaec`, and namespace-B HEAD
`376ca800cdf0360c9702373b0dfcfb47c3eea0bb1179f02216e11295fdad1569`.
The shared baseline has artifact SHA-256
`a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e`, manifest SHA-256
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`, and visible payload
SHA-256 `374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`.
It contains three directories, three files, and 4,194,389 content bytes.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-pressure
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-pressure

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.c3qc5k28 \
  --route direct-udp --scenario sync-tree-pressure
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.5nh407kh \
  --route forced-tcp --scenario sync-tree-pressure
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and are intentionally not the durable distribution surface. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This proves one publisher, one subscriber, a worker queue bound of one, one cross-process transaction
stall, overload refusal, event-pump liveness, exact retained retry, and two additional namespace
convergences on this construction kernel. It does not prove a peak resident-memory ceiling,
namespace storage/object quota saturation, read-only storage, multi-source or multi-host behavior,
arbitrary kernel scheduling, target-fleet load, priority transport for sync, content-v2, destructive
collection, automatic OTA, or safety-critical actuation.
