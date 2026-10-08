# Meta: Proving Grounds Protocol (rev0433)

## Purpose
Use this protocol when the repo needs a thin shared answer to:
> which representative Rust realities should serious pilots bind to so their claims become more comparable and less rhetorical?

Read with:
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`

## Required assets
The first proving-grounds lane should include:
- `proofgrounds/README.md`
- `proofgrounds/portfolio-scenario-matrix-v0/README.md`
- `proofgrounds/portfolio-scenario-matrix-v0/scenarios.json`
- `tools/check_proving_ground_matrix.py`

## Required scenario fields
Every scenario in the first shared matrix must include:
- `scenario_id`
- `title`
- `scenario_class`
- `primary_tax`
- `topology`
- `environment`
- `decision_classes`
- `relevant_seams`
- `minimum_artifacts`
- `must_prove`
- `must_not_claim`
- `skip_conditions`

## Minimum corpus rules
The initial matrix must:
1. include at least four scenarios;
2. keep scenario IDs unique;
3. cover at least these classes:
   - `inner_loop_workspace`
   - `public_release_boundary`
   - `locked_down_intake`
   - `native_edge_polyglot`
4. keep `cross_target_docs_drift` strongly preferred whenever consumer-routing or docs-derived claims are in scope;
5. make skip conditions explicit rather than silent.

## Required non-claims
The matrix must **not** claim that:
- one scenario proves default readiness;
- every seam must support every scenario;
- scenario coverage is the same as freshness renewal;
- or one passed scenario can silently re-rank the strategic ladder.

## Checker duties
`tools/check_proving_ground_matrix.py` should stay thin.
It may check:
- file presence;
- JSON parseability;
- required fields;
- unique IDs;
- minimum scenario count;
- and required class coverage.

It must **not** claim to validate seam-local artifact semantics or current external evidence.

## Revision rule
If a revision materially changes the shared proving-grounds matrix, it should update in the same revision:
- `design/portfolio-proving-grounds-2026Q1.md`
- `meta/PROVING_GROUNDS_PROTOCOL.md`
- `proofgrounds/portfolio-scenario-matrix-v0/scenarios.json`
- and `tools/check_proving_ground_matrix.py`

If no scenario changed, say so rather than silently leaving the matrix stale.
