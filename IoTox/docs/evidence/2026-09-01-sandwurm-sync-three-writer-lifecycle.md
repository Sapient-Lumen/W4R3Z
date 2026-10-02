# Sandwurm three-writer lifecycle evidence

Date: 2026-09-01

Status: accepted accelerated construction evidence

## Claim

One networkless Sandwurm/KVM guest ran a private loopback c-toxcore bootstrap and three distinct
source-linked IoTox 0.46.0 rev0046 daemons with 2 virtual CPUs and 2 GiB RAM. The owners established
three friendship edges, all six directional read-write shares, three stable writer branches, a
three-way offline conflict, and one explicit causal resolution. Twenty-four subsequent sequential
edits rotated across the writers and converged without conflict or manual publish/pull.

After convergence, one writer created a negotiated format-2 checkpoint. Both remote stores received
the checkpoint. The local owner pinned and unpinned its exact record, planned two unreachable graph
objects, quarantined both with no-replace moves, and authenticated and restored both. The third
writer was then stopped. Each of the two survivors committed an exact terminal cutoff for it,
reduced its active frontier from three branches to two, and reduced its automatic remote sources
from two to one. Restarting the retired writer with a new local edit did not return that edit or its
branch to either survivor.

The Cloud Hypervisor launch exposed no network device. Tox traffic stayed inside the guest loopback
network namespace; no external bootstrap, relay, route, or service participated.

## Accepted cell

| Proof | Allocated size | Evidence bytes | Binary SHA-256 |
|---|---:|---:|---|
| `.sandwurm/exports/three-writer/run.XXiFEDeB` | 100 KiB | 87,993 | `4ee0f545a852ec11eb42363e141ae21d9ac20100ae241fd84d8314d6f3bbad88` |

The five-file compact-export manifest SHA-256 is
`e1ccc7a37b617361396658fbdc53db081578a0ff26c94450383fb5064b4843da`.
Both the generic VM-smoke verifier and the dedicated three-writer verifier accepted the compact tree
after export. The source-linked package used by the corresponding final native run was
`/nix/store/s2q6blva66x3igz0lwipdgai9wj55dz1-iotox-source-linked-0.46.0-rev0046`.

The content-free guest receipt records:

| Observation | Result |
|---|---:|
| distinct Tox identities / stable principals | 3 / 3 |
| friendship edges / directional owner grants | 3 / 6 |
| initial branch count per node | 3, 3, 3 |
| conflict alternatives per node | 2, 2, 2 |
| shadow cycles / elapsed | 24 / 37,333 ms |
| periodic scheduler attempts per node | 5, 6, 6 |
| checkpoint copies at remote nodes | 2 |
| GC candidates / quarantined / restored | 2 / 2 / 2 |
| cutoff survivors | 2 |
| survivor branch counts after cutoff | 2, 2 |
| survivor remote-source counts after cutoff | 1, 1 |
| retired-writer re-entry | refused |
| watchdog restarts | 0 |
| complete fixture elapsed time | 98,947 ms |

The resolved content digest is
`2e36c7c239464b968cb222c88a12f4157d66e3ca8877ab1156c4b5f8019fe835`.
Content itself, RecallRoot phrases, Tox savedata, authority private material, worktrees, CAS objects,
and writable guest disks are absent from the retained proof.

## Intermittent pending-exchange observation

The immediately preceding constrained cell,
`.sandwurm/lab/three-writer/run.XXHenEIi`, did not produce guest evidence before its 20-minute
deadline and is not an accepted proof. Read-only inspection of its preserved ext4 root showed that
all six shares, the three-way conflict, resolution, and five shadow cycles had completed. On cycle
six, node C had atomically exposed the new worktree, but its signed workspace remained in
`pending_exchange`; the old projection remained in the same-parent staging directory and A/B stayed
on cycle five. This is an intermittent availability observation, not evidence of content loss: the
visible directory and signed pending journal identified both orientations exactly.

The qualification harness now prints bounded stage progress, uses a 180-second convergence bound
rather than placing a 900-second inner wait beneath a 1,200-second guest deadline, and can capture
kernel wait-channel names and restart only the stalled writer after 30 seconds. An unresponsive
control socket is bounded before process-group termination. Restart must reconfirm both sessions and
finish the same cycle before the run may continue. The accepted retry did not need that recovery
path, so the actual ext4 stall and watchdog-assisted recovery still need deliberate fault injection
or repetition; unit/process tests remain the direct pending-exchange recovery proof.

## Reproduction, export, and verification

```bash
./tools/iotox-sandwurm-lab.sh up-three-writer
./tools/iotox-sandwurm-lab.sh export-three-writer RAW_PROOF_ROOT
python3 tools/verify-sandwurm-vm-smoke.py COMPACT_PROOF_ROOT device
python3 tools/verify-sync-three-writer-sandwurm.py COMPACT_PROOF_ROOT
```

The VM gate always uses fresh state. Direct harness runs retain their state root by default and use
`--fresh-state` only for an explicit from-scratch ceremony.

## Exact nonclaims

This is accelerated same-computer construction evidence, not hours-long deployment or independent-
machine evidence. It does not qualify malicious authorized writers, signed forks, conflict storms,
power cuts, very large trees, case-folding or metadata portability, ignored paths, encryption at
rest, hardware rollback witnesses, transitive group membership, or permanent purge. A checkpoint
is one authorized writer's signed frontier attestation, not multisignature agreement by every
writer. Cutoff is repeated owner-local policy on each survivor, not consensus or general authority
revocation. ADRs 0281 and 0283 subsequently close the adversarial and long-shadow gates with distinct
evidence; this accelerated receipt's own claim remains unchanged. Synchronization still is not an
independent backup.
