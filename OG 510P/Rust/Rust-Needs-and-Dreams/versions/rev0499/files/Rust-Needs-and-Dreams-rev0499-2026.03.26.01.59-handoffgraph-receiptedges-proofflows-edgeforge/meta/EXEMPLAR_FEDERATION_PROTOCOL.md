# Meta: Exemplar Federation Protocol (rev0466)

## Purpose
Use this protocol when the repo needs a thin shared answer to:
> once the archive has scenario cards, anchor profiles, and a shared artifact spine, what maintained proving worlds should serious pilots and future receipts actually reuse?

Read with:
- `design/portfolio-exemplar-federation-2026Q1.md`
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/portfolio-anchor-corpus-2026Q1.md`
- `design/shared-spine-execution-blueprint-2026Q1.md`

## Required assets
The first exemplar-federation lane should include:
- `proofgrounds/portfolio-exemplar-federation-v0/README.md`
- `proofgrounds/portfolio-exemplar-federation-v0/exemplars.json`
- `tools/check_exemplar_federation.py`

## Required exemplar fields
Every exemplar in the first shared federation must include:
- `exemplar_id`
- `title`
- `exemplar_class`
- `scenario_bindings`
- `anchor_bindings`
- `workspace_posture`
- `privacy_posture`
- `renewal_cadence`
- `required_artifacts`
- `comparison_invariants`
- `allowed_variation`
- `public_twin_strategy`
- `must_not_claim`
- `notes`

## Minimum federation rules
The initial federation must:
1. include at least five exemplars;
2. keep exemplar IDs unique;
3. bind every exemplar to one or more scenario IDs from `proofgrounds/portfolio-scenario-matrix-v0/scenarios.json`;
4. bind every exemplar to one or more anchor IDs from `proofgrounds/portfolio-anchor-corpus-v0/anchors.json`;
5. cover every current scenario ID at least once;
6. include at least these exemplar classes:
   - `public_inner_loop_exemplar`
   - `public_release_boundary_exemplar`
   - `restricted_shadow_exemplar`
   - `public_native_edge_exemplar`
   - `cross_target_docs_exemplar`

## Required non-claims
The federation must **not** claim that:
- one exemplar proves ecosystem-default readiness;
- public exemplar success replaces private-world validation where policy or sensitivity matter;
- exemplar cards replace scenario cards, anchor profiles, or seam-local fixtures;
- or a stale demo workspace is acceptable just because its schema still parses.

## Checker duties
`tools/check_exemplar_federation.py` should stay thin.
It may check:
- file presence;
- JSON parseability;
- required fields;
- unique IDs;
- minimum exemplar count;
- binding only to declared scenario and anchor IDs;
- and coverage of all current scenarios.

It must **not** claim to validate seam-local payload semantics, real external freshness, or whether a given public/private twin strategy is institutionally sufficient.

## Revision rule
If a revision materially changes the shared exemplar federation, it should update in the same revision:
- `design/portfolio-exemplar-federation-2026Q1.md`
- `meta/EXEMPLAR_FEDERATION_PROTOCOL.md`
- `proofgrounds/portfolio-exemplar-federation-v0/exemplars.json`
- and `tools/check_exemplar_federation.py`

If no exemplar changed, say so rather than silently leaving the federation stale.
