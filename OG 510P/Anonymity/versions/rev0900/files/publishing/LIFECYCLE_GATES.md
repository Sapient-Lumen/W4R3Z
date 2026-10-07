# Lifecycle Gates

This file says *when* each compact control surface matters.
It is the stage-by-stage crosswalk, not the current state report.
For the current bundle's gate statuses, see `reports/lifecycle_gate_status.json`.

## Reentry

**Gate:** `reentry_identity_and_trust`

Use these first:

- `VERSION`
- `RELEASE_MANIFEST.json`
- `REVISION_RECEIPT.json`
- `START_HERE.md`
- `CONTEXT_PACK.json`
- `reports/archive_surface_coherence.json`
- `reports/transient_surface_audit.json`
- `reports/manifest_sha256_verification.json`
- `reports/operator_command_hygiene.json`

If these disagree, stop and repair them before trusting anything smaller than the full archive tree.

## Public boundary

**Gate:** `citation_and_public_boundary`

Use these when the question is “what is publicly citable right now?” rather than “what exists in the repo?”

- `published/CITATION_HEADS.md`
- `published/citation_heads.json`
- `published/LEGACY_PUBLISHED_LINKS.md`
- `published/legacy_published_links.json`
- `published/PUBLICATION_CLASSIFICATION.md`
- `published/publication_classification.json`
- `published/PUBLIC_SURFACE.json`

If these disagree, publish nothing and do not casually cite frozen repo material as public.

## Queue

**Gate:** `queue_and_decision_integrity`

Use these when you need the current queue posture and decision lineage without hand-crawling the repo:

- `release_queue/QUEUE_INDEX.json`
- `release_queue/REVIEW_INVENTORY.json`
- `reports/review_inventory_integrity.json`
- `release_queue/LATEST_DECISION.md`
- `release_queue/DECISION_INDEX.md`
- `release_queue/DECISION_INDEX.json`

If these disagree, do not move papers between states.

## Paper review

**Gate:** `review_move_readiness`

Use these before any Candidate / Hold / Published-ready move:

- `publishing/REVIEW_ORDER.md`
- `publishing/REVIEW_RUBRIC.md`
- `publishing/TURN_DECISION_PROTOCOL.md`
- `release_queue/QUEUE.md`
- `release_queue/STATUS.md`

If any of this context is missing, the safe move is a written no-move decision.

## Publication execution

**Gate:** `publication_execution`

Use these before an actual release:

- `PUBLISHING.md`
- `publishing/CONSERVATIVE_RELEASE_POLICY.md`
- `publishing/RELEASE_FLOW.md`
- `publishing/release_preflight.py`
- `release_queue/LATEST_DECISION.md`
- `published/PUBLIC_SURFACE.json`

This gate is intentionally narrow and usually closed.
A bundle with no explicit publish decision should say so clearly.

## Post-publication audit

**Gate:** `post_publication_audit`

Use these after any new public release:

- `published/CITATION_HEADS.md`
- `published/PUBLIC_SURFACE.json`
- `published/INDEX.md`
- `reports/archive_surface_coherence.json`
- `reports/manifest_sha256_verification.json`
- `MANIFEST.sha256`

The right default after publication is not celebration but a fresh audit.
