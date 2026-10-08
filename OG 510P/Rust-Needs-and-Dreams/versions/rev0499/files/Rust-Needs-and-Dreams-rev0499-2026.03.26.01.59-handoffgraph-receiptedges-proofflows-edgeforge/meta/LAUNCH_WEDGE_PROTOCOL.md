# Launch wedge protocol (rev0496)

Use this protocol when a revision is mainly about **how a worthy contribution first becomes real for users** rather than about rank, live packet posture, residency, hot substrate drift, or broad claim-state.

## What this layer governs
The launch-wedge layer is for:
- first-adopter shape;
- trigger moments where the pain is sharp enough to justify trying the contribution;
- the initial artifact or surface that enters that moment;
- proving grounds that count as honest first proof; and
- anti-goals that prevent early wedge success from being mistaken for permission to sprawl.

It is not for:
- broad reranking;
- declaring a new active frontier;
- replacing packets, watchcards, or stewardship notes; or
- treating “interesting to imagine” as equivalent to “believable to enter”.

## Required revision outputs
A launch-wedge revision should normally leave behind:
1. a broad design note explaining why a wedge layer is needed now;
2. a machine-readable wedge ledger for the current strongest seams;
3. a structural checker for that ledger;
4. refreshed routing and continuity rails; and
5. any source-atlas updates needed to cover newly repeated anchors.

## Required wedge-card fields
Each wedge card in `ledgers/portfolio-launch-wedges-v0/wedges.json` should name at least:
- `wedge_id`
- `title`
- `seam`
- `wedge_kind`
- `status`
- `target_user`
- `decision_window`
- `trigger_moment`
- `initial_surface`
- `import_surfaces`
- `proof_artifacts`
- `proving_grounds`
- `success_signals`
- `anti_goals`
- `credible_home`
- `next_if_proven`
- `related_assets`
- `supporting_sources`
- `review_horizon`
- `notes`

## Status guidance
Use wedge status values conservatively:
- `active` — the wedge is currently the archive's preferred first-proof path for that seam;
- `candidate` — promising but not yet the archive's preferred first wedge;
- `hold` — strategically important seam, but the wedge should stay constrained or deferred;
- `retired` — previously meaningful wedge no longer recommended.

## Default operating rules
1. Keep **strategic rank** separate from **launch wedge**. A lower-ranked seam can still have a clearer first wedge than a higher-ranked one.
2. Keep **wedge proof** separate from **residency/officialization**. A wedge can be real while still staying companion-first.
3. Keep **imports** separate from **owned truth**. A wedge should say what upstream/service/machine-readable surfaces it relies on.
4. Require at least one **anti-goal** for every wedge card.
5. Prefer wedges that answer one painful decision within a working day.
6. Refuse wedges that only sound valuable after being widened into a platform, portal, or official program.

## Revision hygiene
If a revision materially changes the preferred wedge for a strong seam, refresh in the same revision:
- `design/epic-contribution-launch-wedges-2026Q1.md`
- `ledgers/portfolio-launch-wedges-v0/wedges.json`
- `tools/check_launch_wedges.py`
- `RESEARCH_LOG.md`
- `meta/LATEST_REVISION_FILESET.md`

Also refresh front-door routing when the next user question should be “what is the first believable wedge?” instead of “what ranks highest?”.
