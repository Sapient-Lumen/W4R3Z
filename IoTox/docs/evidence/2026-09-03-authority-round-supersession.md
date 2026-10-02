# Authority round supersession

- Date: 2026-09-03
- Host: IoTox founding x86_64 machine
- Decision: ADR 0324
- Status: direct state-machine and replacement Sandwurm gates accepted

## Rejected KVM observation

Clean source revision `0f74d3d` completed the existing persistent three-writer capacity phase in a
2-vCPU/2-GiB Sandwurm KVM guest, then failed the recovery rehearsal's initial 180-second branch wait.
The rejected raw proof was
`.sandwurm/lab/three-writer/run.XXOhgabk`. Its guest journal reported:

```text
sync recovery rehearsal failed: timeout waiting for recovery full-mesh branches
```

The stopped task disk was mounted read-only with journal replay disabled. Node 1 held only its own
branch. Nodes 2 and 3 each held their own and the other's branch. Both reported one
`awaiting-authority-proof` session; node 1 reported none. All three exact ledgers contained the
expected three active principals. This identifies an asymmetric second-challenge stall rather than
object corruption or missing durable grants.

This run has status `launched-without-guest-evidence`; it is rejected and is not qualification
evidence.

## Direct gate

The existing `ledger mutation immediately invalidates a previously proven principal` check now
freezes a challenge, advances the ledger a second time before proof preparation, and requires the
strict successor challenge to replace the unfinished round. It then signs and verifies the latest
head and injects a different nonce at the same head, which remains a protocol error.

```sh
nix develop --command ctest --test-dir build/gcc-debug \
  -R '^iotox\.unit-and-integration$' --output-on-failure
```

Result: 831/831 owned checks passed in 33.70 seconds.

## Replacement Sandwurm gate

Clean source revision `2d5e869f72e94e3591c6b5b1ffe1aa1bbc5f6b69` ran the byte-identical
source-linked binary SHA-256
`705d65f96e64c13d4d6079a787e28d12bb02a62467697e18bbe9ada84110d010` in the same 2-vCPU/2-GiB
guest class. It crossed all six rapid initial grants, converged all three branches, and completed the
entire capacity/conflict/maintenance phase. The recovery phase then crossed a further six-edge mesh,
the survivor restart and authority re-proof barrier, the empty replacement, complete live-node loss,
and a final six-edge fresh-identity mesh. No authority session remained awaiting proof.

The accepted proof is `.sandwurm/exports/three-writer/run.XXJGHoNd`; the recovery phase completed in
97,238 ms and the compact manifest SHA-256 is
`81213534d4754ad8cd8bebe04838b39d88205e87e092271d6c3b9d8191b72439`. This is causal system
evidence paired with the deterministic state-machine check, not a proof that every network schedule
has been explored.

## Evidence boundary

The direct gate proves the authority-registry state transition. The rejected VM makes the original
liveness defect reproducible and localizes the asymmetric stall; the clean replacement crosses that
exact boundary and the larger recovery ceremony. This is not a network-availability guarantee,
exhaustive schedule proof, independent-backup result, or precious-data claim.
