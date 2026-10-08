# Archive stewardship handoff controls

Generated for `rev0799` from `metadata/archive_stewardship_handoff_controls.json`.

Non-closing stewardship handoff controls for license, maintainer authority, contribution rules, security contact, release signing, route retirement, source refresh, and succession. These controls make missing owner decisions explicit; they do not grant rights, appoint maintainers, authorize reuse, or close any live gap.

## Handoff policy

A ZIP, green lint result, release note, generated manifest, or public reader surface is not a custodian. Every future closure, source-preservation, route-retirement, security, contribution, license, and succession decision needs named authority outside the artifact. The control can block closure and surface missing decisions; it cannot supply the owner decision.

## Summary counts

| Metric | Count |
| --- | ---: |
| Stewardship handoff controls | 3 |
| Gap blockers | 5 |
| Required public documents | 17 |
| Required role classes | 15 |

## Handoff status counts

| Status | Count |
| --- | ---: |
| `owner_decision_required` | 1 |
| `security_contact_and_scope_required` | 1 |
| `successor_and_review_cadence_required` | 1 |

## Gap blockers

| Gap | Handoff controls |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `ASH-SUCCESSION-001` |
| `GAP-030-active-route-retirement-and-taxonomy-control` | `ASH-ARCHIVE-001`, `ASH-SUCCESSION-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `ASH-ARCHIVE-001`, `ASH-SECURITY-001`, `ASH-SUCCESSION-001` |
| `GAP-032-license-maintainer-contribution-governance` | `ASH-ARCHIVE-001`, `ASH-SECURITY-001`, `ASH-SUCCESSION-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `ASH-ARCHIVE-001`, `ASH-SUCCESSION-001` |

## Control details

### `ASH-ARCHIVE-001` — Archive license, maintainer authority, contribution, citation, and release-signing handoff

Status: `owner_decision_required`

Handoff blocker: Blocks GAP-032 and any future stewardship closure. Public files, schemas, and generated indexes can show what decisions are missing, but they do not grant rights, appoint maintainers, define contribution authority, or authorize route/source/gap decisions.

| Handoff family | Items |
| --- | --- |
| Linked gaps | GAP-030-active-route-retirement-and-taxonomy-control; GAP-031-source-evidence-preservation-and-claim-capture; GAP-032-license-maintainer-contribution-governance; GAP-033-power-distribution-and-material-outcome-theory |
| Source-claim receipts | SCR-M16-21-OPEN-CODE-001; SCR-GSA-OSS-POLICY-001; SCR-REUSE-LICENSE-001; SCR-CC-LICENSE-CONSIDERATIONS-001; SCR-OSS-GOVERNANCE-ROLES-001 |
| Required owner decisions | license_family_and_exact_license_text; copyright_holder_and_attribution_statement; maintainer_or_steward_names_or_role_classes; merge_release_and_gap_closure_authority; citation_and_reuse_guidance; AI_or_bulk_contribution_policy; route_demotion_and_retirement_authority; source_snapshot_and_preservation_authority |
| Required public documents | LICENSE_or_RIGHTS.md; NOTICE_or_ATTRIBUTION.md; GOVERNANCE.md; MAINTAINERS.md; CONTRIBUTING.md; CITATION.cff_or_CITATION.md; RELEASE_PROCESS.md; RETIREMENT_POLICY.md; SOURCE_PRESERVATION_POLICY.md |
| Role classes required | owner_or_rightsholder; release_manager; source_preservation_steward; route_retirement_steward; security_contact; contribution_reviewer; gap_closure_reviewer; succession_backup |
| Handoff clocks | owner_decision_clock; license_review_clock; maintainer_confirmation_clock; release_signing_clock; source_refresh_clock; route_retirement_review_clock; succession_review_clock |
| Allowed cube artifacts | public document presence status; role class without contact detail; decision status class; review clock class; source-claim receipt identifiers; gap blocker list; limitation statement; public release hash after signing |
| Prohibited cube artifacts | private legal advice; private owner email; signature image; credential; access token; private security report; embargoed vulnerability detail; private contributor identity document; unpublished license negotiation |

Next action: Prepare owner-review drafts of LICENSE/RIGHTS, GOVERNANCE, MAINTAINERS, CONTRIBUTING, SECURITY, CITATION, RELEASE_PROCESS, RETIREMENT_POLICY, and SOURCE_PRESERVATION_POLICY. Do not mark them approved until owner/legal/stewardship review is complete. Confirm license, maintainer, security, and succession handoff scope before treating this control as stewardship.

### `ASH-SECURITY-001` — Security contact, vulnerability disclosure, private-report routing, and embargo boundary handoff

Status: `security_contact_and_scope_required`

Handoff blocker: Blocks security-governance closure. A SECURITY.md requirement, disclosure template, or public contact class does not itself create a monitored inbox, safe harbor, response capacity, or private-report custody.

| Handoff family | Items |
| --- | --- |
| Linked gaps | GAP-031-source-evidence-preservation-and-claim-capture; GAP-032-license-maintainer-contribution-governance |
| Source-claim receipts | SCR-CISA-VDP-001; SCR-CISA-VDP-TEMPLATE-001; SCR-GSA-OSS-POLICY-001 |
| Required owner decisions | security_contact_channel; scope_of_covered_surfaces; report_acknowledgment_expectation; embargo_and_public_disclosure_boundary; triage_owner_and_backup; private_report_storage_location_outside_cube; public_advisory_release_authority |
| Required public documents | SECURITY.md; VULNERABILITY_DISCLOSURE.md_or_security_section; RELEASE_PROCESS.md; INCIDENT_RESPONSE_POINTER.md |
| Role classes required | security_contact; security_triage_backup; release_manager; privacy_reviewer; source_preservation_steward |
| Handoff clocks | security_contact_confirmation_clock; vulnerability_acknowledgment_clock; triage_clock; advisory_release_clock; post_advisory_correction_clock |
| Allowed cube artifacts | public security-contact status class; public covered-scope class; source-claim receipt identifiers; non-sensitive advisory status; limitation statement |
| Prohibited cube artifacts | private vulnerability report; embargoed exploit detail; secret scan output; credential; access token; reporter private contact detail; private remediation branch; private incident log |

Next action: Draft SECURITY.md with covered scope, reporting channel, acknowledgment posture, non-retaliation/safe-harbor language if approved, and private report custody outside the cube. Do not publish as active until the channel and owners are real. Confirm license, maintainer, security, and succession handoff scope before treating this control as stewardship.

### `ASH-SUCCESSION-001` — Succession, source-refresh, post-closure monitoring, and route-retirement handoff

Status: `successor_and_review_cadence_required`

Handoff blocker: Blocks treating rev0799 or any later ZIP as self-maintaining. Succession controls can define review clocks and role classes, but cannot name a willing successor, guarantee future monitoring, or prove route retirement/source refresh occurred.

| Handoff family | Items |
| --- | --- |
| Linked gaps | GAP-029-affected-person-outcome-validation; GAP-030-active-route-retirement-and-taxonomy-control; GAP-031-source-evidence-preservation-and-claim-capture; GAP-032-license-maintainer-contribution-governance; GAP-033-power-distribution-and-material-outcome-theory |
| Source-claim receipts | SCR-A123-2026-MONITORING-001; SCR-GAO-GREENBOOK-MONITORING-001; SCR-GAO-EVIDENCE-CI-001; SCR-A11-S290-LEARNING-001; SCR-GSA-OSS-POLICY-001; SCR-OSS-GOVERNANCE-ROLES-001 |
| Required owner decisions | named_successor_or_stewardship_body; handoff_trigger_for_inactivity_or_unavailability; source_refresh_owner; postclosure_monitoring_owner; route_demotion_authority; gap_reopen_authority; archive_freeze_or_read_only_policy |
| Required public documents | SUCCESSION.md; MAINTAINERS.md; SOURCE_REFRESH_RUNBOOK.md; POSTCLOSURE_MONITORING_RUNBOOK.md; RETIREMENT_POLICY.md; GAP_REOPEN_POLICY.md; ARCHIVE_FREEZE_POLICY.md |
| Role classes required | primary_steward; backup_steward; source_refresh_steward; postclosure_monitoring_steward; route_retirement_steward; gap_reopen_reviewer; release_manager |
| Handoff clocks | inactivity_review_clock; source_refresh_clock; postclosure_monitoring_clock; route_retirement_clock; gap_reopen_clock; succession_drill_clock |
| Allowed cube artifacts | public successor role class; review cadence class; source-refresh status class; route-retirement decision class; gap reopen decision class; public limitation statement |
| Prohibited cube artifacts | private succession agreement; private owner contact detail; private claimant or household evidence; linkage key; administrative extract; embargoed security report; credential; access token |

Next action: Draft SUCCESSION, SOURCE_REFRESH_RUNBOOK, POSTCLOSURE_MONITORING_RUNBOOK, RETIREMENT_POLICY, GAP_REOPEN_POLICY, and ARCHIVE_FREEZE_POLICY. Keep every live gap open or in progress until owners accept the runbooks and clocks. Confirm license, maintainer, security, and succession handoff scope before treating this control as stewardship.


## Privacy posture

The cube may hold public-safe stewardship classes, owner-decision status, linked gap identifiers, source-claim receipt identifiers, role classes, document-name requirements, release-signing requirements, security-contact classes, succession-clock classes, and route-retirement authority classes. It must not hold private owner contact details, private security reports, embargoed vulnerabilities, private legal advice, contributor identity documents, signatures, credentials, tokens, or custody of external private evidence.
