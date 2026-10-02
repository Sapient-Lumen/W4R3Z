# Persistent three-writer synchronization capacity and recovery

- Date: 2026-09-03
- Host: IoTox founding x86_64 machine
- Decisions: ADRs 0320--0322, 0329
- Status: accepted bounded construction evidence

## Clean-source retained cell

One fresh 2-vCPU/2-GiB Sandwurm Cloud Hypervisor guest used a persistent ext4 root and no external
network. A private loopback c-toxcore bootstrap connected three distinct source-linked IoTox
daemons. The owners created three friendship edges, all six directed read/write shares, and one
full-mesh tree-v2 namespace.

The capacity phase originated 512 deterministic files of 16,384 bytes on node A. All three ordinary
worktrees converged to the same 8,388,608-byte canonical capacity digest before one explicit repair
per node. The run then stopped all three daemons for unequal edits, retained two conflict
alternatives per node, resolved them causally, rotated 24 sequential edits among the writers,
checkpointed, pinned/unpinned, quarantined/restored two candidates, retired one writer on both
survivors, and refused its attempted re-entry.

| Observation | Result |
| --- | ---: |
| initial branches per node | 3, 3, 3 |
| capacity catch-up | 70,997 ms |
| repair per node | 163 / 318 / 75 ms |
| Agent high-water RSS | 17,084 / 16,768 / 17,280 KiB |
| allocated delta per node | 21,352,448 / 19,894,272 / 19,906,560 bytes |
| conflict alternatives per node | 2, 2, 2 |
| shadow cycles / elapsed | 24 / 108,048 ms |
| watchdog restarts | 0 |
| GC candidates / quarantined / restored | 1 / 1 / 1 |
| survivor branches / sources after cutoff | 2,2 / 1,1 |
| complete guest campaign | 269,284 ms |

The source revision is the clean commit
`61554ea86e6e7208de1d52d20a38491b0bc40f60`. All 24 successor cycles completed without the
watchdog. The fresh-state capacity digest and resolved-conflict digest are byte-identical to the
earlier pressure/recovery cell.

The raw proof root was compacted, verified, and moved from the workspace to recoverable desktop
trash. The retained content-free proof is:

| Proof | Allocated size | Evidence bytes | Binary SHA-256 |
| --- | ---: | ---: | --- |
| `.sandwurm/exports/three-writer/run.XXBBdbmC` | 100 KiB | 88,463 | `4f51c0d2a515f847513c5995a78b38b50bd6d6a15d772084d6fb78fb81f311c6` |

Its five-file compact-export manifest SHA-256 is
`24bf6f84b68504ee5aa9aeab4dd9e665c9e649fb1bfd85ddc5cdee15df1d6b70`; the sync receipt SHA-256 is
`6e5d1100b2564ce1fe143b4a99798051911d61698873f12a7fbae0cbf508928b`. Both the generic VM-smoke
verifier and dedicated three-writer verifier accepted the raw tree before export and the compact
tree afterward. The receipt contains no Tox keys, RecallRoot phrases, paths, content, savedata,
authority secrets, worktrees, or CAS objects.

## Pressure/restart retained cell

The earlier accepted cell used the same binary SHA-256 and identical capacity population. It took
130,219 ms to catch up, 177/58/53 ms to repair, about 16--19 MiB Agent high-water RSS, and about
20--22 MiB allocated growth per node. Its 24 successor cycles took 214,555 ms and the complete run
took 418,235 ms. Cycle 24 crossed the strict 30-second watchdog under ext4 journal pressure; the
wait-channel sample was `do_sys_poll`, `futex_wait_queue`, `hrtimer_nanosleep`, and
`jbd2_log_wait_commit`. Restarting only writer C completed startup reconciliation, preserved the
local edit, reconfirmed both authenticated sessions, and converged the exact cycle before the run
could pass.

That compact proof remains at `.sandwurm/exports/three-writer/run.XXejaDnB` (100 KiB, 88,668
evidence bytes). Its five-file manifest SHA-256 is
`5c8f0cb65680ebc09c1d63a21404c73b317b46d1e31234bd05884320a9bdb814`; its sync receipt SHA-256 is
`3313df2dd58d32d9474cdd02e7acbbe3fe6359d2dbadcf42edbb06e48d21febf`. Its source field names the
then-dirty base revision, but the exact binary hash is byte-identical to the clean-source proof
above. Both verifiers accept it independently.

## Cap-4 lane-window rerun

After ADR 0329 added bounded tree-v2 exact-object lanes and the helper learned to record
`tree_lane_cap`, the same networkless 512-file Sandwurm guest was repeated from clean source revision
`f5078bd482381915f011634727b6621b07175127`. Earlier retries exposed a missing host Node lookup and
two helper API regressions before the accepted retry; none of those rejected proof roots was retained
as accepted evidence.

| Observation | Result |
| --- | ---: |
| `tree_lane_cap` | 4 |
| capacity files / logical bytes | 512 / 8,388,608 |
| capacity catch-up | 37,090 ms |
| repair per node | 55 / 83 / 56 ms |
| Agent high-water RSS | 17,732 / 18,688 / 16,252 KiB |
| allocated delta per node | 21,647,360 / 19,873,792 / 19,857,408 bytes |
| shadow cycles / elapsed | 24 / 97,769 ms |
| watchdog restarts | 0 |
| recovery rehearsal | passed / 109,085 ms |
| storage-fault rehearsal | passed / 211,237 ms |
| abrupt exchange observed | pending-workspace |
| final storage-fault bytes | 33,620,017 |

The retained compact proof is `.sandwurm/exports/three-writer/run.5OJVbUl2` (104 KiB, 90,904
evidence bytes). Its compact-export SHA-256 is
`08042a62b8001af70a8652a39a8a7c27d57f4c066f5158bc7c631bb6881f9db4`; the sync receipt SHA-256 is
`10d7faf13c584073817bdd2982b2e681a4077e271d99fa69b67f86b359ed3659`; the VM-smoke SHA-256 is
`7a456450091ba578edc45d9ef223e285d31408184a83ad859cdabd736ce4ff6e`. Both verifiers accepted the
compact proof. The IoTox binary SHA-256 is
`5cdc1e1ced100c72355b50fbbfd41fe8ca004853fd2534b55fcee367222822ea`.

This rerun updates the established 512-file VM evidence under the default cap-4 lane window. It does
not replace a near-ceiling one-lane/four-lane Sandwurm comparison.

## Rejected diagnostic cells

The path to the accepted cell retained failures as engineering evidence, never as passes:

- The unbatched 512-file baseline reached only nine shadow cycles in roughly 522 seconds; eight
  crossed the watchdog and required restart. Read-only inspection sampled ext4 journal and block-I/O
  waits. Its synthetic raw tree was deleted after diagnosis.
- The first batched build cut explicit conflict resolution from about 16.8 seconds to 2.1 seconds
  and its first successor to 3.6 seconds, but cycle 2 remained pending after writer restart. The
  signed workspace and both directory markers proved that the new projection was visible and the
  exact old projection remained staged. This exposed absent startup workspace reconciliation.
- With startup reconciliation added, cycle 3 failed closed because the visible tree matched neither
  exact signed side. Read-only manifest comparison proved an exact staged cycle 1, a visible
  pending-cycle-2 marker, and intact cycle-3 user bytes. ADR 0322 adds this crash-forward join.
- A later fresh cell exchanged branches only between B and C. The harness had called authenticated
  `sync-repair` on A at 10 Hz while short-circuiting before B/C. Replacing that observer with a
  canonical filename count restored initial convergence to 21.6 seconds in the accepted retry.

Every rejected raw tree contained only synthetic state. Each was detached from read-only inspection
and permanently deleted; none produced or was promoted as an accepted receipt.

## Reproduction

```bash
./tools/iotox-sandwurm-lab.sh up-three-writer
./tools/iotox-sandwurm-lab.sh export-three-writer RAW_PROOF_ROOT
python3 tools/verify-sandwurm-vm-smoke.py COMPACT_PROOF_ROOT device
python3 tools/verify-sync-three-writer-sandwurm.py COMPACT_PROOF_ROOT
```

The VM cell always uses fresh identities and state. A direct harness invocation retains keys by
default and requires `--fresh-state` to replace them.

## Evidence boundary

These are same-computer, same-hypervisor, networkless construction cells. Together they prove a
repeatable useful persistent-disk population, three-node catch-up, exact repair, bounded memory/disk
observations, one real journal-pressure restart recovery, cap-4 lane-window operation on the
established 512-file VM gate, and the named lifecycle. They do not prove independent administration,
physical storage durability, near-ceiling performance, cold-cache repeatability, 24-hour stability,
abrupt power loss, ENOSPC/read-only recovery, hostile writers, open-descriptor write safety,
non-Linux portability, backup independence, or precious-data readiness.

A later direct-host 3,500-file/57,344,000-byte diagnostic timed out before follower projection. That
run is recorded separately as rejected bottleneck evidence in
`2026-09-03-sync-near-ceiling-timeout.md`; it is not part of this accepted Sandwurm capacity proof.
