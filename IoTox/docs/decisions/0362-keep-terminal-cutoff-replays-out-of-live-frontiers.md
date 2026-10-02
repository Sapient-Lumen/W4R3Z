# ADR 0362: Keep terminal cutoff replays out of live frontiers

- Date: 2026-09-10
- Status: accepted

## Context

The first duration-bound three-writer soak/recovery run from ADR 0361 exposed a recovery stall after
retiring one writer. Both surviving writers had accepted the same terminal cutoff for the departed
writer and each reported one surviving remote source principal, but the retired writer's exact
terminal branch record could still be re-offered later and become a live
`tree-v2/branches/<writer>.branch` pointer again.

That record is valid historical evidence. It is the precise head named by the cutoff and must remain
available for history validation, repair, and garbage-collection rooting. It is not current writer
authority and must not re-enter the live frontier after retirement.

## Decision

`TreeV2BranchStore::accept` now consults the local maintenance cutoff state when it is constructed
with a local device key.

- A branch for a writer with no terminal cutoff follows the normal genesis, duplicate, checkpoint,
  and advance rules.
- A branch that is outside an existing terminal cutoff is refused.
- A branch that exactly matches the terminal cutoff generation and record is accepted as
  `retired-terminal`: its manifest and immutable branch record are installed or reused, a matching
  pointer is retained below `tree-v2/retired-branches/`, any exact live branch pointer for that writer
  is removed, and the state witness removes that writer from the live frontier.

The direct regression `tree-v2 branch store keeps terminal cutoff replay retired` freezes both the
fresh exact-replay case and repair of a bad state where the same terminal bytes exist as both a live
and retired pointer.

## Consequences

Retired writer history remains reusable without silently granting the retired writer live membership
again. Replacement nodes can validate old cutoffs and historical records while the current frontier
stays limited to active writers.

This does not replace the operational retirement ceremony: survivors still need the cutoff, authority
revocation, Tox friendship removal, ordered checkpoint exchange, and reseeding flow. It also does not
prove backup independence, a 24-hour soak, or dishonest-storage behavior.

## Evidence

The repaired tree passed the focused CTest slice, direct recovery/soak controls, and the accepted
Sandwurm same-host/KVM/ext4 proof `.sandwurm/exports/three-writer/run.UFBCMzt9`. That compact proof
includes the short three-writer writable soak, retained recovery-provenance bindings, and
storage-fault follow-up from the same source-linked binary.
