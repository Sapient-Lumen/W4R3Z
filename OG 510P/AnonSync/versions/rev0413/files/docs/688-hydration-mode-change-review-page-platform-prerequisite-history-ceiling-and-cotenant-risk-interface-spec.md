# Hydration-mode change review page: platform prerequisite, history ceiling, and co-tenant risk interface spec

## Purpose

This review page exists because changing hydration mode is not one storage toggle.
A change can:

- switch engines entirely
- add or remove shell/provider action lanes
- move a subject from eligible to degraded or blocked on the current path
- narrow retained-history guarantees
- disable or restore collision detection expectations
- become unsafe because another cloud provider, another runtime, or inherited local flags already occupy the same lane

The operator must review those consequences before commit.

## Review sections

Render the following sections in order:

1. **Current contract**
2. **Requested contract**
3. **Prerequisite verdict**
4. **Action-lane consequences**
5. **History and collision consequences**
6. **Co-tenant and parallel-runtime risk**
7. **Action choices**
8. **Receipt promise**

### 1) Current contract

Show:

- current engine
- current lane health
- current eligibility verdict
- current history guarantee
- current collision guarantee
- current safe sentence

### 2) Requested contract

Show:

- requested engine or lane change
- requested scope
- whether the change is live, recreate-only, path-migration-only, or blocked
- seats / subjects affected

### 3) Prerequisite verdict

Show:

- OS / provider API readiness
- filesystem / path readiness
- extension / provider readiness
- strongest unmet prerequisite
- whether a different path class would satisfy the request

The operator must be able to answer: **can the requested engine honestly run here?**

### 4) Action-lane consequences

Show:

- whether open/double-click hydration changes
- whether context-menu or provider actions appear, disappear, or degrade
- whether in-app fallback remains available
- whether subtree pin / keep-local / evict-local actions change scope or proof

The operator must be able to answer: **what local interaction model changes after apply?**

### 5) History and collision consequences

Show:

- whether prior file versions remain retained, narrow to delete-only, or disappear
- whether collision detection remains full, narrows, or becomes unsupported
- whether local-only hydrated files change cleanup or reclaim behavior
- whether the requested change alters later recovery language

The operator must be able to answer: **what rollback and conflict promises survive this change?**

### 6) Co-tenant and parallel-runtime risk

Show:

- existing provider conflicts
- parallel runtime / multi-agent conflicts
- inherited cloud-file flags / attributes that may override the expected default
- version-line or seat-line caveats that change the guarantee

The operator must be able to answer: **what other local systems can distort the requested result?**

### 7) Action choices

Offer only honest actions:

- `Apply requested engine`
- `Use in-app-only fallback`
- `Move subject to an eligible path first`
- `Keep current engine`
- `Block until co-tenant conflict is removed`
- `Create successor subject with requested engine`

Each choice must state claim ceiling afterward.

### 8) Receipt promise

The resulting receipt must prove:

- requested engine/lane change
- effective engine afterward
- unmet prerequisites if any
- action-lane changes that actually took effect
- history/collision ceiling after apply
- co-tenant findings
- strongest safe sentence afterward

## Review object

Fields:

- `hydration_review_id`
- `subject_ref`
- `current_engine`
- `requested_engine`
- `current_lane_health`
- `requested_lane_intent`
- `current_history_guarantee`
- `requested_history_expectation`
- `current_collision_guarantee`
- `requested_collision_expectation`
- `eligibility_findings[]`
- `cotenant_findings[]`
- `path_migration_required` boolean
- `apply_path` (`live`, `recreate`, `migrate-path-first`, `blocked`)
- `strongest_safe_sentence_after`

## Rules

### Rule 1 — prerequisite failure must be explicit before commit

No silent fallback from one hydration engine to a weaker one.

### Rule 2 — history/collision narrowing is review-grade

If the requested change lowers rollback or collision truth, the review must say so plainly before apply.

### Rule 3 — co-tenant conflict is not troubleshooting garnish

Conflicts with other provider lanes or another runtime are part of the contract.

### Rule 4 — action-lane loss is not merely cosmetic

If the local interaction model changes, the review must carry that fact as a contract delta, not a UI footnote.

## Acceptance criteria

A later operator can see:

- what was requested versus what became effective
- whether the path/seat really qualified for the requested engine
- which local action lanes changed
- which rollback/collision promises narrowed or survived
- what co-tenant risk remained at commit time
