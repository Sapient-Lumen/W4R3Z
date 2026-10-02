# ADR 0281: Close the bounded tree-v2 adversarial gate

Status: accepted, 2026-09-01

## Context

Tree-v2 already had causal merge, signed branch/store checks, pending-exchange recovery, maintenance,
and real three-daemon lifecycle evidence. Its roadmap gate remained open because those facts were not
accounted as one finite adversarial matrix, and neither the full conflict nor ordinary tree ceiling
had been exercised.

"Every crash edge" is meaningful only against named durable transitions. It cannot mean every
possible instruction or storage failure. The gate therefore needs an exact list that can be kept in
the owned registry.

## Decision

The founding bounded matrix consists of:

1. CAS install temporary cleanup and unsafe temporary refusal;
2. branch-current atomic temporary cleanup, same-writer fork refusal, and signed-record tamper;
3. signed workspace initialize/begin/finish replay plus record tamper and foreign-signer refusal;
4. pending worktree exchange recovery before rename, after rename with the old tree at staging, and
   fail-closed preservation when neither visible tree matches;
5. checkpoint-branch commit before workspace-marker recovery;
6. signed terminal-cutoff commit before current-branch retirement and exact retry;
7. recoverable GC quarantine/restore, tampered quarantine refusal, and symlink-shaped inventory
   refusal; and
8. the existing eight-point treepack projection process-crash matrix.

Exercise the conflict ceiling with 16 independently signed concurrent writers at one path in 128
seeded arrival permutations. All results must be byte-identical, and candidate 17 must fail with
`resource_exhausted`. Retain the exhaustive six arrival permutations for three writers and the real
three-daemon offline conflict/resolution lifecycle.

Exercise the default tree population ceiling with 4,096 unique regular files through scan, CAS
import, branch signature, merge, and projection. ADR 0280 repairs the nominal-manifest-size defect
this test exposed while preserving every formerly valid digest.

Use the 24-cycle networkless three-daemon lifecycle for long-offline/checkpoint/pin/GC/cutoff and
retired-writer re-entry. Use the two-hour incumbent shadow in ADR 0283 for real-directory duration;
the two gates share that receipt rather than rerunning an artificial second soak.

## Consequences

The roadmap's adversarial/scale gate now refers to this finite matrix. It does not claim arbitrary
filesystem semantics, formal crash consistency, a hostile kernel, storage that lies about `fsync`,
more than 4,096 entries, or more than 16 competing values at one path. Those are outside the frozen
product bounds rather than untested promises.
