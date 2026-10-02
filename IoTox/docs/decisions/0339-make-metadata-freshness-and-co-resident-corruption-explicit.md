# ADR 0339: Make metadata freshness and co-resident corruption explicit

- Status: accepted, implemented, and qualified on the founding Sandwurm/KVM/ext4 stack
- Date: 2026-09-08

## Context

ADR 0337 proves that one byte-invalid live record from each of tree-v2's five
signed metadata families is rejected without mutation and can be reopened only
after exact external restoration. That result answers an integrity question,
not a freshness question. A cryptographically valid old record still verifies
unless an independently stored rollback witness remembers a newer complete
semantic root.

The first gate also mutates one family at a time. It does not show the behavior
when all five invalid roots are present together, and the phrase
`metadata=verified` in successful `sync-repair` output does not tell the
operator whether an external freshness witness participated.

## Decision

1. Successful tree-v2 `sync-repair` output includes
   `rollback-witness=0|1`. `metadata=verified rollback-witness=0` means that
   signatures, canonical encodings, references, and selected content passed;
   it must never be read as an anti-rollback claim.
2. Deterministic witness tests retain two complete points for each mutable
   semantic-root family that can be independently replayed: branch pointer,
   signed workspace, and signed maintenance state. They restore the exact old
   record and its matching old local guard while the external witness remains
   current. Both a live read and a replacement/cold reconciliation must return
   `protocol_error`, retain local bytes, and leave the external witness
   unchanged. Restoring the exact current record and guard must recover.
3. Immutable branch records and manifests remain content addressed. Replacing
   either at its current digest path with different valid old bytes is not a
   coherent substitution; complete-frontier rollback is instead covered by
   ADR 0314's witness gate.
4. Metadata-corruption receipt v2 adds a second experiment after ADR 0337's
   five sequential cells. The harness stops the complete Agent process group,
   verifies every Agent task is stopped, applies the five same-size bit flips
   sequentially, verifies that all five corrupt byte strings are co-resident
   while the tasks remain stopped, and only then resumes the Agent. This is a
   process-observation fence, not an atomic storage transaction.
5. With all five roots corrupt, live `sync-repair` must refuse at the branch
   pointer and retain every corrupt byte string. A controlled Agent shutdown
   must succeed with exit zero. Cold startup must then refuse at the branch
   pointer. Exact restoration of one family at a time must expose the next
   family in the frozen startup-validation order: branch pointer, manifest,
   immutable branch record, workspace, maintenance. The manifest precedes the
   derived immutable record because the pointer must first name an
   authenticated manifest from which the record digest is derived. Only the
   final exact
   restoration may permit startup, identity/worktree preservation, full-mesh
   convergence, and repair.
6. The strict host verifier accepts the retained rev0050 v1 proof and the new
   rev0051 v2 proof under distinct exact product identities. It reports the
   receipt schema and `simultaneous_receipt_verified=true|false`; this states
   what the closed receipt proves, not that the compact verifier independently
   observed guest threads or omitted startup logs.
7. The NixOS guest predicate is an early smoke assertion. The source-tree
   Python verifier with closed schemas, exact integer types, duplicate-key
   rejection, and compact digest closure remains mandatory after Sandwurm
   returns the proof to the host.

## Consequences

Integrity and freshness are now visible as separate operational properties.
An unwitnessed namespace can be useful and cryptographically authenticated,
but snapshots of its complete signed state can still roll it backward. The
external witness is the only implemented anti-rollback authority, and it is
operationally independent only when its service, keys, and checkpoints live
outside the Agent disk/admin/snapshot failure domain.

The co-resident experiment is stronger than five isolated corruptions but
remains deliberately narrow. The harness observes each mutation while the
Agent is stopped; it does not claim one atomic five-file storage write. Live
`sync-repair` is exercised once and exposes only the first invalid family.
The ordered peeling result comes from fresh startup processes. Compact proof
retains the guest's closed classification assertions and hashes of private
startup logs, not the logs themselves, so the host does not independently
reparse their text.

## Qualification record

Source-linked Sandwurm run `MG27auOK`, from commit
`2be7a2aafcf1f54216b9a587809755f684ce83bd`, passes the receipt-v2 gate on
the founding networkless Cloud-Hypervisor/KVM/ext4 stack. Its 10,003-byte
content-free compact proof is
`.sandwurm/exports/sync-metadata-corruption/run.MG27auOK`; both raw and
compact roots pass the strict verifier. See
`../evidence/2026-09-08-sync-tree-v2-co-resident-metadata-corruption.md`.

This does not add automatic repair, peer-supplied replacement, trustworthy
backup provenance, dishonest-storage protection, or a physical power-cut
claim. A witness outage fails closed. Emergency witness replacement and
re-anchoring remain explicit operator ceremonies rather than availability
fallbacks.
