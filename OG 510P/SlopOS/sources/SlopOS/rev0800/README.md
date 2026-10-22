# SlopOS — Epoch Zero closure office

**Revision:** 0800
**Lifecycle:** OPEN
**Epoch:** EPOCH_ZERO / CLOSURE
**Archive:** `SlopOS-rev0800-2026.07.15.03.06-proposerefine-valuesnapshot-custodyspine-fortiethforge.zip`

SlopOS is an experiment in **effect sovereignty**: consequential state change must
not follow merely because a proposal, model, program, operator, agent, receipt, or
observation says it should. The promotion chain must remain reviewable:

```text
intent -> explicit attenuated authority -> deterministic admission
       -> smallest justified effect -> completion/currentness observation

requirement -> specification -> refinement -> source/compiler/binary
            -> platform/configuration-scoped claim
```

The permanent non-promotions are equally important: proposal is not authority;
authority is not admission; admission is not effect; effect is not completion or
current state; observation is not authority; evidence is not proof; old proof is not
current proof; and the preserved vault is not the living project.

## Epoch judgment

Epoch Zero remains **OPEN**. Rev0800 closes a bounded PROPOSE value-correspondence
edge, but the pinned Isabelle session has not run, the vertical C++20 source relation
is not mechanized, the other authority operations remain outside this edge, no
privileged effect is justified end to end, and no independent reviewer has accepted
the exact final basis.

## What rev0800 constructs

1. `AuthorityCore` and `AuthorityReference` now expose the same typed,
   copy-only `AuthorityValueSnapshot`. Occupied proposals and leases are sorted into
   prefixes with exact default tails; all resources and the finite sequence are
   copied. Text rendering is downstream from this value image.
2. A separate `slopos_authority_refinement` library implements one independent
   PROPOSE expected-state transformer. It names the exact first-failure order and
   rejects any wrong outcome, insertion, sequence, prior proposal, lease, resource,
   or snapshot shape.
3. A private terminal-sequence test relates concrete core/reference execution to the
   checker. The production classes still expose no sequence setter.
4. `P0_Authority_Propose_Refinement.thy` states bounded HOL command/context
   semantics with explicit 16/64-bit value bounds, fixed capacity, exact denial
   frame, exact selected proposal registration, one sequence advance, and context
   validity preservation. The formal gate remains BLOCKED until Isabelle2025-2 runs.
5. Vault excavation recovered the old independent-model/canonical-observation law
   without importing old snapshot code, proof-registry sprawl, or a generated
   PROPOSE language. A future custody recovery pack is specified only as a reversible
   derivative; original archives remain immutable.

A fresh Ninja dry run is **103 active steps versus 253 full-research steps**. The
seven-step increase over rev0799 is the bounded refinement library/test, not a
reopened platform ladder.

## Open the office

```sh
cmake -S . -B build/debug -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DSLOPOS_BUILD_LEGACY_M0=OFF
cmake --build build/debug
ctest --test-dir build/debug --output-on-failure \
  -E '^(proof-toolchain-doctor|isabelle-session-current|office-audit|office-custody-audit|office-open|office-close-remains-open)$'
build/debug/slopos-harness --authority-propose-refinement
build/debug/slopos-office audit --root .
build/debug/slopos-office resume --root .
```

Read `REVISION.md`, `docs/architecture/MISSION-HEART-AND-EPOCH-REVIEW.md`,
`docs/decisions/DEC-0048-P0-PROPOSE-VALUE-REFINEMENT-SQUARE.md`, and
`docs/office/HANDOFF.md`. The machine-readable order is
`spec/office/read-order.tsv`.

## Claim ceiling

Rev0800 provides bounded hosted C++ value correspondence and formal source. It is
not a checked current Isabelle theorem, universal C++20/source/compiler refinement,
object-layout/ABI theorem, trusted clock, persistent or concurrent authority service,
safe identifier-reuse scheme, platform isolation result, product, or release.
