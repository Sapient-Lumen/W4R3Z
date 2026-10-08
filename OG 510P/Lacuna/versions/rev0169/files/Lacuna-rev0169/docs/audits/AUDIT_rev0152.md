# Audit — rev0152

## Scope

This audit examined the canonical rev0151 fair-play artifact, the sibling rev0151 particle prototype, database migration custody, particle arithmetic, event/projection replay, turn authority, context noninterference, schemas, CLI entrances, and historical tests.

## A-0152-01 — world weights had no evidence custody

**Severity:** high epistemic integrity

**Before:** `set_world_weight` could author a number and rationale, but no operation represented a complete evidence update over all surviving alternatives.

**Risk:** hosts could present ad hoc preferences as if they were posterior reasoning, omit inconvenient worlds, or lose the relationship between evidence and changed planning attention.

**Repair:** add review-first `update_particle_bank`, exact population coverage, bank digest binding, immutable `particle.updated` events, per-world arithmetic custody, CLI/Python/turn entrances, and deterministic rebuild.

**Evidence:** particle-bank unit tests, CLI end-to-end update round trip, schema parity tests, projection tamper/rebuild test.

## A-0152-02 — one hidden world could still become the de facto state card

**Severity:** high architectural

**Before:** candidate worlds existed, but there was no first-class normalized view or diversity diagnostic.

**Risk:** downstream planners would likely select one world early and recreate the premature commitment problem Lacuna was designed to avoid.

**Repair:** expose the complete bank, normalized weights, valuation groups, effective sample size, entropy, and explicit nonclaims without adding a winner operation.

**Evidence:** bank normalization and duplicate-valuation tests; planner context rendering.

## A-0152-03 — partial evidence updates could create a false denominator

**Severity:** high correctness

**Before in the sibling prototype design space:** a loose adapter could have assessed only favored worlds.

**Risk:** omitted worlds would lose mass without an explicit prune or assessment.

**Repair:** require every live or selected world exactly once and reject missing, extra, duplicate, empty, stale, or oversized vectors atomically.

**Evidence:** incomplete/stale/zero-posterior tests and turn scope tests.

## A-0152-04 — bank reviews needed semantic staleness, not only ledger-head staleness

**Severity:** high concurrency

**Before:** using only the current event head would either over-stale harmless narration sources or under-specify which hidden state was assessed.

**Risk:** a review could be misapplied after a relevant world mutation, or a same-turn narration source could make a valid update unusable.

**Repair:** bind to `bank_sha256` over complete population state. Turn preparation may rebind the request head after a narration source while preserving the independently computed bank digest. Any relevant in-transaction mutation changes the digest and refuses.

**Evidence:** stale bank and unscoped director turn tests.

## A-0152-05 — valuation sameness was being confused with record sameness

**Severity:** medium interpretability

**Before:** one fingerprint would either hide provenance differences or overstate semantic difference.

**Risk:** diversity metrics could count duplicate explanations as distinct, or merge worlds whose custody mattered.

**Repair:** split valuation and custody fingerprints and report equivalent-valuation groups without claiming complete-world identity.

**Evidence:** duplicate valuation test and divergent-likelihood diagnostic test.

## A-0152-06 — repeated use of one evidence assertion double-counted a factor

**Severity:** high quantitative integrity

**Before during audit:** the sibling implementation permitted the same `evidence_assertion_id` to authorize repeated multiplicative updates.

**Risk:** an operator or model could amplify one observation indefinitely while every individual update remained arithmetically valid.

**Repair:** centralize active-unused evidence validation so both the review entrance and mutation path refuse reuse; add a unique evidence-factor index as a final projection barrier. Corrections require a new or superseding assertion. A duplicate factor inside one atomic change-set rolls back the first attempted multiplication.

**Evidence:** review-reuse refusal, committed-reuse refusal, same-change atomic rollback regression, and schema-shape check.

## A-0152-07 — superseded evidence left an invisible posterior liability

**Severity:** high epistemic honesty

**Before during audit:** after evidence used for reweighting was superseded, current weights remained but no surface identified the invalidated factor.

**Risk:** a normalized vector could be mistaken for a clean current posterior.

**Repair:** expose applied factor status and `reweighting_debt` in the planner bank, status, rendering, and update receipts. Do not rewrite history automatically.

**Evidence:** supersession-debt regression test; planner context inspection.

## A-0152-08 — particle projection arithmetic needed defensive verification

**Severity:** high audit robustness

**Before:** malformed numeric storage such as NaN could crash audit computations or propagate silently.

**Risk:** corrupted projections could turn verification itself into a denial of service.

**Repair:** parse finite numbers defensively, report structured surface-specific errors, recompute every scalar and member equation, and rebuild from immutable events.

**Evidence:** nonfinite projection tamper test and arithmetic verification suite.

## A-0152-09 — global bank authority leaked through world-scoped planning

**Severity:** high access integrity

**Before in the broad director model:** a privileged but world-scoped packet might appear entitled to any planner operation.

**Risk:** a model seeing one branch could normalize or mutate the full population it was not shown.

**Repair:** omit the bank and updates from world-scoped planner context and refuse `update_particle_bank` under a world-scoped grant.

**Evidence:** context firewall and world-scoped director refusal tests.

## A-0152-10 — two rev0151 branches independently claimed schema 6

**Severity:** critical migration custody

**Before:** the fair-play branch and particle sibling both defined incompatible 5→6 migrations and physical shapes.

**Risk:** a version number no longer identified one deterministic migration history; adopting either definition silently could falsify lineage.

**Repair:** keep the delivered fair-play artifact as canonical parent, preserve its 5→6 digest, and advance the unified runtime to schema 7 with a new 6→7 digest.

**Evidence:** schema-lineage documentation, migration receipts, and schema-6 variant tests.

## A-0152-11 — official schema-6 fresh and migrated cubes had different particle shapes

**Severity:** high migration reliability

**Before:** fresh rev0151 cubes contained empty dormant particle tables, while the official 5→6 migration created only fair-play tables. Runtime shape expectations could therefore reject a legitimately migrated cube.

**Risk:** two official paths to “schema 6” were not physically equivalent.

**Repair:** make 6→7 accept either absence or empty dormant tables and produce one exact canonical schema-7 shape.

**Evidence:** tests for fresh dormant schema 6 and migrated schema 6 without particle tables.

## A-0152-12 — replacing dormant tables could silently destroy private rows

**Severity:** critical data custody

**Before during migration design:** a straightforward drop/recreate step would erase any rows written by a private extension.

**Risk:** forensic information would disappear while migration reported success.

**Repair:** preflight counts and refuse nonempty particle tables with `unowned-particle-projection-rows`. The operator must export or explicitly rebuild them first.

**Evidence:** migration refusal test verifies row, version, and ledger head remain unchanged.

## A-0152-13 — particle arithmetic was embedded in the storage monolith

**Severity:** medium maintainability

**Before:** implementing the feature entirely in `store.py` would further entangle pure math, transaction policy, querying, and verification.

**Risk:** changes to statistics or fingerprints would be harder to test and easier to couple accidentally to SQLite state.

**Repair:** extract deterministic fingerprint, bank, distribution, digest, and likelihood functions into `src/lacuna/particles.py`.

**Evidence:** module boundary and pure-function coverage through particle tests.

## A-0152-14 — the storage layer remains too large

**Severity:** medium maintainability; unresolved

**Current:** `store.py` still owns migration, validation, event append, projection replay, verification, query construction, explanations, and multiple domain protocols.

**Risk:** review burden and accidental cross-domain coupling continue to grow.

**Disposition:** perform bounded extractions only when protected by parity tests. Candidate next cuts are migration/shape custody and particle projection verification. A wholesale rewrite is explicitly rejected.

## A-0152-15 — zero likelihood can behave like hidden pruning

**Severity:** medium epistemic policy; unresolved

**Current:** an authored likelihood of zero sets a world's posterior weight to zero without changing its `live` status.

**Risk:** the operation remains formally “reweight only” while making a hypothesis unable to recover under later multiplicative updates unless a human resets its weight.

**Disposition:** retain current mathematical behavior but document it. A future policy should decide between strict-positive likelihoods, an explicit extinction authorization, or log-weight/floor semantics.

## A-0152-16 — weights are not reconstructible from an editable factor ledger

**Severity:** high future capability; unresolved

**Current:** updates preserve historical factors, but supersession creates debt rather than automatic recomputation.

**Risk:** long campaigns cannot retract, revise, or reorder evidence cleanly.

**Disposition:** design a separate factor-ledger recomputation receipt before adding evidence retraction. It must bind a chosen base distribution, ordered active factor set, complete world population, and resulting digest.

## Residual risks

Rev0152 intentionally does not solve:

- calibrated likelihood estimation;
- dependence or correlation between evidence assertions;
- underflow in very long floating-point update chains;
- world proposal, ancestry, resampling, merge, or diversity floors;
- automatic recovery from zero-weight live worlds;
- causal agency or counterfactual validity;
- semantic completeness of world fingerprints;
- prose-to-evidence extraction;
- hostile-host forking, signatures, or trusted time; or
- narrative quality, mystery fairness, characterization, or thematic value.

These are named limits, not implied features.
