# Standing-policy lineage and subject-attribution interface spec

The archive already separates current share posture from future-arrival policy, explains why a later arrival is here now, and previews what one standing-policy edit will change.
What still remained too easy to lose was the **versioned bridge** between those surfaces:

> after a few standing-policy edits, which exact policy version handled this subject, what changed since then, and is the subject still carrying a grandfathered outcome that newer arrivals would not get now?

This document turns that question into one explicit interface contract.
It is the lineage companion to `58-policy-origin-defaults-and-precedence-spec.md`, the explainability companion to `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`, the auditability companion to `102-policy-delta-preview-and-arrival-simulation-interface-spec.md`, and the historical precursor to `104-subject-policy-drift-and-realignment-review-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync Private Identity & Linking My Devices`, `Selective Sync`, `Folder Types and Management`, `Synchronization Modes`, `How to manually set the location of the folders synced across linked devices?`, and `Settings on mobile platforms` together still describe a system where:

- linked-device mode changes apply to newly added folders while current ones remain as they are
- prior approval can let later pending folders auto-connect
- future sharing can widen to all linked devices after one approval choice
- default roots and mobile `Simple mode` still steer later arrivals
- current help is mostly about what the current settings mean, not about which older policy version handled a given subject

That is real convenience.
But once policy changes accumulate, the operator still has to reconstruct history from memory:
which arrivals are grandfathered, which draft path came from an older template, which approval match happened under a wider remembered scope, and whether today's current setting actually explains yesterday's local state.

AnonSync should not accept that reconstruction burden.
Any standing-policy family that can change later-arrival behavior should therefore surface one explicit **lineage and attribution contract**.

## Core rule

A standing-policy family is not fully inspectable until the product can answer five questions in one place:

1. what effective policy version is current now for this seat/scope
2. what older versions preceded it and when they were superseded
3. which exact version handled this subject when it was announced, drafted, matched, or bound
4. how that older applied version differs from the current version now
5. which receipt proves the policy transition or subject attribution being claimed

If the operator still has to compare current settings with fuzzy memory of prior modes, approvals, or default roots to answer those five questions, the surface is not explicit enough.

## Public objects

### Standing policy version

A durable snapshot of one effective standing-policy family for one reviewed seat and governed scope.

Suggested fields:

- `standing_policy_version_id`
- `seat_ref`
- `governed_scope`
- `policy_family` (`arrival-template`, `approval-memory`, `admission-default`, `placement-default`, `materialization-default`)
- `version_seq`
- `effective_from`
- `superseded_at` nullable
- `policy_fields`
- `created_by_receipt_ref`
- `superseded_by_version_ref` nullable
- `superseded_by_receipt_ref` nullable
- `notes` nullable

### Policy lineage entry

A compact row describing one transition in a standing-policy family.

Suggested fields:

- `lineage_entry_id`
- `policy_version_ref`
- `status` (`current`, `superseded`, `future-staged`, `revoked`)
- `delta_summary`
- `effect_boundary_summary`
- `non_effect_summary`
- `receipt_ref`

### Subject policy attribution

A read object connecting one subject to the standing-policy version(s) that influenced it.

Suggested fields:

- `subject_policy_attribution_id`
- `subject_ref`
- `seat_ref`
- `governed_scope`
- `current_subject_stage`
- `applied_policy_version_ref`
- `applied_at`
- `attribution_class` (`matches-current`, `grandfathered`, `draft-carried-forward`, `memory-matched`, `superseded-before-bind`, `unknown`)
- `difference_from_current_summary`
- `current_policy_version_ref`
- `supporting_receipt_refs[]`

### Policy compare projection

A compare view between one older applied version and the current effective version.

Suggested fields:

- `policy_compare_projection_id`
- `older_version_ref`
- `current_version_ref`
- `field_diffs[]`
- `semantic_diffs[]`
- `subject_effect_summary`
- `non_effect_summary`
- `counterfactual_summary`

## Fixed inspection order

Every lineage/attribution surface should preserve the same sections in the same order:

1. **Seat, scope, and current effective version**
2. **Version lineage**
3. **Subject attribution**
4. **Current-versus-applied compare**
5. **What did not change**
6. **Admissible actions**
7. **Receipts and proof links**

### 1) Seat, scope, and current effective version

This section should show:

- which reviewed seat is in view
- which governed scope is in view
- the current effective version id and its effective-from time
- the compact semantic summary of that current version

The operator must be able to answer: **what policy is in force here now?**

### 2) Version lineage

This section should show:

- newest-to-oldest lineage entries
- each delta summary
- each effect-boundary summary
- which receipt created or superseded each version

The operator must be able to answer: **what changed, and in what order?**

### 3) Subject attribution

This section should show, for the current subject or selected subjects:

- which policy version handled the subject
- at which lifecycle point it mattered (`announced`, `matched`, `drafted`, `claimed`, `bound`)
- whether the subject now matches current policy or is grandfathered
- which receipt proves the relevant transition or application

The operator must be able to answer: **which rule actually touched this thing?**

### 4) Current-versus-applied compare

This section is mandatory whenever the applied version differs from current.
It should show:

- field-level differences
- semantic differences in ordinary language
- the strongest effect difference for this subject
- one counterfactual summary (`if this arrived now, it would ...`)

Example:

```text
Applied then: claim-suggested under /srv/family/{{share_name}}
Current now: announce-only under /tank/family/{{share_name}}
If Photos-2026 arrived now, it would remain announced and no draft path would be created.
```

The operator must be able to answer: **what is different now from the rule that handled this subject then?**

### 5) What did not change

This section is mandatory.
It should include the strongest easy-to-misread non-effects, for example:

- the older draft kept its prior candidate path until explicitly refreshed
- the standing-policy edit did not rebind already bound shares
- the attribution being shown does not imply that current policy is invalid now
- changing current policy later did not retroactively fabricate a different old receipt

The operator must be able to answer: **what tempting but false reading should I avoid?**

### 6) Admissible actions

This section should allow verbs such as:

- `Inspect current policy`
- `Inspect applied version`
- `Compare versions`
- `Refresh eligible draft under current policy`
- `Keep grandfathered outcome`
- `Open wider policy lineage`

It must not flatten unlike outcomes into one vague `Update` or `Reconnect` verb.

### 7) Receipts and proof links

The receipts section should show:

- the mutation receipt that created the current version
- the mutation receipt that superseded the older version, if any
- the subject receipt that proves the subject's stage or bind under that older version
- whether the compare projection was live-computed or cached

The operator must be able to answer: **what later proof confirms the timeline being claimed?**

## Row and card contract

A truthful compact row should keep these facts adjacent, in this order:

1. subject or seat/scope
2. current effective version summary
3. applied version summary
4. strongest grandfathering or matches-current fact
5. next honest action

Example subject row:

```text
Photos-2026   current: announce-only /tank/family   applied: claim-suggested /srv/family   grandfathered draft   Explain policy lineage
```

Example seat row:

```text
Home-NAS / family arrivals   current v7 announce-only   previous v6 claim-suggested   3 grandfathered subjects   View lineage
```

Opening the row should reveal version lineage and compare before any refresh or apply action.

## Dense/mobile rule

Dense and mobile clients may compress wording, but they must still preserve:

- current version summary
- applied-version or `matches current` summary
- one explicit grandfathering or non-grandfathering label
- an entry point to receipts or compare

A dense client may shorten `grandfathered by prior template` to `grandfathered v6`, but it may not hide whether the subject still reflects an older policy version.

## CLI contract

The CLI should expose lineage and attribution as first-class read surfaces:

```text
anonsync policy lineage show --seat home-nas --scope family-arrivals
anonsync policy lineage show --seat home-nas --scope family-arrivals --history 10
anonsync subject policy show --subject incoming:photos-2026 --seat home-nas
anonsync policy compare --current spv_01J... --applied spv_01H...
anonsync policy receipt show pdr_01J...
```

The CLI should never reduce this to `settings get mode`, `current defaults`, or equivalent folklore.

## What must never be implied

The interface must never imply that:

- today's current policy version fully explains every older subject still visible on the seat
- a grandfathered subject is broken merely because it differs from current policy
- a later policy edit rewrote the historical receipt that handled an older subject
- one subject compare is the same as a full policy-family lineage view
- policy lineage can be reconstructed safely from labels like `Selective Sync`, `Disconnected`, or `Simple mode` alone

The truthful contract is: **current version first, applied version second, compare third, receipts always reachable**.
