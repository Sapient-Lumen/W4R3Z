# Audit — rev0153

## Scope

This audit examined the rev0152 particle update path, superseded-evidence debt, migration lineage, planner/audience entrances, deterministic replay, numerical behavior, and duplicated particle logic. The goal was not to add a generic belief-revision engine. It was to find the smallest auditable mechanism that can repair current weights without rewriting historical decisions.

## Method

The review traced:

- `particle.updated` event creation through projection and verification;
- evidence assertion supersession after factor application;
- bank construction and fingerprinting paths;
- context and turn authorization surfaces;
- schema-6→7 lineage repair and schema-7 migration behavior;
- floating-point update behavior under tiny likelihood chains;
- projection rebuild order; and
- change-set and turn-schema operation parity.

Research comparison covered reason maintenance, event sourcing, sequential Monte Carlo, and stable log normalization. See [`../research/RESEARCH_rev0153.md`](../research/RESEARCH_rev0153.md).

## Findings and repairs

### A-0153-01 — reweighting debt had no governed repair

**Severity:** high epistemic integrity

**Before:** when an applied evidence assertion ended, Lacuna correctly exposed debt but left the current distribution permanently carrying that factor unless a human manually reset weights.

**Risk:** a normalized vector could remain numerically tidy while its support ledger was known to be invalid. Manual weight changes would erase the relationship between repair, baseline, and surviving factors.

**Repair:** add review-first `reconcile_particle_bank`, immutable `particle.reconciled` custody, complete factor dispositions, and deterministic weight projection.

**Evidence:** withdrawn-factor repair test restores the baseline, preserves the original update, marks the factor `reconciled-excluded`, and verifies/rebuilds cleanly.

### A-0153-02 — inverse-factor repair would be non-replayable

**Severity:** high arithmetic/custody

**Before during design:** the simplest apparent repair was to divide current weights by the withdrawn likelihood.

**Risk:** zero likelihood has no inverse; underflowed mass cannot be recovered; repeated floating-point division compounds error; and the result depends on mutation order rather than an immutable base.

**Repair:** reconstruct the first update's prior bank and replay the complete authorized factor set from that baseline.

**Evidence:** active-later-factor test excludes an earlier withdrawn factor while preserving and replaying the later factor exactly.

### A-0153-03 — factors could be replayed across a changed hidden-world surface

**Severity:** critical semantic integrity

**Before during design:** a campaign-wide factor list would include likelihoods assessed before worlds, assignments, commitments, statuses, or authored priors changed.

**Risk:** old likelihoods would silently answer a different question against a new population or custody surface.

**Repair:** introduce conservative structural factor epochs. World creation, assignment, revision, commitment raise, manual weight change, and status change retire earlier factors from current replay responsibility.

**Evidence:** structural-boundary test shows a superseded old factor becomes `epoch-retired`, creates no current debt, and cannot authorize reconciliation in the new empty epoch.

### A-0153-04 — sequential products could irreversibly underflow

**Severity:** high numerical integrity

**Before:** each update normalized after multiplication, but sufficiently tiny current mass multiplied by a tiny positive likelihood could become exactly zero. Later multiplication cannot recover zero.

**Risk:** a live hypothesis could be extinguished by representation limits rather than authored zero likelihood.

**Repair:** factor reconciliation accumulates positive likelihoods in log space and uses max-shifted log-sum-exp normalization.

**Evidence:** a 140-factor regression recovers positive posterior mass near `1e-140` after the simulated sequential surface has already underflowed that member to zero.

### A-0153-05 — non-finite log state could leak into canonical JSON

**Severity:** high replay portability

**Before during implementation:** representing extinguished members with `-Infinity` would be mathematically convenient but not valid portable JSON and could produce runtime-dependent serialization.

**Risk:** event digests and projection replay would depend on non-standard numeric encodings.

**Repair:** store `null` log-factor sums for extinguished members and a typed `extinguished_by_update_id`; reject non-finite numeric projection/event fields.

**Evidence:** verifier checks reconciliation scalar and member finiteness; pure calculation emits no `NaN` or infinity.

### A-0153-06 — a reconciliation review could become stale invisibly

**Severity:** high concurrency/authorization

**Before during design:** a factor selection and replay result could be calculated, followed by an unrelated committed event, then applied under a different ledger head.

**Risk:** the custody receipt would falsely imply review of the actual committed state.

**Repair:** bind the complete review core to cube identity and base head. Any separately committed intervening event invalidates the digest.

**Evidence:** stale-review test refuses without appending an event; fresh review succeeds.

### A-0153-07 — repeated no-op repairs could spam custody

**Severity:** medium ledger quality

**Before during design:** the same factor set and already-current posterior could be reconciled repeatedly under new IDs.

**Risk:** event history would accumulate meaningless repair claims and make actual factor changes harder to inspect.

**Repair:** compute a factor-set digest and refuse a reconciliation when an earlier receipt for that set already produced both the current and calculated posterior bank.

**Evidence:** repeat-reconciliation test returns `particle-factor-ledger-already-reconciled` and preserves event count.

### A-0153-08 — global repair authority could leak into local model context

**Severity:** critical confidentiality/noninterference

**Before during feature addition:** adding the review to generic planner context risked exposing global world membership and factor history to world-scoped or audience contexts.

**Risk:** a model could infer hidden alternatives or normalize a local subset as though it were the full denominator.

**Repair:** expose review and history only in unscoped planner context; omit them structurally from audience and world-scoped packets; refuse `reconcile_particle_bank` in world-scoped director turns.

**Evidence:** context/turn test checks JSON omission, rendered Markdown non-disclosure, unscoped success, and scoped refusal.

### A-0153-09 — reconciliation projection lacked independent forensic verification

**Severity:** critical replay custody

**Before during implementation:** simply trusting the stored posterior would make `rebuild-projections` repeat a corrupted calculation rather than detect it.

**Risk:** tampered members, factor dispositions, boundaries, or statistics could appear valid.

**Repair:** `verify` independently reconstructs event-time boundary, evidence activity, factor order, baseline/current/posterior banks, log-space arithmetic, statistics, factor-set digest, review digest, and per-world members.

**Evidence:** direct member tamper fails verification; projection rebuild restores the event-derived value and passes.

### A-0153-10 — schema-7 migration could inherit the schema-6 dormant-row refusal incorrectly

**Severity:** critical migration safety

**Before during audit:** the unowned-particle-row preflight originated to protect schema 6. Applied without a source-version guard, it would reject legitimate event-owned schema-7 particle rows during 7→8 migration.

**Risk:** every real rev0152 campaign with particle history could become unmigratable.

**Repair:** run dormant-row refusal only when the source is schema 6. Schema 7 preserves event-owned particle projections and adds reconciliation tables.

**Evidence:** schema-seven migration test preserves ledger head and existing particle update, creates schema-8 tables, and verifies cleanly.

### A-0153-11 — particle-bank construction existed in parallel forms

**Severity:** medium maintainability

**Before:** live worlds and historical update receipts required nearly identical fingerprinted-bank normalization, inviting drift between current and reconstructed baselines.

**Risk:** a reconciliation could compare digests produced by subtly different algorithms.

**Repair:** extract `build_particle_bank_from_records` and make both live-bank and historical-baseline paths use it.

**Evidence:** all original particle tests plus reconciliation digest/replay tests pass through the shared constructor.

### A-0153-12 — valuation-divergence logic was duplicated

**Severity:** medium auditability

**Before:** presentation and verifier paths independently grouped valuation-equivalent worlds with different likelihoods.

**Risk:** diagnostics could disagree or one path could be fixed without the other.

**Repair:** extract `valuation_likelihood_divergence_groups` into the pure particle module and reuse it.

**Evidence:** original divergence tests and full verifier suite pass after extraction.

### A-0153-13 — executable entrance was not covered end to end

**Severity:** medium integration reliability

**Before during implementation:** Python tests covered reconciliation, but command parsing, campaign resolution, JSON emission, and CLI operation assembly could still drift.

**Risk:** the feature would work only as a library while the intended human/ChatGPT subprocess entrance failed.

**Repair:** add a campaign-level CLI test that creates evidence/worlds, applies a factor, supersedes evidence, reviews, reconciles, inspects custody, and verifies.

**Evidence:** the executable round trip passes under the bundled `python -S` launcher.

### A-0153-14 — human Markdown omitted the repair frontier

**Severity:** medium usability

**Before during implementation:** JSON planner context contained the review but Markdown context displayed only bank and updates.

**Risk:** human directors using the readable entrance would see debt without the authorized repair or blockers.

**Repair:** render reconciliation readiness, factor counts, digest, blockers or projected ESS/total variation, recent custody, and explicit nonclaim.

**Evidence:** rendering test asserts the planner sees a ready repair and factor ID while the audience rendering does not disclose it.

## Residual risks

### A-0153-R1 — correlated evidence can still be multiplied

Single-use assertion IDs prevent exact duplicate factors, not two assertions derived from one observation. Lacuna needs factor-family or dependence custody before weights deserve stronger probabilistic language.

### A-0153-R2 — likelihood vectors cannot yet be corrected in place

A factor may be included or excluded, but a mistaken likelihood assessment has no governed predecessor/successor replacement protocol.

### A-0153-R3 — structural epochs are intentionally coarse

Some old factors might remain semantically portable after a commitment or harmless assignment change. Rev0153 refuses to infer portability. Reassessment is required.

### A-0153-R4 — zero likelihood remains an authored extinction decision

Log-space replay recovers positive mass lost to underflow, not mass intentionally assigned likelihood zero. There is no diversity floor or separate extinction authorization.

### A-0153-R5 — doubles are not an exact wire arithmetic standard

The implementation is deterministic in the supported runtime and checks close numeric equality. It does not promise bit-identical results across arbitrary languages or hardware.

### A-0153-R6 — the storage module remains large

`store.py` still combines migration, domain mutation, replay, verification, explanation, and query surfaces. Pure particle calculations have been extracted, but further cuts should remain bounded and parity-tested.

### A-0153-R7 — no world proposal or resampling exists

Repair can expose a concentrated or implausible bank but cannot create a missing explanation, preserve semantic minorities, or record ancestry.

### A-0153-R8 — current support is not causal agency

A player-influenced factor can change weights without proving that outcomes would differ under a nearby counterfactual. Reconciliation does not close that conceptual gap.

## Acceptance result

The rev0153 acceptance run covers factor withdrawal, active-factor replay, log-space recovery, stale and repeated refusal, epoch boundaries, tamper/rebuild, context noninterference, direct turns, schema-7 migration, rendered human context, and executable CLI lifecycle in addition to all retained rev0152 behavior.
