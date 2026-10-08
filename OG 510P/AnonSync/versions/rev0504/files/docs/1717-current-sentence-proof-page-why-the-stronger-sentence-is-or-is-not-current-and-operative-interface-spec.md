# Current-sentence proof page — why the stronger sentence is or is not current and operative

## Purpose

This page is the durable proof artifact for any claim that a stronger sentence is current, partially current, not yet current, rolled back, or superseded.
It exists so the product can later prove not only that promotion was allowed, but why currentness did or did not actually take hold across the required consumer scope.

## Mandatory proof fields

### 1. Source linkage

- case identifier
- source promotion receipt identifier
- source publication and authority receipts still relevant
- rule version governing current-sentence commitment
- commit lane version, if separate

### 2. Currentness status

- strongest promotion-authorized sentence
- strongest sentence actually current
- currentness rung
- whether currentness is preview, staged, core-only, all-required, rollback-armed, rolled back, or superseded
- lower sentence that remains current for any residual cohort

### 3. Consumer evidence

- required consumer families
- verified current consumer families
- lagging or stale consumer families
- evidence basis for each family
- whether any family is intentionally excluded from reliance on the stronger sentence
- whether UI, API, receipt, and subscriber state matched or diverged

### 4. Commit and rollback basis

- commit actor or automation policy
- trusted commit time
- rollout strategy used
- rollback authority
- rollback triggers known at issuance time
- whether rollback is global or cohort-scoped

### 5. Blocked stronger claims

- why all-required-consumer current was blocked, if applicable
- why an even stronger downstream sentence remains blocked
- whether contradiction across surfaces froze stronger claims
- what next event would strengthen currentness
- what next event would weaken or roll it back

## Required proof statements

The page must be able to state sentences like these:

- `the stronger sentence was promotion-authorized but not yet committed because required subscriber readiness was missing`
- `the stronger sentence is currently live only for the adjudicator and automation cohort; external consumers remain on the lower sentence pending reconciliation`
- `the stronger sentence is current for all required consumers under commit rule C4 after UI, API, receipt, and subscriber reconciliation passed`
- `the stronger sentence was rolled back for public consumers after contradictory state appeared in one downstream consumer family, while core internal consumers preserved the lower sentence`
- `the stronger sentence was superseded by a newer sentence without rewriting the earlier current interval`

## Proof ceiling

This page may prove `why this sentence is or is not currently operative for a given consumer scope`.
It may not on its own prove that every future consumer, mirror, or archive has converged unless the currentness rule for that scope separately agrees.

## Preservation rules

The proof must preserve:

- the strongest sentence merely authorized
- the strongest sentence actually current
- the consumer families included and excluded
- disagreements that limited stronger claims
- rollback exposure and fallback sentence
- the next strengthening and weakening triggers

## Drift rule

If later evidence shows the sentence was treated as current on a mistaken basis, this page must downgrade into explicit stale-current, rollback, or invalid-current proof rather than silently disappearing.

