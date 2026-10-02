# Sandwurm three-writer synchronization evidence

Date: 2026-08-31

Status: accepted construction evidence

Lifecycle note: this historical gate predates checkpoint, GC, and writer-cutoff support. Its exact
nonclaims remain true for this cell; the later accelerated lifecycle claim is retained separately in
`2026-09-01-sandwurm-sync-three-writer-lifecycle.md`.

## Claim

One networkless Sandwurm/KVM guest ran a private loopback c-toxcore bootstrap and three distinct
source-linked IoTox daemons. The owners established all three friendship edges and all six
directional read-write shares for one tree-v2 namespace. Every local automation-v2 record named the
other two stable principals.

After all daemons were stopped, each worktree wrote a different value to the same path. Restart and
unattended reconciliation produced three authenticated branches and the same deterministic ordinary
projection plus exactly two provenance-bearing alternatives at every node. A later ordinary edit on
one node, made after it had observed all three fronts, removed the conflict and converged to the same
digest everywhere.

The Cloud Hypervisor launch exposed no network device. Tox traffic remained inside the guest's
loopback network namespace; no external bootstrap, relay, route, or service participated.

## Accepted cell

| Proof | Allocated size | Evidence bytes | Binary SHA-256 |
|---|---:|---:|---|
| `.sandwurm/exports/three-writer/run.XXbLFcpO` | 100 KiB | 87,445 | `fca848cc73403c33d160a753db77804facee06cc339f8a294581123b6d6cd8cd` |

The five-file compact-export manifest SHA-256 is
`f6f05c66123185f1b33474b22c8576f783383a34e2eeb755ff3c5e9394b53953`. Both the generic IoTox VM
smoke verifier and the dedicated three-writer verifier accepted the compact tree after export.

The content-free qualification receipt records:

| Observation | Result |
|---|---:|
| distinct Tox identities / stable principals | 3 / 3 |
| friendship edges / directional owner grants | 3 / 6 |
| remote principals per automation record | 2 |
| branch count per node | 3, 3, 3 |
| conflict alternatives per node | 2, 2, 2 |
| periodic scheduler attempts per node | 50, 46, 44 |
| automation format / fixed bytes | 2 / 4,808 |
| fixture elapsed time | 71,830 ms |
| explicit causal resolution | observed |

The resolved content digest is
`2e36c7c239464b968cb222c88a12f4157d66e3ca8877ab1156c4b5f8019fe835`. Content itself, RecallRoot
phrases, Tox savedata, authority private material, worktrees, CAS objects, and writable guest disks
are absent from the retained proof.

## Reproduction, export, and verification

```bash
./tools/iotox-sandwurm-lab.sh up-three-writer
./tools/iotox-sandwurm-lab.sh export-three-writer RAW_PROOF_ROOT
python3 tools/verify-sandwurm-vm-smoke.py COMPACT_PROOF_ROOT device
python3 tools/verify-sync-three-writer-sandwurm.py COMPACT_PROOF_ROOT
```

The harness uses persistent `.cache/sync-three-writer/state` by default, so ordinary repeated host
runs reuse the three Tox identities, stable devices, and owner state. Pass `--fresh-state` directly
to `tools/run-sync-three-writer.py` only for a from-scratch ceremony; the ephemeral VM gate does so.

That default was exercised twice against the same host state. The first content-free receipt
`.sandwurm/three-writer/reuse-first.json` has SHA-256
`e523c8e7b6c849dcc39d1f195dab2d62de4d070f3a28b973dff3508c77367b27` and reports
`state_reused=false`; the second has SHA-256
`2f0b123b530832d47115b772f39166e488fa9274ebcc81fdea47116c686ca6f8` and reports
`state_reused=true`. All three Tox-key hashes and all three stable-principal hashes are identical
across the pair. Both runs reproduce three branches, two alternatives per node, and explicit
resolution. This also exercises loaded authority-v3 state rather than replaying the bootstrap and
migration ceremony.

The successful raw root allocated 1.5 GiB and was removed from the live lab only after the compact
copy passed both verifiers. It was moved to the sandbox user's recoverable Trash; after that Trash is
emptied, rerunning the fixture or restoring a machine snapshot is the recovery path. Four incomplete
or superseded three-writer roots and six earlier superseded pair roots were removed by the bounded
workspace cleaner, reclaiming another 12.6 GiB.

## Exact nonclaims

This is a same-computer, one-VM deterministic construction cell, not independent-machine or hostile
network evidence. It does not qualify partial-mesh forwarding, automatic group membership,
revoked-writer cutoff, long-offline retention, malicious forks, conflict storms, power loss,
large-tree performance, filesystem watching, metadata portability, encryption at rest, or
recoverable tree-v2 garbage collection. It does not make the synchronized worktree a safe sole copy
of important data.
