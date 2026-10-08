# Evidence-gap and closure contracts — 2026-03-24

This note keeps three packet families distinct.

## `evidence-gap.report`

A statement of:
- which stage/gate is currently unsatisfied,
- which subject or starter set the gap applies to,
- which existing packet exposed the gap,
- what class of gap it is,
- and whether the gap is automatable, manual-artifact, manual-judgment, or blocked-upstream.

It is **not**:
- a workflow ticket,
- proof that the gap can be solved,
- or a fresh decision packet.

## `evidence-campaign.plan`

A statement of:
- which gaps are in scope for the current bounded effort,
- which actions will be taken,
- which artifacts are expected,
- which authority route each action uses,
- who owns it,
- and what stop conditions end the campaign.

It is **not**:
- proof that the campaign succeeded,
- permission to skip adjudication,
- or a general task-management system.

## `gap-closure.receipt`

A statement of:
- which specific gap moved,
- which produced artifacts justify the movement,
- what closure status now applies,
- which earlier basis remains inherited,
- and which gaps remain open.

It is **not**:
- proof that the stage is fully satisfied,
- retroactive rewriting of the earlier basis,
- or a replacement for progression/adjudication artifacts.

## Required vocabulary

### Gap classes

A useful `0.1` vocabulary:
- `source_parity_missing`
- `docs_materialization_missing`
- `docsrs_parity_missing`
- `target_support_unresolved`
- `security_state_unresolved`
- `trusted_publishing_unknown`
- `review_backlog_open`
- `profile_floor_unmet`
- `manual_judgment_required`
- `other`

### Automation classes

A useful `0.1` vocabulary:
- `local_command`
- `hosted_import`
- `manual_review`
- `upstream_request`

### Closure statuses

A useful `0.1` vocabulary:
- `closed`
- `partially_closed`
- `blocked`
- `reopened`
- `manual_review_required`

### Campaign stop conditions

A useful `0.1` vocabulary:
- `stage_can_progress`
- `remaining_gaps_need_adjudication`
- `gap_moved_to_exception`
- `blocked_upstream`
- `new_compare_required`

## Non-claims that must stay explicit

Even when the packets look good, the crate must refuse to imply:

- that docs.rs queue/build/download facts equal offline-readiness by themselves,
- that crates.io Security-tab visibility equals safety or task fit,
- that Trusted Publishing equals operational suitability,
- that `cargo vet suggest` backlog items must all be turned into audits,
- that `cargo vet renew` means the underlying criteria story broadened,
- or that one closed gap automatically closes the rest of the stage.

## Why this separation matters

The current Rust substrate now exposes enough structured data that future tooling will be tempted to flatten:
- public metadata,
- local checks,
- hosted checks,
- policy decisions,
- and missing evidence

into one generic “score”.

This note exists so the archive does not do that.
A worthy crate should say:
- what is known,
- what is missing,
- what is being attempted,
- and what changed

as four different things.

## Sources

- Cargo plumbing
- Cargo build analysis
- docs.rs builds / metadata / download / queue
- crates.io Security tab / Trusted Publishing / `pubtime`
- Cargo Vet commands / wildcard audits
- cargo-deny common options
