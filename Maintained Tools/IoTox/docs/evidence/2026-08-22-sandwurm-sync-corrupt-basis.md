# Sandwurm synchronization corrupt-basis recovery evidence

Date: 2026-08-22

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests recovered a signed successor after the subscriber's
exact accepted range basis was deliberately corrupted. The gate passed over observed direct UDP and
forced TCP with the same production binary, revision identities, and state ordering.

For each carrier, the device published a deterministic 4 MiB generation 1 and the client pulled and
explicitly activated it. The client then overwrote only the first 4 KiB of its digest-derived basis
object with zeroes using `conv=notrunc`, proved that file size was unchanged and SHA-256 no longer
matched its name, and retained that corrupt file. The device changed one bounded source region and
published the exact parent-linked generation 2. The client:

1. committed and reverified the complete generation-2 manifest;
2. refused the corrupt generation-1 object as a range basis;
3. emitted the ordinary whole-artifact request under a fresh attempt and FileId;
4. verified and committed the exact complete generation-2 artifact;
5. accepted the signed HEAD last and explicitly activated its exact token; and
6. proved the old corrupt digest path was still present and invalid.

Both guest receipts report `sync_range_fallback_observed=true` and
`sync_corrupt_basis_preserved=true`. They report zero range count/reused/fetched bytes, preventing the
fallback from being mislabeled as successful delta reuse.

## Accepted cells

| Route | Raw private proof | Compact proof | Span | Binary SHA-256 |
|---|---|---|---:|---|
| direct UDP | removed after verified compaction | `.sandwurm/exports/pairs/pair.1fyi5byu` | 355,754,630,982 ns | `56a9cd58098b3bd1c534e2df0d4a06b3e2c09e545e931742390952479b3e793c` |
| forced TCP | removed after verified compaction | `.sandwurm/exports/pairs/pair.9tkvsybe` | 348,493,306,776 ns | `56a9cd58098b3bd1c534e2df0d4a06b3e2c09e545e931742390952479b3e793c` |

Both cells converged on:

- generation: `2`;
- artifact bytes: `4,194,304`;
- artifact SHA-256: `0e2590fa6bcc290f7307cb0c0a34cc807934895293f4be25aafb102383075411`;
- manifest SHA-256: `322dd3fffdda3747ca592f2627138d8ae32fd064680b34aa4dd238b01804e032`;
- signed HEAD record: `dead8d7be3834b7d06128ae25a6b343168c48e154ac3af60a605944c7a85b31d`;
- range count/reused/fetched bytes: `0 / 0 / 0`;
- fallback-observing roles: `2`;
- corrupt-basis-preserving roles: `2`.

The compact UDP and TCP proofs allocate 110,592 bytes each and independently pass the ordinary pair
verifier. Their manifest SHA-256 values are respectively
`d5a9a846338affc9a95f168392d1db31c78535d4e69152c1c5e94006ab3998be` and
`07efa718d12dc81468ca45b4bb3a1ff273699527684fcdfbb012ca863ba90cb6`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-corrupt-basis

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.1fyi5byu \
  --route direct-udp --scenario sync-file-corrupt-basis
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.9tkvsybe \
  --route forced-tcp --scenario sync-file-corrupt-basis
```

The raw roots contained private writable guest disks and injected test identities. They were removed
after both compact proofs independently reverified; rerunning the fixture is the recovery path.

## Exact nonclaims

This proves liveness and authority ordering when an older accepted basis is corrupt before range
planning. It does not repair or delete that old object, repair a corrupt object already occupying the
successor's own digest path, continue a partially failed range bundle, survive power loss, establish
filesystem fault behavior, enable quarantine/GC, or prove two-physical-host behavior. Those remain
separate gates.
