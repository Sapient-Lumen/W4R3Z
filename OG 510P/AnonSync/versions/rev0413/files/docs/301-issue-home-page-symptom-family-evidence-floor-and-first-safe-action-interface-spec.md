# Issue home page — symptom family, evidence floor, and first safe action interface spec

## Purpose

The archive already has convergence bundles, diagnostic probes, repair ladders, and intervention receipts.
What still remained under-specified was the very first ordinary page an operator should see when something simply looks wrong:

> what family of problem is this, what evidence already exists, and what is the least-destructive first action worth taking?

Current Resilio docs make this seam concrete.
Operators are still told to inspect `Peers`, `Status`, warning rows, and several troubleshooting pages before they can tell whether they are dealing with source absence, connectivity, lock pressure, database injury, missing service material, slow internal work, or local filesystem trouble.
AnonSync should compile that into one page.

## Core decision

AnonSync must expose one first-class **Issue home** page for every active incident-like symptom family.
It is not a generic alert drawer.
It is the stable page that turns raw symptoms into an explicit issue family, evidence floor, and first safe action.

## Fixed page order

Every issue-home page should render the same sections in the same order:

1. **Current verdict**
2. **Evidence floor**
3. **First safe action**
4. **Escalation ladder**
5. **Receipts and residue**

### 1) Current verdict

Show:

- `issue_home_page_id`
- `issue_family` (`source-absence`, `reachability`, `lock-pressure`, `environment-conflict`, `integrity-damage`, `slow-progress`, `path-loss`, `unknown`)
- `affected_subject_refs[]`
- `severity` (`info`, `watch`, `degraded`, `blocked`, `unsafe-to-retry-blindly`)
- `current_verdict_summary`
- `why_this_is_the_current_family`

The page must name the strongest honest family even when ambiguity remains.
`unknown` is allowed, but only after the page names what evidence is missing.

### 2) Evidence floor

Show:

- `fresh_evidence_rows[]`
- `stale_evidence_rows[]`
- `missing_evidence_rows[]`
- `evidence_floor_verdict` (`sufficient-for-first-action`, `needs-light-refresh`, `needs-operator-inspect`, `needs-probe-plan`)
- `time_window_covered`

This section answers:

> what do we already know well enough that the first step is safe, and what still is not proven?

### 3) First safe action

Show exactly one primary recommendation plus optional alternates:

- `primary_first_action`
- `why_this_action_is_first`
- `expected_signal_after_action`
- `copy_safety_posture`
- `alternate_safe_actions[]`
- `blocked_actions[]`

Typical primary actions include:

- `wait and recheck`
- `inspect environment conflict`
- `recompute route evidence`
- `review repair ladder`
- `open crash capture`
- `touch only after environment review`

The page may not recommend destructive repair as the first action while a lighter truthful rung still exists.

### 4) Escalation ladder

Show the next stronger pages reachable if the first action fails:

- **Environment conflict**
- **Repair plan**
- **Crash capture**
- existing convergence / intervention pages where relevant

Each row should show:

- entry condition
- stronger evidence needed
- copy-safety impact
- why it is not yet the first recommendation

### 5) Receipts and residue

Show:

- `related_receipt_refs[]`
- `last_action_attempt_refs[]`
- `open_residue_rows[]`
- `when_the_page_will_recompute`

The page must preserve whether a human merely inspected the issue, attempted a first action, or escalated to a stronger lane.

## Object model implications

### Issue home page

Fields:

- `issue_home_page_id`
- `issue_family`
- `affected_subject_refs[]`
- `severity`
- `fresh_evidence_rows[]`
- `stale_evidence_rows[]`
- `missing_evidence_rows[]`
- `evidence_floor_verdict`
- `primary_first_action`
- `alternate_safe_actions[]`
- `blocked_actions[]`
- `escalation_rows[]`
- `related_receipt_refs[]`
- `next_honest_action`

### Issue-family row

Fields:

- `symptom_row_id`
- `signal_kind` (`warning-row`, `status-row`, `peer-row`, `transfer-row`, `filesystem-observation`, `operator-report`)
- `supports_issue_families[]`
- `freshness_verdict`
- `confidence_weight`

## Explicit non-goals

AnonSync should not:

- make operators open multiple unrelated pages before learning the first safe action
- present a large bag of equally-weighted troubleshooting ideas
- hide the difference between `safe first action` and `possible later repair`
- infer destructive recovery from stale evidence

## Relationship to nearby specs

This page sits above the deeper mechanisms in:

- `137-convergence-evidence-bundle-and-disambiguation-ladder-interface-spec.md`
- `138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md`
- `199-integrity-rebuild-reindex-and-subject-repair-ladder-interface-spec.md`
- `232-diagnostic-export-log-redaction-and-self-serve-support-boundary-interface-spec.md`

Those pages remain deeper tools.
This page is the ordinary front door.
