# Meta: Anchor Corpus Protocol (rev0434)

## Purpose
Use this protocol when the repo needs a thin shared answer to:
> once a pilot names a proving-ground scenario, which concrete representative case profiles should it bind to so comparison stays honest and repeatable?

Read with:
- `design/portfolio-anchor-corpus-2026Q1.md`
- `design/portfolio-proving-grounds-2026Q1.md`
- `meta/PROVING_GROUNDS_PROTOCOL.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`

## Required assets
The first anchor-corpus lane should include:
- `proofgrounds/portfolio-anchor-corpus-v0/README.md`
- `proofgrounds/portfolio-anchor-corpus-v0/anchors.json`
- `tools/check_anchor_corpus.py`

## Required anchor fields
Every anchor in the first shared corpus must include:
- `anchor_id`
- `title`
- `anchor_class`
- `scenario_bindings`
- `representative_shape`
- `required_traits`
- `hold_constant`
- `allowed_variation`
- `minimum_artifacts`
- `primary_evidence_focus`
- `must_not_claim`
- `notes`

## Minimum corpus rules
The initial anchor corpus must:
1. include at least five anchors;
2. keep anchor IDs unique;
3. bind every anchor to one or more scenario IDs from `proofgrounds/portfolio-scenario-matrix-v0/scenarios.json`;
4. cover every current scenario ID at least once;
5. keep at least these anchor classes present:
   - `workspace_profile`
   - `release_boundary_profile`
   - `intake_policy_profile`
   - `native_edge_profile`
   - `docs_consumer_profile`

## Required non-claims
The corpus must **not** claim that:
- an anchor is a universal benchmark;
- one anchor proves default readiness;
- one anchor can silently rerank the strategic ladder;
- or the corpus replaces freshness renewal or seam-local validators.

## Checker duties
`tools/check_anchor_corpus.py` should stay thin.
It may check:
- file presence;
- JSON parseability;
- required fields;
- unique IDs;
- minimum anchor count;
- binding only to declared scenario IDs;
- and coverage of all current scenarios.

It must **not** claim to validate seam-local payload semantics, benchmark quality, or current external evidence.

## Revision rule
If a revision materially changes the shared anchor corpus, it should update in the same revision:
- `design/portfolio-anchor-corpus-2026Q1.md`
- `meta/ANCHOR_CORPUS_PROTOCOL.md`
- `proofgrounds/portfolio-anchor-corpus-v0/anchors.json`
- and `tools/check_anchor_corpus.py`

If no anchor changed, say so rather than silently leaving the corpus stale.
