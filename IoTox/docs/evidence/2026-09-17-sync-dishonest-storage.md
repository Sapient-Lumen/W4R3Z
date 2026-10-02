# Sync dishonest-storage drill — 2026-09-17

Status: accepted first same-host dishonest-storage substrate gate; not complete storage
qualification.

## Command

```sh
tools/iotox-repo.sh sync-dishonest-storage-drill
python3 tools/verify-sync-dishonest-storage-drill.py \
  .sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X
```

The helper creates a 96-MiB ext4 origin image with generation 1 of three
IoTox-shaped tree-v2 state families, then mounts a device-mapper snapshot over
that origin with a 64-MiB COW device. Generation 2 is written through the
snapshot with file and directory fsyncs and is read back before the cut. The
snapshot COW is then discarded, modeling storage that acknowledged a durable
write but later returned the older valid backing state. A cold read-only
`noload` remount of the origin returns generation 1. The external witness floor
remembers generation 2 and refuses mutation.

## Accepted receipt

```text
run-id:                         run.UbmYPe1X
source revision:                59a00cdca6c69c53bde6bb01463c4544a2a98731
receipt:                        .sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X/receipt.json
receipt-sha256:                 d2a72f7f2d1d5511bd2e3d0f44b73c0d0196e7342489319dee25a39a84b01dc0
verification:                   .sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X/verification.json
verification-sha256:            16d6986300a66df3ba21ad2c0fce05a771cbc46fe18ab19be86c7b087a2f94bb
block interposer:               device-mapper-snapshot
filesystem:                     ext4
storage lie:                    snapshot-cow-discard-after-acknowledged-fsync
base generation:                1
acknowledged generation:        2
cold generation:                1
external witness floor:         2
base/cold state sha256:         6f19540f2f3e6361585a60147048fb795e62918614f5c798fd3460885aeafbd3
acknowledged/floor sha256:      c7a851ce94164143b7a86166fbe82baf371ff492c9e608fbbef0d33bbfeb51d7
families:                       branch-pointer, workspace, maintenance
rollback-detected:              true
mutation-refused:               true
contains-secrets:               false
raw-retained:                   false
```

The retained compact evidence is only `receipt.json`, `verification.json`, and
`summary.json`. The raw loop images, mount directories, loop devices, and
device-mapper node were removed after the receipt was written. A follow-up
check found no live mount, mapper, or loop reference under
`.sandwurm/lab/sync-dishonest-storage`.

## Boundary

This is stronger than a syscall-level simulation because the write goes through
an ordinary ext4 mount backed by a real kernel device-mapper block target. It
also keeps the claim narrow. The records are content-free IoTox-shaped state
records, not a full production three-daemon sync namespace. The run proves that
the new harness, verifier, and witness-floor semantics can expose one
acknowledged-write-then-valid-old-cold-read lie and refuse it.

This does not prove:

- storage-media honesty;
- the full dishonest-storage matrix;
- physical power-loss behavior;
- independent backup custody;
- protection for every sync record family;
- exact production Agent integration for every tree-v2 write boundary; or
- precious-data readiness.

The next dishonest-storage work should use the same receipt shape against
`dm-log-writes`, `dm-flakey`, an NBD/virtio block proxy, or a Sandwurm guest
disk so selected write/flush prefixes, cross-family mixtures, torn records,
and masked I/O errors can be replayed against production sync operations.
