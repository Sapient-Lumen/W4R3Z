# Sandwurm synchronization target-object repair evidence

Date: 2026-08-23

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests repaired a corrupt object at the exact target digest
path and recovered the already accepted revision from its authorized publisher. The gate passed over
observed direct UDP and forced TCP with the same production binary, namespace policy, immutable
revision identities, and authority ordering.

For each carrier, the device published a deterministic 4 MiB generation 1 and the client pulled and
explicitly activated it. The client then overwrote and fsynced the first 4 KiB of the exact artifact
object without changing its private regular-file shape. It proved the resulting SHA-256 no longer
matched the digest-derived filename and invoked `sync-repair sandwurm-file`. Repair:

1. inspected the exact two-object final inventory and verified the manifest;
2. moved only the 4 MiB artifact mismatch into a private, uniquely named quarantine file;
3. left the signed accepted-HEAD and activation records byte-identical;
4. left the target digest path absent until an explicit new pull;
5. recovered the same signed HEAD and complete artifact from the live authorized publisher;
6. restored the exact digest path without deleting or replacing the quarantined evidence; and
7. passed a second clean repair scan with two verified objects and zero new quarantine effects.

Both guest receipts agree on the corruption, repair, recovery, clean retry, quarantine preservation,
and signed-state preservation observations. The pair verifier requires exact cross-role agreement on
the object and byte counts.

## Accepted cells

| Route | Raw private proof | Compact proof | Span | Binary SHA-256 |
|---|---|---|---:|---|
| direct UDP | removed after verified compaction | `.sandwurm/exports/pairs/pair.gzgjsiqq` | 359,665,908,232 ns | `782a1f2792ce0576fd7d2de696c5d88641ab652eed19a8c009719a32c85e0f51` |
| forced TCP | removed after verified compaction | `.sandwurm/exports/pairs/pair.hkwzsf05` | 388,925,072,468 ns | `782a1f2792ce0576fd7d2de696c5d88641ab652eed19a8c009719a32c85e0f51` |

Both cells retained:

- generation: `1`;
- artifact bytes: `4,194,304`;
- manifest bytes: `786,496`;
- artifact SHA-256: `1de6e2103a31b5c18b763e77890345d93dfb615af400a4b90c0e0f1c4820fd4e`;
- manifest SHA-256: `3bb8ad40b5677466b9f83b77af9c17f08c7d57313ede8fb4733e2f1323cc1866`;
- signed HEAD record: `60ed8db76d5b2ac931449281e29762cdee0fb300f329072b5d97d853603983ac`;
- first repair aggregate: two inspected, one verified, one quarantined, `4,194,304`
  quarantined bytes;
- recovery aggregate: two verified final objects, zero newly quarantined objects or bytes;
- repair- and recovery-observing roles: `2 / 2`.

The compact UDP and TCP proofs allocate 110,592 bytes each and independently pass the ordinary pair
verifier. Their pair-manifest SHA-256 values are respectively
`d711658d396af2af5acb1a38e4a6f774e1d148ddd852427199570a5cf048b9aa` and
`19f6e46a6f4d03696b7c1d6495e710678458472fd82d37fdf7b8531e65377c93`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-repair
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-repair

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.gzgjsiqq \
  --route direct-udp --scenario sync-file-repair
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.hkwzsf05 \
  --route forced-tcp --scenario sync-file-repair
```

The raw roots contained private writable guest disks and injected test identities. They were removed
after the compact proofs reverified through the binary-pinned pre-GC repair schema; rerunning the
fixture is the recovery path. The current verifier separately requires all GC fields from newer
repair binaries and does not permit a current proof to downgrade into that legacy shape.
During fixture development, a content-free guest failure receipt was added so a failed phase,
generated-script line, repair job status, byte observation, and maintenance diagnostic can terminate
the host wait immediately without exporting content or secrets. One rejected fixture also exposed
an evidence comparison that had not normalized the uppercase digest projection from `sync-status`;
the comparison now uses canonical lowercase before asserting identity.

## Exact nonclaims

This proves explicit quarantine and authorized same-revision recovery for one corrupt target artifact
on ext4-backed Sandwurm guest disks. It does not automatically scrub on read or startup, repair a
corrupt manifest independently, purge quarantine, authorize deletion, prove disk-full or power-loss
behavior, prove deterministic-directory convergence, reject a remotely offered rollback or fork in
this genuine-provider cell, combine multiple sources, activate automatically, or prove
two-physical-host behavior.
