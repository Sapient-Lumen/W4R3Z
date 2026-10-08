# Decisions — rev0153

## D-0153-01 — preserve old updates and repair current support with a new event

**Decision:** never mutate or delete `particle.updated` when its evidence ends; append `particle.reconciled` to record the later factor selection and derived weights.

**Why:** a past planning action and its current justification are different facts. Event history must retain both.

## D-0153-02 — replay from an immutable epoch baseline

**Decision:** use the first particle update's recorded prior bank after the latest structural boundary as the reconciliation baseline.

**Why:** it is complete, event-owned, and exactly the distribution from which the current factor chain began. Dividing current weights cannot recover zeros or exact custody.

## D-0153-03 — define conservative structural factor epochs

**Decision:** world creation, assignment, revision, commitment raise, manual weight change, and status change start a new epoch.

**Why:** those events can alter membership, valuation, custody, or authored prior. Old likelihoods are not presumed portable across them.

## D-0153-04 — select factors mechanically from assertion activity

**Decision:** include current-epoch factors whose evidence assertion is active; exclude those whose assertion ended before reconciliation.

**Why:** the kernel can audit recorded assertion state. It cannot safely infer from prose whether a factor should semantically survive.

## D-0153-05 — retain excluded factors as first-class custody

**Decision:** store included and excluded factor rows in every reconciliation.

**Why:** exclusion is part of the explanation for the repaired distribution and must not erase why earlier planning differed.

## D-0153-06 — use log-space replay

**Decision:** sum positive log likelihoods and normalize with a max-shifted log-sum-exp calculation.

**Why:** full replay should repair factor authority and numerical underflow at the same time. Sequential products can lose positive mass irreversibly.

## D-0153-07 — represent extinction without non-standard JSON numbers

**Decision:** use null log-factor state plus `extinguished_by_update_id` for zero baseline mass or zero likelihood.

**Why:** `Infinity` and `NaN` are not portable canonical JSON and would make event hashing/runtime behavior ambiguous.

## D-0153-08 — bind authorization to the complete calculated review

**Decision:** hash cube identity, ledger head, boundary, baseline, current bank, full factor disposition, blockers, and complete result.

**Why:** a digest that covered only factor IDs would not prove which population or arithmetic the author reviewed.

## D-0153-09 — allow one meaningful no-op, refuse repeated identical repair

**Decision:** a first reconciliation may record that log-space replay equals the current bank; subsequent identical factor-set/posterior repairs are blocked.

**Why:** an audit receipt can be useful without a weight change, but repeated no-op events add no custody value.

## D-0153-10 — keep reconciliation complete-population and planner-only

**Decision:** expose review/history only to unscoped planner/host surfaces and refuse the operation from world-scoped director turns.

**Why:** factor replay is defined over one complete denominator. Local normalization would manufacture a false global surface and leak hidden alternatives.

## D-0153-11 — separate reconciliation from assertion supersession

**Decision:** ending evidence does not automatically mutate weights.

**Why:** epistemic assertion custody and global hidden-world planning authority are separate acts. The explicit debt/review boundary keeps side effects visible.

## D-0153-12 — keep reconciliation separate from prior authoring

**Decision:** `reconcile_particle_bank` cannot supply new base weights or change likelihoods.

**Why:** repair should be deterministic from recorded custody. A new prior or corrected factor is a new modeling decision requiring a different protocol.

## D-0153-13 — do not carry factors across structural epochs automatically

**Decision:** factors before the latest boundary are labelled `epoch-retired`, even when a human might judge them still relevant.

**Why:** explicit reassessment is safer than unrecorded semantic portability.

## D-0153-14 — advance database schema to 8 without changing event schema

**Decision:** add reconciliation projections through a deterministic 7→8 migration while retaining event envelope schema 1.

**Why:** the immutable envelope remains compatible; only SQLite physical projection shape changes.

## D-0153-15 — gate schema-6 forensic refusal by source version

**Decision:** nonempty dormant-particle-row preflight applies only to schema 6, not schema 7.

**Why:** schema-7 particle rows are event-owned canonical projections and must migrate intact.

## D-0153-16 — share pure particle constructions

**Decision:** historical and live banks use `build_particle_bank_from_records`; valuation-divergence grouping has one shared function; reconciliation math remains pure.

**Why:** digest and audit algorithms must not drift between mutation, query, and verification surfaces.

## D-0153-17 — verify reconciliation by independent replay

**Decision:** `verify` reconstructs historical factor activity and arithmetic rather than trusting event summary values or projection rows.

**Why:** event/projection parity alone would faithfully reproduce tampered or internally inconsistent calculations.

## D-0153-18 — stop before factor dependence and replacement

**Decision:** rev0153 implements inclusion/exclusion replay only.

**Why:** correlated evidence, corrected likelihood vectors, factor families, and portability need explicit typed lineage. Hiding them inside reconciliation would overstate what the kernel knows.
