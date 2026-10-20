# Sandwurm tree-v2 projection descriptor retention evidence

On 2026-09-08 local time, source-linked Sandwurm/KVM/ext4 run `1fq3WhIY`
qualified ADR 0340's bounded open-descriptor projection-retention gate.

The run used one networkless Cloud Hypervisor guest, persistent ext4 node
volumes, three IoTox nodes per cell, and six directed read/write sync shares
per cell. The product binary was `IoTox 0.51.0 rev0051`, binary SHA-256
`128dcb974471b18b03aa54884ea8b2eae84a12cd8965a6dd7f9fa2d360fa27b8`, from
source commit `e034311dc4d5843f5650e3194b43879dd5f434a4`.

## Qualified cells

- `pre-exchange-selected`: an external helper retained a writable descriptor
  for selected `held.bin`; external `strace` delayed and fenced the production
  sync worker at `renameat2(..., RENAME_EXCHANGE)` entry; the helper wrote and
  fsynced through the descriptor; IoTox retained the ambiguous old projection
  and pending workspace, live `sync-repair` returned protocol-error
  classification `exchanged old projection changed`, explicit salvage was
  reapplied, all three writers converged, and repair verified all three nodes.
- `post-exchange-unselected`: an unselected local `local/held.bin` descriptor
  was retained across successful `renameat2` exit; live repair returned
  protocol-error classification `preserved unselected projection changed`;
  ext4 refused read-only remount while the writable descriptor was still open;
  after closing the descriptor, read-only/read-write remount preserved the
  retained stage inode and bytes; cold startup refused before exposing the
  control socket; explicit salvage was published as `recovered/held.bin`; all
  three writers converged and repair verified all three nodes.

The selected trace was represented by strace as a split entry/resume pair
(`raw_exchange_line_count=2`, `split_exchange_observed=true`). The unselected
trace was represented as one successful line
(`raw_exchange_line_count=1`, `split_exchange_observed=false`). Both cells
verified exactly one successful exchange bound to the exact visible and stage
paths.

## Commands

```sh
./tools/iotox-sandwurm-lab.sh up-sync-projection-descriptor
python3 tools/verify-sync-projection-descriptor-sandwurm.py \
  .sandwurm/lab/sync-projection-descriptor/run.1fq3WhIY
python3 tools/verify-sandwurm-vm-smoke.py \
  .sandwurm/lab/sync-projection-descriptor/run.1fq3WhIY device
```

The one-command lab wrapper ran both verifiers successfully after the guest
evidence returned. The compact exporter then projected the accepted raw proof
to `.sandwurm/exports/sync-projection-descriptor/run.1fq3WhIY` and the same
strict descriptor verifier replayed that compact root successfully.

```text
compact proof root:       .sandwurm/exports/sync-projection-descriptor/run.1fq3WhIY
manifested files:         5
manifested bytes:         7,644
compact-manifest SHA-256: 250e2ee61e978d05b84e85e2c43584373fe664c77a2fb36bf938254e9f22a76c
```

```sh
./tools/iotox-sandwurm-lab.sh export-sync-projection-descriptor \
  .sandwurm/lab/sync-projection-descriptor/run.1fq3WhIY
python3 tools/verify-sync-projection-descriptor-sandwurm.py \
  .sandwurm/exports/sync-projection-descriptor/run.1fq3WhIY
```

## Nonclaims

This proof does not make local writers authoritative, does not perform
automatic conflict merge, and does not close writes after final obsolete-tree
validation begins. It does not cover writable mappings, hostile same-UID
processes, directory descriptors, hard links, mount namespaces, non-ext4
filesystems, lying storage, physical power loss, or independent backup
provenance.

The retained evidence can now use the compact proof plus strict verifier.
