# Decisions — rev0149

## D-0149-01 — changing truth is revision, not assignment

**Decision:** refuse an occupied exact assignment slot. A truth-changing update must cite a current `revision-impact` digest and create a successor record.

**Why:** initial hypothesis adoption and later correction have different epistemic meaning. The predecessor must remain inspectable.

**Rejected:** silently end the old row inside `assign_world`; mutate the row in place; infer revision from prose.

## D-0149-02 — bind impact review to the complete current head

**Decision:** any intervening ledger event invalidates a revision digest.

**Why:** selective dependency hashing would require trusting that the dependency analysis is already complete. Head binding is simple, deterministic, and safe under concurrent planning.

**Cost:** unrelated changes can force a fresh review. This is acceptable for a high-impact operation.

## D-0149-03 — expose burden as policy, never as probability

**Decision:** calculate an ordinal score from named custody components and label it with a versioned policy identifier and nonclaim.

**Why:** reviewers need triage, but a numeric output can falsely imply empirical calibration. Component transparency allows later replacement without rewriting history.

## D-0149-04 — commitment moves upward one boundary at a time

**Decision:** permit only adjacent monotone raises. Supply no in-place lowering operation.

**Why:** each boundary is a review opportunity. Silent weakening would destroy the meaning of hard commitments.

**Alternative for change:** revise a nonhard assignment or fork the candidate world.

## D-0149-05 — hard commitment is a local stop sign

**Decision:** hard blocks revision inside that world; it does not globally canonize the claim.

**Why:** plural worlds must remain possible. A fair-play precommitment can be hard in one world while another world explores a different authored branch.

## D-0149-06 — explicit consequences are authored, not inferred

**Decision:** record directed consequence links only through explicit operations.

**Why:** chronology and shared subject matter are insufficient evidence of causality. Automatic linking would incentivize overfitted retcons.

## D-0149-07 — binding blocks; softer consequences become debt

**Decision:** any incident binding link blocks revision. Notice/material links contribute burden and remain active if an endpoint ends.

**Why:** automatically deleting loses history; automatically transferring invents a new dependency. Repair must be authored.

## D-0149-08 — assignment consequence graphs are acyclic

**Decision:** refuse active assignment-to-assignment cycles and bound impact traversal.

**Why:** revision analysis needs deterministic termination and a comprehensible dependency direction. Cyclic semantic explanations can still be represented in prose or a future richer model, but not in this blocking graph.

## D-0149-09 — perspective explanation is a projection, not redaction

**Decision:** check every returned link against perspective access and emit safe event envelopes.

**Why:** hiding a target record is insufficient if its ID leaks through a visible neighbor. Confidentiality must be closed under traversal.

## D-0149-10 — keep model hosting outside the cube

**Decision:** support humans, subprocess callers, and ChatGPT-like hosts through CLI, direct Python methods, and typed turn packets; do not add a vendor client.

**Why:** the cube should validate state transitions regardless of which model or human proposed them. Model invocation policy changes faster than epistemic custody.

## D-0149-11 — database schema 4, event schema 1

**Decision:** add projections and additive event types without rewriting historical event envelopes.

**Why:** physical query layout and immutable event contract evolve independently. Migration must preserve the ledger head.
