# 20 — Retained export envelope

## Purpose

A retained export is a detached package of a local assessed state for audit, incident review, compliance retention, current-policy recheck, or operator handoff.

It is not a new assessment unless a receiver explicitly performs a new local assessment.

## Shape

```text
retained_assessment_export:
  export_context
  local_assessed_state
  optional export_integrity
```

`local_assessed_state` remains the rev0062 object. `export_context` explains why it was exported and what profile-reference strength was expected at that export boundary.

## Export context

```text
exported_at
purpose
retention_label
profile_reference_tier
detached_from_configured_boundary
current_policy_checked
notes
```

`profile_reference_tier` uses the tiered rule from `spec/10-profile-reference-strength.md`.

## Retained-state rule

A retained export must carry a local assessed state whose `retention_context.retained` is true.

This prevents ordinary transient telemetry from being mislabeled as retained audit material.

## Digest rule

For retained export, an envelope signature is not enough. If the assessed profile's reference policy or boundary tier expects a digest, the nested `assessed_profile` must include a digest binding `normative_profile_rules`.

## Current policy rule

A historical retained assessment can remain valid at assessment time while being rejected or record-only under current policy. The retained export may carry `policy_acceptance`, but it must not rewrite historical `profile_conformance` to make the record look currently actionable.

## Receiver rule

A receiver of a retained export may record, reject, or re-evaluate the export under local policy. It must not treat the envelope's `sent_at`, file timestamp, or export timestamp as the original assessment time.
