# Meta: Hypothesis Ledger Protocol (rev0495)

## Purpose
Use this protocol when the repo needs a repeatable shared format for **named present-tense strategic claims, downgrade triggers, falsifiers, and affected control-loop layers**.
This protocol is **not** the same as watchcard renewal, packet review, stewardship mapping, pilot scoring, proving-ground coverage, or seam-local semantic validation.

It exists for the narrower question:
> what minimum structure should a shared hypothesis ledger require so the archive's strongest present-tense claims can be reviewed, narrowed, degraded, superseded, or retired visibly?

Read with:
- `design/portfolio-hypothesis-ledger-2026Q1.md`
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-portfolio-control-loop-2026Q1.md`
- `design/epic-contribution-hot-substrate-watchcards-2026Q1.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/PORTFOLIO_CONTROL_LOOP_PROTOCOL.md`

## Required top-level fields
Every shared ledger should include:
- `schema_family`
- `revision`
- `hypotheses`

## Required hypothesis-card fields
Every hypothesis card must include:
- `hypothesis_id`
- `title`
- `claim_class`
- `status`
- `statement`
- `supporting_sources`
- `related_seams`
- `related_assets`
- `affected_loops`
- `leading_indicators`
- `downgrade_triggers`
- `falsifiers`
- `review_horizon`
- `notes`

## Required class coverage
The shared portfolio ledger must cover at least these classes:
- `one_project_ranking`
- `multi_project_ranking`
- `frontier_posture`
- `anti_tacit_knowledge`
- `staging_claim`
- `portfolio_hygiene`
- `proof_discipline`

## Allowed status values
Every hypothesis card must use one of:
- `active`
- `narrowed`
- `degraded`
- `superseded`
- `retired`

## Allowed review horizons
Every hypothesis card must use one of:
- `hot`
- `warm`
- `cool`
- `cold`

## Allowed affected-loop values
Every hypothesis card must use one or more of:
- `watchcard`
- `packet`
- `stewardship`
- `canon`
- `hygiene`

## Minimum anti-cheating rules
- A hypothesis card must not omit downgrade triggers just because the claim feels culturally entrenched.
- A hypothesis card must not omit falsifiers just because the claim is strategically attractive.
- A hypothesis card must not point to missing canon assets.
- A hypothesis card may be mechanically well-formed and still be strategically wrong.
- The checker may validate structure and coverage, but it does **not** settle the claim.
- A hot source change does **not** automatically narrow a hypothesis unless the card's own triggers are met.

## Hard failures
A shared hypothesis-ledger check must fail when:
- a required top-level field is missing;
- `hypotheses` is not a list;
- a required class is absent;
- a hypothesis ID is duplicated;
- a status value is outside the allowed set;
- a review horizon is outside the allowed set;
- an affected-loop value is outside the allowed set;
- a required list field is empty;
- a related canon asset does not exist; or
- the ledger has fewer than seven cards.

## Required non-claims
A passing ledger check must **not** claim that it:
- refreshed external citations automatically;
- reranked seams automatically;
- resolved a renewal queue item;
- downgraded a claim by itself; or
- proved any seam-local design correct.

## Minimum maintenance rule
If a revision materially changes one of the archive's strongest repeated claims, it should update all of the following in the same revision, or explain why not:
- `design/portfolio-hypothesis-ledger-2026Q1.md`
- `meta/HYPOTHESIS_LEDGER_PROTOCOL.md`
- `ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json`
- `tools/check_hypothesis_ledger.py`
- the nearest watchcard, packet, stewardship, canon, or hygiene targets named by the affected card
