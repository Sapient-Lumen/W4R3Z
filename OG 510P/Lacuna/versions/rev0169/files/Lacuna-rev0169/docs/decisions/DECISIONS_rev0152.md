# Decisions — rev0152

## D-0152-01 — keep several weighted worlds rather than selecting one hidden reality

**Decision:** expose a complete planner-only particle bank over all live and selected worlds.

**Why:** delayed commitment is useful only while alternatives remain explicit. A single “winning state card” recreates premature collapse and hides uncertainty behind fluent prose.

## D-0152-02 — treat weights as authored planning quantities

**Decision:** normalize and update weights mathematically while carrying explicit nonclaims about calibration and truth.

**Why:** Lacuna has no generative likelihood model capable of justifying objective posterior probabilities. Useful arithmetic does not require false statistical authority.

## D-0152-03 — separate reweighting from resampling, pruning, and selection

**Decision:** `update_particle_bank` may change weights only.

**Why:** reweighting is reversible planning attention; resampling changes population and ancestry; pruning removes a current option; selection changes planning status. Combining them would hide qualitatively different decisions inside one operation.

## D-0152-04 — require complete-population assessment

**Decision:** every live or selected world must appear exactly once in an update.

**Why:** partial normalization creates a misleading denominator and lets omitted alternatives disappear without an explicit decision.

## D-0152-05 — bind updates to a deterministic bank digest

**Decision:** a review supplies `expected_bank_sha256`, covering membership, status, raw weights, valuation fingerprints, and custody fingerprints.

**Why:** likelihoods assessed against one population must not be applied after a world, assignment, commitment, status, or weight changes.

## D-0152-06 — distinguish valuation equivalence from custody equivalence

**Decision:** emit separate `valuation_sha256` and `custody_sha256` fingerprints.

**Why:** two worlds can assert the same explicit propositions while differing in provenance, commitment, or lineage. Conversely, equal fingerprints do not prove complete-world identity because unrepresented state may differ.

## D-0152-07 — surface divergent treatment of equivalent valuations

**Decision:** permit but diagnose different likelihoods for the same valuation fingerprint.

**Why:** the assessor may rely on legitimate unrepresented distinctions or may be smuggling unstated state into the update. The kernel should expose the seam rather than infer which case applies.

## D-0152-08 — apply each evidence assertion at most once

**Decision:** enforce one particle update per `evidence_assertion_id` at review, mutation, and projection layers; duplicate attempts in one change-set must roll back atomically.

**Why:** multiplying the same evidence factor repeatedly exaggerates influence. Until Lacuna has a full factor ledger and recomputation protocol, single use is the safest honest rule.

## D-0152-09 — represent superseded evidence as reweighting debt

**Decision:** do not rewrite historical updates when their evidence assertion is superseded; expose the debt in the current bank and update receipt.

**Why:** silent retraction would rewrite past planning custody, while silently calling the resulting weights current would hide invalidated support. Debt makes both facts visible.

## D-0152-10 — allow unscoped director updates but forbid world-scoped normalization

**Decision:** only an unscoped privileged planner turn may mutate the global bank.

**Why:** a world-filtered context is not a complete denominator. Granting global reweight authority from a local view would manufacture false certainty.

## D-0152-11 — keep particle state out of audience projections

**Decision:** omit bank membership, weights, update rationales, fingerprints, factor history, and debt from perspective context.

**Why:** even counts and diagnostic IDs can leak hidden-world topology. Audience and planner views must remain structurally separate.

## D-0152-12 — retain fair-play schema 6 as the canonical parent lineage

**Decision:** treat the delivered rev0151 fair-play artifact as parent and port the sibling particle prototype forward.

**Why:** two sibling branches independently claimed schema 6. Pretending both were one physical lineage would falsify migration custody.

## D-0152-13 — advance the combined database to schema 7

**Decision:** preserve the official 5→6 fair-play digest and create a new digest-identified 6→7 particle migration.

**Why:** a new version is the only unambiguous way to reconcile the collision while retaining auditable parentage.

## D-0152-14 — refuse nonempty dormant particle rows during migration

**Decision:** migration may replace only absent or empty schema-6 particle tables.

**Why:** those rows have no official event owner in the canonical parent. Deleting them loses forensic state; adopting them invents provenance. Refusal forces an explicit operator decision.

## D-0152-15 — extract particle arithmetic from the storage monolith

**Decision:** place fingerprinting, bank construction, statistics, hashing, and likelihood updates in `particles.py` while retaining transaction orchestration in `store.py`.

**Why:** pure deterministic computation is easier to audit and test separately. The remaining large store module is acknowledged debt, not an invitation to perform a risky wholesale rewrite.

## D-0152-16 — do not implement a maximum-weight winner

**Decision:** stop at governed reweighting.

**Why:** selecting the argmax would turn a planning heuristic into a hidden canon transition and invite particle impoverishment. Proposal, resampling, diversity floors, and selection need explicit future protocols.
