# Crate Health Contract Kit fixtures

This fixture family exists to keep **P-0011 Crate Health Contract Kit** concrete.

The core claim is that crate health should be a **reviewable contract**, not a popularity proxy, not a single release-date heuristic, and not a grab-bag of security/publishing signals.

## Core review objects

- `health-profile.report.json`
- `maintenance-window.report.json`
- `succession-map.report.json`
- `support-intent.report.json`
- `maintenance-coverage.report.json`
- `health-check.report.json`
- `work-routing.report.json`
- `response-channel.receipt.json`
- `continuity-backstop.report.json`
- `registry-signal.import.json`
- `routing-drift.diff.json`
- `health-support-bundle.manifest.json`

## What these fixtures are trying to protect

They protect against flattening all of the following into one fake verdict:

- recent publish activity,
- security-tab presence,
- trusted-publishing posture,
- one maintainer-authored note,
- downstream assumptions about long-term support,
- and whether invisible maintenance work is actually covered or just implied by visible activity.

## Scenario families

### `quiet_release_stream_but_reactive_support_is_explicit/`
A crate can publish infrequently and still make an honest reactive-support promise.
The fixture shows how a quiet release stream should not automatically read as abandonment.

### `deprecated_lane_without_successor_window_or_backup_fails_health_check/`
A crate can look “transparent” about deprecation while still failing to tell downstream users:
- who carries support now,
- whether any successor exists,
- or how long current versions are still in scope.

The fixture keeps that omission visible.

### `quiet_release_stream_has_lights_on_coverage_but_review_capacity_gap/`
A crate can honestly cover janitorial work while still lacking explicit review and contributor-enablement capacity.
The fixture keeps quiet support from being mistaken for broad stewardship coverage.

### `active_feature_work_without_ci_security_or_docs_owner_needs_manual_review/`
A crate can look vibrant from release notes and PR activity while still leaving CI, security response, or documentation freshness ownerless.
The fixture keeps visible feature momentum from laundering invisible maintenance gaps.


### `public_bug_route_private_security_route_and_explicit_ci_owner/`
A crate can honestly expose public issue intake while still keeping security reports private and CI breakages routed more narrowly.
The fixture keeps “open an issue” from being treated as a universal support answer.

### `codeowners_paths_do_not_by_themselves_define_release_or_security_routes/`
A crate can import useful review ownership from CODEOWNERS and still have no honest release or security route.
The fixture keeps path review substrate from laundering broader stewardship claims.

### `single_primary_with_org_backstop_and_rotation_window/`
A crate can depend on one primary maintainer while still documenting an organization backstop.
The fixture keeps continuity posture separate from both pure bus-factor folklore and fully staffed maintainer-team claims.


### `security_tab_trusted_publishing_and_private_reporting_do_not_define_release_or_docs_routes/`
A crate can expose richer crates.io and GitHub security/publishing substrate and still fail to tell downstream users who owns releases or docs freshness.
The fixture keeps imported stewardship context from laundering broader routing claims.

### `repository_transfer_and_team_backstop_change_need_routing_drift/`
A repository transfer can preserve a lot of host state while still changing effective stewardship posture.
The fixture keeps transport success and collaborator continuity separate from honest routing/continuity drift.

### `portable_bundle_keeps_declared_imported_and_manual_gaps_separate/`
A receiver should be able to review one compact stewardship bundle without guessing which facts were maintainer declarations and which were imported host/registry context.
The fixture keeps manual-review gaps visible inside the portable bundle.
