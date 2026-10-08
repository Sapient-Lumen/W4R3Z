# Supersession review page — cohort adoption, waiver carry-forward, and orphan risk

## Purpose

This page is the operator's comparison workspace for answering:

> if we promote this successor or retire this predecessor, who auto-adopts, who stays pinned, who needs a waiver decision, who becomes grandfathered, and who would be orphaned?

## Core decision

Every serious policy supersession must render one **Supersession review** before the product allows promotion or retirement.
The page exists to prevent `everyone moves` folklore.

## Fixed page order

1. cohort summary strip
2. adoption bucket matrix
3. waiver carry-forward review
4. field/world mismatch review
5. retirement risk review
6. operator decision ledger

### 1) Cohort summary strip

Show:

- predecessor id
- successor id
- relation class
- total candidate subjects
- clean auto-adopt count
- grandfathered count
- blocked count
- orphan-risk count
- unknown count

### 2) Adoption bucket matrix

Bucket every subject into exactly one current outcome:

- `auto-adopts`
- `needs-confirmation`
- `keeps-pin`
- `requires-branch`
- `blocked-by-waiver`
- `out-of-scope`
- `grandfathered`
- `orphan-risk`
- `unknown`

For each bucket show:

- subject count
- worlds represented
- field families involved
- strongest safe summary sentence

## Hard rule

`same values today` may never place a subject into `auto-adopts` by itself.
Future-governance posture is required.

### 3) Waiver carry-forward review

For every active waiver cluster, show:

- predecessor waiver id(s)
- carry-forward verdict
- successor fields affected
- rereview deadline
- whether the waiver blocks promotion, blocks retirement, or merely downgrades the subject

## Hard rule

The page may not collapse `resolved by successor` and `still tolerated on successor` into one green outcome.

### 4) Field/world mismatch review

Surface mismatches that change successor truth:

- subjects in unsupported worlds
- subjects losing coverage under successor
- subjects newly covered by successor
- fields removed from scope
- fields added to scope
- world-specific successors and exclusions

## Hard rule

Any mismatch that changes subject posture must remain visible even if the current displayed values still match.

### 5) Retirement risk review

Show the costs of retiring the predecessor now:

- subjects still relying on predecessor-only fields
- subjects whose waivers have no successor verdict
- subjects with no valid successor destination
- audit/receipt debt
- rollback readiness

Render one retirement posture:

- `safe-now`
- `safe-after-listed-actions`
- `promotion-only-no-retirement`
- `retirement-blocked`
- `unknown`

### 6) Operator decision ledger

For each bucket, allow only explicit decisions:

- `promote with auto-adopt`
- `promote and grandfather`
- `promote but keep pinned`
- `split branch`
- `carry waiver forward`
- `re-prove waiver`
- `defer retirement`
- `retire predecessor`
- `rollback`

The ledger must preserve subject counts for every choice.

## Copy rules

- Never say `migrate all` if any subject is grandfathered, blocked, or out of scope.
- Never say `waivers carried` unless the page names which ones and how.
- Never say `old policy can go away` while orphan-risk subjects remain.
- Never say `same profile family` when the relation class is split or merge.
- Never say `no impact` when the only truth is `no value delta for already-matching subjects`.

## Example strongest-safe sentence patterns

- `Most covered desktop subjects auto-adopt the successor, but the predecessor cannot retire yet because service-world waivers still lack carry-forward verdicts.`
- `The successor is narrower than the predecessor: some mobile-local subjects remain explicitly out of scope and will be grandfathered until a world-specific branch is published.`
- `Retirement is blocked because 14 subjects would become orphaned and 3 waivers still depend on predecessor-only fields.`

