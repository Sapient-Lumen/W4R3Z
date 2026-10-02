# Sandwurm content replica cold-start evidence

Date: 2026-08-30

Decision: ADR 0257

Result: accepted for availability-only replica recovery over direct UDP

## Claim

One subscriber and two independently authenticated complementary publishers ran as three IoTox
agents in two simultaneous Sandwurm/Cloud Hypervisor guests. The secondary imported the primary's
valid content-v2 signed HEAD into its distinct replica store, proved that no local publication was
created, and retained only the immutable objects it physically held. After selected-source failure,
that same secondary identity cold-started from the replica without any post-start HEAD injection,
completed a consistent zero-candidate GC traversal, returned at a higher authenticated epoch, and
contributed to a distinct explicit atomic recovery pull.

This qualifies durable availability metadata for one partial replica. It does not make the replica
a publisher, accepted-HEAD writer, activation authority, or transparent continuation of the failed
job. It is a one-machine/two-VM native-UDP experiment, not a two-physical-host result.

## Retained proof

The secret-free compact proof is `.sandwurm/exports/pairs/pair.w_ws202c` and allocates 188,416 bytes.
Both it and the 2.4 GiB disposable private source proof passed strict verification with route
`direct-udp`, scenario `sync-content-multi-source-loss`, and observed connection `udp`.

```text
IoTox binary SHA-256             7cbc8f5ff80faa5f49876efa083798f2c3a549d5af47990f3f5b683d8227f83e
client receipt SHA-256           945367a7d606a982d63e7bcdc03234c6848df758d76656e11b47c02e8532339c
device receipt SHA-256           c07adf4c9222d9404d8e6e2fa12fcb5fd8cd488c5778e5b7bd5f9ba3d51cf8ce
source manifest SHA-256          5a9d8d9e53ee5b0d838d69370bbe5468f2e4ed3337fe036ee3e6d9b8617ef5f1
compact manifest SHA-256         6aeaf0cd9de994036a7c6301fb4c6a139b96014c25c588ade00272eb1f8ce897
compact export SHA-256           01306629e9bb4e7845292b4f210f271a12c621431ee63cda142d47fdcb74ca55
replica-import checkpoint SHA-256 084d2cf048af1b14bf856dfdc3974022abe0edaa69237147dc8e678fd4470f71
cold-start checkpoint SHA-256    1887118a9e09f71fa940861cd1941354b9f173c2ea258c3e8573929b1d172b75
signed-HEAD record SHA-256       5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c
```

The compact exporter omitted guest disks, injected identities, bootstrap secret key, and live
runtime state. Its per-file digest map includes both new checkpoints, so strict replay binds their
exact bytes rather than merely trusting summary counters.

## Exact observations

```text
atomic multi-source pull observed roles       2
sources                                       2
availability requests/results                 4 / 4
primary/secondary physical CAS objects        5 / 2
first/replacement jobs                        7063742433837224666 / 4755243178061663929
secondary object requests before stop         1
verified objects retained from failed job     2
verified bytes retained from failed job       528
secondary authenticated epoch                 1 -> 2
secondary Agent restarts                      1
durable replica cold start                    true
constructed replica reinjection               false
local published HEAD at secondary             absent
replica GC traversal                          complete and consistent
replica GC candidates                         0
```

Before the fault, `sync-replica-import sandwurm-file SIGNED_HEAD_PATH` returned the exact HEAD
record and wrote a device-custody envelope. The import checkpoint records
`authority=availability-only`, `published-head=0`, and `replica-head=1`. The later checkpoint records
`durable-replica-head-cold-start=1`, `published-head-absent=1`, and `replica-gc-consistent=1`.

The first job still failed whole: the subscriber retained no accepted HEAD or activation and
cleaned transient staging/CTA1 state. The replacement job has a distinct ID and is the only job that
converged. Persistence therefore repairs source restart, not the atomic failure boundary.

## Repository validation

- GCC Debug: 664/664 owned checks and 46/46 CTest entries passed in the pinned development shell;
- Clang Debug: warnings-as-errors build plus the same 664/664 and 46/46 passed;
- five cgroup process entries were expected skips in both compiler lanes because the shell lacked a
  delegated writable cgroup subtree;
- the Sandwurm runner, verifier, exporter, and Ratox terminal-probe self-tests passed;
- both the historical reinjection proof `pair.xujufman` and the durable proof `pair.w_ws202c` passed
  the hardened verifier, which requires exactly one of the legacy or durable claims; and
- `nix flake check` passed with the new source files present in the Git-backed flake closure.

## Reproduction

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-content-multi-source-loss
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.w_ws202c sync-content-multi-source-loss
```

The raw proof contains private guest disks and is intentionally disposable after compact export and
strict replay.

## Nonclaims

This evidence does not qualify transparent in-job source replacement, subscriber daemon/guest
restart, replica discovery or automatic admission, more than one replica writer chain, simultaneous
content lanes, byte striping, forced TCP, Tor or I2P, comparative speedup, two physical hosts,
arbitrary timing, hostile filesystems/kernels, power loss, permanent GC purge, fleet behavior, or
unattended update safety.
