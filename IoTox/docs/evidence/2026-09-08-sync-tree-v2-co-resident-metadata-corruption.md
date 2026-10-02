# Tree-v2 co-resident signed-metadata corruption — 2026-09-08

## Result

IoTox rev0051 qualifies ADR 0339's five-root, co-resident corruption gate on
the founding Sandwurm/Cloud-Hypervisor/KVM/ext4 stack. One networkless VM ran
three source-linked IoTox daemons over an internal loopback Tox mesh with six
directed read/write shares. After convergence, the harness stopped all ten
Agent tasks, changed one final byte in all five live signed metadata roots,
verified the five changed byte strings were simultaneously present while the
tasks remained stopped, and only then resumed the Agent.

Live `sync-repair` refused the first root, branch pointer, with
`protocol-error` / exit 4 without changing any corrupt root. A controlled
stop exited zero. Cold startup then refused at branch pointer with exit 3.
Exact in-place restoration, with file and parent-directory `fsync`, exposed
the next root on each fresh startup in the product's actual validation order:

1. branch pointer;
2. manifest named by that pointer;
3. immutable branch record derived from that manifest;
4. workspace; and
5. maintenance.

Only after all five exact originals were restored did startup succeed. The
original identity and worktree remained intact; all nodes converged to
`[3,3,3]`, and repair succeeded on all three nodes.

## Bound build and topology

```text
source Git commit:       2be7a2aafcf1f54216b9a587809755f684ce83bd
product:                 IoTox 0.51.0 rev0051
binary SHA-256:          9b43ed8ddff00c2a8984dd20cf6bcafd1ac7b1d0af78ba2ffd4fed070bd3481a
proof ID:                run.MG27auOK
substrate:               Cloud Hypervisor / KVM, 2 vCPU, 2 GiB
guest filesystem:        ext4
guest network class:     none
IoTox transport:         loopback-only inside the networkless VM
nodes / directed shares: 3 / 6
stopped Agent tasks:     10
campaign elapsed:        24,207 ms
final tree SHA-256:      1d1c86ea77eadc494258669412902108a02e1e1846ebf7b939bbc6967a12016d
final tree shape:        5 files / 1 directory / 16,411 bytes
final branch counts:     3 / 3 / 3
repair-verified nodes:   3
```

The strict verifier accepts both the raw proof and its compact projection,
including the receipt-v2 stopped-task, co-residency, first-error, controlled
shutdown, ordered-restoration, and completion fields. It accepts the older
rev0050/v1 proof only under its distinct historical family order and product
identity; that compatibility does not upgrade the older proof to v2.

## Compact evidence

```text
proof root:               .sandwurm/exports/sync-metadata-corruption/run.MG27auOK
manifested files:         5
manifested bytes:         10,003
source-proof-root SHA-256:6a70b3f560a1b8671c1e256b46fce9fd12e78b908465cb02dab7c4bd2a6150f7
compact-manifest SHA-256: f1568328078149800eae6cbd13d427155a29001fbd1c647f17a2af46d956ba9b
contains secrets:         false
```

The compact root contains closed summaries of the Sandwurm chain and launch
receipts, plus the exact guest VM-smoke and metadata-corruption receipts. The
strict host verifier checks duplicate-key rejection, receipt schema/product
identity, exact integer types, networkless KVM/ext4 substrate, ordered family
records, and compact digest closure. It commits SHA-256 values of private
startup logs but does not retain or reparse those logs.

Reproduce:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-metadata-corruption
./tools/iotox-sandwurm-lab.sh verify-sync-metadata-corruption \
  .sandwurm/lab/sync-metadata-corruption/RUN_ID
./tools/iotox-sandwurm-lab.sh export-sync-metadata-corruption \
  .sandwurm/lab/sync-metadata-corruption/RUN_ID
./tools/iotox-sandwurm-lab.sh verify-sync-metadata-corruption \
  .sandwurm/exports/sync-metadata-corruption/RUN_ID
```

## Nonclaims and next gate

This is a process-observation fence around sequential same-size writes; it is
not one atomic five-file storage transaction. It proves byte-invalid current
roots are retained and require exact operator restoration on one honest
virtual ext4 stack. It does not prove automatic repair, trustworthy backup
provenance, valid-old complete-frontier freshness without an external witness,
corruption of every durable family, physical power removal, dishonest storage,
or precious-data/sole-copy suitability.

It also does not qualify open-descriptor or remount behavior. ADR 0340 is the
next production gate: retain an exchanged obsolete projection when a held
descriptor writes after exchange, then prove that retention through controlled
restart and ext4 remount before an explicit salvage ceremony.
