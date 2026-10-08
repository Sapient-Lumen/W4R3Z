# Decision journey protocol (rev0497)

Use this protocol when a revision is mainly about **how several worthy seams should compose during one repeated decision moment** rather than about rank, wedge entry, residency, hot substrate drift, or broad claim-state.

## What this layer governs
The decision-journey layer is for:
- repeated operator or maintainer moments such as triage, admission review, issue handoff, release review, readiness evaluation, and conservative default selection;
- cross-seam artifact flow during those moments;
- the point where a journey ends in a real decision;
- and refusal clauses that keep a journey from being mistaken for a platform mandate.

It is not for:
- broad reranking;
- declaring a new frontier;
- replacing seam-local contracts or specimen packs; or
- claiming that every seam must always compose with every other seam.

## Required revision outputs
A decision-journey revision should normally leave behind:
1. a broad design note explaining why the journey layer is needed now;
2. a machine-readable journey ledger for the current core operator moments;
3. a structural checker for that ledger;
4. refreshed routing and continuity rails; and
5. any source-atlas updates needed to cover newly repeated anchors.

## Required journey-card fields
Each journey card in `ledgers/portfolio-decision-journeys-v0/journeys.json` should name at least:
- `journey_id`
- `title`
- `journey_class`
- `status`
- `primary_decision`
- `entry_seam`
- `supporting_seams`
- `trigger_moment`
- `entry_artifacts`
- `major_steps`
- `decision_outputs`
- `proof_of_completion`
- `anti_goals`
- `credible_home`
- `related_assets`
- `supporting_sources`
- `review_horizon`
- `notes`

## Status guidance
Use journey status values conservatively:
- `active` — currently the archive's preferred framing for a repeated decision moment;
- `candidate` — plausible but not yet preferred;
- `hold` — strategically relevant but should stay narrow or deferred;
- `retired` — previously meaningful journey no longer recommended.

## Default operating rules
1. Keep **wedge entry** separate from **journey composition**. A seam can have a strong wedge but still fit multiple later journeys.
2. Keep **seam-local contracts** separate from **journey use**. Journeys are about how artifacts travel, not about replacing seam-local specs.
3. Require at least one **primary decision** and one **proof-of-completion** per journey.
4. Require at least one **anti-goal** for every journey card.
5. Prefer journeys that fit one painful operator day or one bounded review cycle.
6. Refuse any journey framing that only becomes attractive after being widened into a platform, portal, or official super-suite.

## Revision hygiene
If a revision materially changes how the strongest seams compose in repeated operator moments, refresh in the same revision:
- `design/epic-contribution-decision-journeys-2026Q1.md`
- `ledgers/portfolio-decision-journeys-v0/journeys.json`
- `tools/check_decision_journeys.py`
- `RESEARCH_LOG.md`
- `meta/LATEST_REVISION_FILESET.md`

Also refresh front-door routing when the next user question should be “what real decision journey does this help?” instead of only “what seam or wedge is strongest?”.
