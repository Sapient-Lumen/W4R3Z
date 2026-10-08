# Support bundle manifest

A support bundle is the smallest named artifact that can carry a support claim without collapsing code, fixtures, snapshots, and operator interpretation into one vague sentence.

## Rule

A support bundle manifest should make the following explicit:

- which `surface × workflow-set × lane` it is about
- whether the bundle is only a candidate, intentionally held, review-ready, or published
- which named artifacts another implementer should inspect first
- what the bundle can support today and what it still cannot support honestly

## Required fields

Current GlassTTY support bundle manifests require:

- `bundle_key`
- `bundle_status`
- `surface_key`
- `browser_lane`
- `captured_at`
- `workflows_touched`
- `artifact_refs`
- `support_record`
- `result_summary`
- `publication_decision`

Optional but increasingly important fields:

- `claim_scope.publication_blockers`
- `publish_guard`
- `transition_history`

## Statuses

- `candidate` — coherent enough to review
- `hold` — useful evidence exists, but stronger publication should stop here for now
- `published-ready` — review says the bundle can safely support stronger support language
- `published` — frozen support artifact that living records may cite directly

## Current doctrine

A held bundle is still valuable. It means GlassTTY has turned scattered evidence into one inspectable support object without pretending that publication blockers do not exist.


Use `python scripts/support-bundle-transition.py ...` when the manifest changes queue state so `bundle_status` and `publication_decision.decision` stay aligned.


## Publish guard

Bundles that clear `published-ready` or `published` should carry a `publish_guard` recording the current support-record / support-surface / published-support / revision heads they were reviewed against.

That lets GlassTTY surface stale published support as a head mismatch instead of silently pretending old review still binds to newer truth heads.
