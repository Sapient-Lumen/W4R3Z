# Sandwurm synchronization GC quarantine evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently exercised the quarantine-only collector
after signed generation-1 file convergence and explicit activation over observed direct UDP. Each
guest:

1. bind-mounted an empty private directory over the namespace `objects` directory and required
   `sync-gc sandwurm-file dry-run` to refuse the mount boundary;
2. unmounted it and proved both live digest-named objects remained exact;
3. created two sentinels outside the namespace root and recorded their SHA-256 values;
4. installed one valid 32,768-byte digest-named but unreferenced artifact;
5. required dry-run to report two rooted objects and one candidate without creating quarantine;
6. required quarantine to move that exact device/inode, report one moved and one durable object, and
   retain `purge=disabled`;
7. reverified both live object digests, the quarantined object digest, and all four outside-root
   sentinels; and
8. required exact retry to report zero candidates and zero effects while preserving quarantine.

The same scenario also retained its earlier corrupt-target repair/recovery assertions. The GC result
is local filesystem evidence; the Tox carrier establishes that it ran inside the complete production
guest/Agent/control construction rather than making GC a network operation.

## Accepted cell

| Route | Raw private proof | Compact proof | Span | Binary SHA-256 |
|---|---|---|---:|---|
| direct UDP | removed after audited compaction | `.sandwurm/exports/pairs/pair.ci0p3t6f` | 289,672,103,225 ns | `829ec298709f831899a37ec1abd062b3755fedbdb717d67b80e0768e5689dda3` |

The manifest binds two GC-observing roles, two mount refusals, four preserved outside-root sentinels,
one dry-run candidate per role, one moved and durable object per role, and two purge-disabled roles.
Client and device receipt SHA-256 values are respectively
`5dbe7d49006d682e5416049929a8c3354e2f2655c0efb40b82eb5e26f20add20` and
`898603cd65ca69db18104d91457e66dbe9c933ae737b79307a3fe65fd5475954`.
The compact pair manifest SHA-256 is
`c5bafce7c0a547ea83e2b591b6ae8acd5abff95f1f7b7d77a2568da2381155c2`; the compact-export
declaration SHA-256 is
`d74ee6046118e684b2e1e0dca8295cb10582a587b07c481277f6de1a11588421`.
The independently reverified compact proof allocates 122,880 bytes and contains no secrets or private
guest disk.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-repair
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.ci0p3t6f \
  --route direct-udp --scenario sync-file-repair
```

The raw proof contained private writable guest disks and injected test identities. It and the weaker
pre-mount development proof were removed after the current compact proof passed the ordinary strict
verifier; they are recoverable only by rerunning the fixture.

## Exact nonclaims

This does not purge quarantine, prove coordinated-rollback resistance, provide an independent
monotonic witness, qualify automatic/startup collection, prove abrupt power-loss behavior, authorize
remote collection, prove a second physical host, or qualify every filesystem/kernel. Forced TCP is
not repeated because collector semantics are local and transport-independent; the encompassing
repair/convergence scenario already has separate historical direct-UDP and forced-TCP evidence.
