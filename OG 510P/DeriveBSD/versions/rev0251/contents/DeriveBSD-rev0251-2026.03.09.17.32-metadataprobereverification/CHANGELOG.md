## 2026-03-09r254

- Keep later stronger packet-capture evidence checks metadata-first by accepting `adrs/ADR-0115-packet-capture-strong-export-remote-reverification-boundary.md`, adding `docs/525-packet-capture-strong-export-remote-reverification-boundary.md`, and introducing generic/packet transport reverification receipts plus canonical stronger packet examples so follow-up evidence re-checks join the computed export+acceptance receipts and keep `reverification.body_downloaded = false` instead of re-downloading packet bytes or trusting portal screenshots (`spec/transport.reverification.receipt.schema.json`, `spec/packet.capture.export.transport.reverification.receipt.profile.schema.json`, `spec/examples/transport.reverification.receipt.json`, `spec/examples/packet.capture.export.transport.reverification.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, support-handoff, export-posture, risk-register, hygiene, runbook, juicy-lesson, curated-reference, README, and archive-map docs around that remote-reverification boundary so later stronger `packet.capture.normalized` follow-up now uses typed metadata-only `transport.reverification.receipt` evidence and preserves the same accepted remote validator / protection posture / locator (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`, `docs/525-packet-capture-strong-export-remote-reverification-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_reverification_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_reverification_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

# Changelog

## 2026-03-09r253

- Keep stronger packet-capture raw-byte export discoverable after handoff by accepting `adrs/ADR-0114-packet-capture-strong-export-remote-locator-continuity-boundary.md`, adding `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`, and tightening the transport / transport-acceptance / export schemas plus canonical stronger packet-export examples so `result.remote_locator`, `acceptance.remote_locator`, and `adapter.remote_locator` stay aligned instead of leaving later evidence retrieval to portal folklore (`spec/transport.receipt.schema.json`, `spec/transport.acceptance.receipt.schema.json`, `spec/export.receipt.schema.json`, `spec/packet.capture.export.transport.receipt.profile.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, support-handoff, export-posture, risk-register, hygiene, runbook, juicy-lesson, README, and archive-map docs around that remote-locator boundary so stronger `packet.capture.normalized` handoff now preserves one typed recipient-side locator for later retrieval/review instead of leaving operators to portal folklore (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`, `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_remote_locator_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_remote_locator_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-09r252

- Keep stronger packet-capture raw-byte export honest about recipient-side durability by accepting `adrs/ADR-0113-packet-capture-strong-export-remote-protection-posture-boundary.md`, adding `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`, and tightening the transport-acceptance/export schemas plus canonical stronger packet-export examples so `acceptance.remote_protection` and `adapter.remote_protection` stay aligned instead of letting any recipient-accepted upload quietly count as durable evidence (`spec/transport.acceptance.receipt.schema.json`, `spec/export.receipt.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, support-handoff, export-posture, risk-register, hygiene, runbook, juicy-lesson, curated-reference, README, and archive-map docs around that remote-protection boundary so stronger `packet.capture.normalized` handoff now has to name the same recipient-side overwrite/delete-resistance posture instead of treating acceptance alone as a durable-evidence claim (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`, `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_remote_protection_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_remote_protection_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-09r251

- Keep stronger packet-capture raw-byte export on one stable remote representation/version validator by accepting `adrs/ADR-0112-packet-capture-strong-export-remote-validator-continuity-boundary.md`, adding `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`, and tightening the transport/acceptance/export schemas plus canonical stronger packet-export examples so `result.remote_validator`, `acceptance.remote_validator`, and `adapter.remote_validator` stay aligned instead of letting the proof chain collapse back to object id alone (`spec/transport.receipt.schema.json`, `spec/transport.acceptance.receipt.schema.json`, `spec/export.receipt.schema.json`, `spec/packet.capture.export.transport.receipt.profile.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, support-handoff, export-posture, risk-register, hygiene, runbook, juicy-lesson, README, and archive-map docs around that remote-validator boundary so stronger `packet.capture.normalized` handoff now preserves the strongest remote representation/version token the adapter can see instead of treating one remote object id as the whole story (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`, `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_remote_validator_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_remote_validator_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-09r250

- Keep stronger packet-capture raw-byte export on one stable remote object id by accepting `adrs/ADR-0111-packet-capture-strong-export-remote-object-continuity-boundary.md`, adding `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`, and tightening the packet-capture export receipt profile/example so canonical stronger export now requires `adapter.remote_id` and keeps it aligned with transport/acceptance object references (`spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.receipt.profile.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, export-posture, support-handoff, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that remote-object continuity boundary so stronger `packet.capture.normalized` handoff now stays on the same remote object identifier all the way through transport, recipient acceptance, and final export evidence instead of treating “some object in CASE-8841” as good enough (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_remote_object_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_remote_object_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-09r249

- Keep stronger packet-capture raw-byte export recipient acceptance about the exact accepted bytes by accepting `adrs/ADR-0110-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, adding `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, and tightening the packet-capture transport-acceptance profile/example so stronger recipient acceptance now requires `acceptance.remote_artifact_digest` rather than a remote reference alone (`spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, export-posture, support-handoff, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that remote-digest boundary so stronger `packet.capture.normalized` handoff now stays on the same normalized digest all the way through recipient-side acceptance instead of treating “accepted something in CASE-8841” as good enough (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_recipient_digest_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_recipient_digest_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-09r248

- Keep stronger packet-capture raw-byte export recipient-bound by accepting `adrs/ADR-0109-packet-capture-strong-export-destination-bound-approval-boundary.md`, adding `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, and tightening the packet-capture export consent request / export receipt shapes so stronger approval now binds `action.destination`, packet-capture export receipts can carry destination `domain`, and the canonical stronger packet-export examples keep the same approved ticket/recipient/domain tuple instead of approving bytes in the abstract (`spec/consent.request.schema.json`, `spec/export.receipt.schema.json`, `spec/packet.capture.export.consent.request.profile.schema.json`, `spec/examples/packet.capture.export.consent.request.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, consent, transport, evidence-spine, export-posture, support-handoff, high-risk-approval, risk-register, hygiene, runbook, juicy-lesson, curated-reference, and archive-map docs around that recipient-binding boundary so `consent.request.action.destination`, `transport.receipt.destination`, `transport.acceptance.receipt.recipient`, and `export.receipt.destination` now have to keep the same approved destination tuple for stronger `packet.capture.normalized` export (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/256-consent-ux-contract.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_destination_binding_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_destination_binding_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-09r247

- Keep final stronger packet-capture raw-byte export distinct from mere send success by accepting `adrs/ADR-0108-packet-capture-strong-export-recipient-acceptance-boundary.md`, adding `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, adding `spec/transport.acceptance.receipt.schema.json` plus `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, and tightening the canonical stronger packet-export examples so final `packet.capture.normalized` export now carries `delivery_state = recipient-accepted` plus `transport_acceptance_receipt_digest` instead of stopping at transport success (`spec/transport.acceptance.receipt.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/examples/transport.acceptance.receipt.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, export-posture, support-handoff, risk-register, hygiene, runbook, juicy-lesson, curated-reference, and archive-map docs around that closure boundary so stronger export now joins `transport.acceptance.receipt`, keeps the same normalized digest through recipient acceptance, and only counts as final once the recipient-side lane accepted the artifact (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_acceptance_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_acceptance_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-09r246

- Keep stronger packet-capture raw-byte export digest-stable by accepting `adrs/ADR-0107-packet-capture-strong-export-digest-stability-boundary.md`, adding `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, and tightening the canonical packet-capture stronger-export examples so redaction / import / approval / transport / export receipts now all line up on the same normalized artifact digest instead of disconnected placeholders (`spec/examples/redaction.receipt.packet-capture.json`, `spec/examples/content.import.packet-capture.receipt.json`, `spec/examples/packet.capture.export.consent.request.profile.json`, `spec/examples/packet.capture.export.consent.receipt.profile.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, export-posture, risk-register, hygiene, runbook, juicy-lesson, curated-reference, and archive-map docs around that boundary so `consent.request.action.artifact_digest`, `transport.receipt.artifact.digest`, and `export.receipt.artifact.digest` now have to keep the same normalized digest for stronger `packet.capture.normalized` export (`docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/229-evidence-spine-overview.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_digest_stability_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_digest_stability_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-09r245

- Keep completed stronger packet-capture raw-byte export on the generic transport lane by accepting `adrs/ADR-0106-packet-capture-strong-export-transport-boundary.md`, adding `docs/516-packet-capture-strong-export-transport-boundary.md`, and adding a constrained packet-capture export transport receipt profile/example so completed `packet.capture.normalized` handoff stays transport-bound instead of ending at local-file staging (`spec/packet.capture.export.transport.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`).
- Tighten the packet-capture export, transport, support-handoff, evidence-spine, export-posture, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so stronger `packet.capture.normalized` export now requires `transport_receipt_digest`, rejects `destination.type = file` as completed handoff, and keeps a local save subordinate to the actual receipted transport act (`spec/packet.capture.export.receipt.profile.schema.json`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/229-evidence-spine-overview.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`).
- Add `tools/check_packet_capture_export_transport_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_transport_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-09r244

- Keep stronger packet-capture raw-byte export on the generic consent lane by accepting `adrs/ADR-0105-packet-capture-strong-export-approval-evidence-boundary.md`, adding `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, and adding constrained packet-capture export consent request/receipt profile schemas/examples so stronger `packet.capture.normalized` export binds policy/artifact/lease state, requires secure attention, and uses explicit non-`auto` approval evidence (`spec/packet.capture.export.consent.request.profile.schema.json`, `spec/packet.capture.export.consent.receipt.profile.schema.json`, `spec/examples/packet.capture.export.consent.request.profile.json`, `spec/examples/packet.capture.export.consent.receipt.profile.json`).
- Tighten the packet-capture export, consent, support-handoff, evidence-spine, export-posture, high-risk-approval, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so `packet.capture.normalized` export now requires `consent_receipt_digest` and stronger packet raw-byte export cannot collapse into automatic background uploader folklore (`spec/packet.capture.export.receipt.profile.schema.json`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/256-consent-ux-contract.md`, `docs/229-evidence-spine-overview.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`).
- Add `tools/check_packet_capture_export_approval_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_approval_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-09r243

- Keep stronger packet-capture raw-byte export on the generic export lane by accepting `adrs/ADR-0104-packet-capture-export-proof-chain-and-profile-posture.md`, adding `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, and adding constrained packet-capture export policy/receipt profile schemas/examples so `packet.capture.summary` stays the ordinary export class while `packet.capture.normalized` remains a proof-bound stronger action (`spec/packet.capture.export.policy.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.policy.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the export, packet-capture, support-handoff, evidence-spine, export-posture, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so stronger packet exports carry typed `supporting_evidence` joins back to the session / summary / import / redaction chain instead of collapsing into normalized `.pcapng` folklore (`spec/export.receipt.schema.json`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/229-evidence-spine-overview.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_export_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-09r242

- Make packet-capture participation in support bundles mechanically selectable by accepting `adrs/ADR-0103-packet-capture-evidence-joins-in-incident-bundles.md`, adding `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, and extending the canonical `incident.bundle` include-knob / includes surfaces so packet troubleshooting now joins bundles through typed session/summary/import/redaction receipt digests instead of drifting into `extra` or raw `.pcapng` payload defaults (`spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`, `spec/bundle.plan.schema.json`).
- Tighten the incident-bundle, support-handoff, bundle-plan, evidence-spine, packet-capture, export, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so bundle tooling carries packet-capture proof joins while raw packet bytes remain a stronger separate export action (`docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_bundle_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_bundle_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/420-context-pack.md`).

## 2026-03-09r241

- Keep packet-capture normalization on the archive-wide deterministic redaction lane by accepting `adrs/ADR-0102-packet-capture-normalization-redaction-receipt-boundary.md`, adding `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, and adding constrained packet-capture redaction transform/receipt schemas/examples so stronger imported captures gain typed normalization proof instead of a packet-tool side-effect story (`spec/redaction.transform.packet-capture.schema.json`, `spec/redaction.receipt.packet-capture.schema.json`, `spec/examples/redaction.transform.packet-capture.json`, `spec/examples/redaction.receipt.packet-capture.json`).
- Tighten the packet-capture import, redaction, export, incident-bundle, evidence-spine, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so normalized raw-byte derivatives only become ordinary review/export candidates when the import receipt points at generic redaction evidence ending at `packet-records-only` (`spec/content.import.packet-capture.receipt.schema.json`, `spec/examples/content.import.packet-capture.receipt.json`, `docs/195-deterministic-redaction-transforms.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/266-open-questions-and-risk-register.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_normalization_contract.py`, wire it into `tools/hygiene.py`, refresh the curated-reference surface with the Wireshark `editcap` guide, and regenerate generated discovery/version docs (`tools/check_packet_capture_normalization_contract.py`, `tools/hygiene.py`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-09r240

- Keep stronger packet-capture artifacts on a typed safe-open import lane by accepting `adrs/ADR-0101-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, adding `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, and adding constrained `content.import.*` specialization schemas/examples for packet-capture strong-artifact intake and normalization (`spec/content.import.packet-capture.plan.schema.json`, `spec/content.import.packet-capture.receipt.schema.json`, `spec/examples/content.import.packet-capture.plan.json`, `spec/examples/content.import.packet-capture.receipt.json`).
- Tighten the packet-capture session, summary, export, incident-bundle, evidence-spine, risk-register, runbook, juicy-lesson, hygiene, and archive-map docs around that boundary so foreign or sideband/decryption-bearing captures stay on the safe-open lane and only normalized `packet-records-only` derivatives or `packet.capture.summary` become ordinary promotion/export candidates (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_import_contract.py`, wire it into `tools/hygiene.py`, refresh the curated-reference surface with Wireshark capture-normalization references, and regenerate generated discovery/version docs (`tools/check_packet_capture_import_contract.py`, `tools/hygiene.py`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-09r239

- Keep retained raw packet files subordinate to the typed capture lane by accepting `adrs/ADR-0100-packet-capture-local-artifact-metadata-and-retention-boundary.md`, adding `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, and tightening the canonical `packet.capture.session` / `packet.capture.summary` schemas/examples so local artifacts carry explicit `max_local_retention_seconds`, `metadata_posture`, and `retention_until` state instead of relying on filename/tool folklore.
- Tighten the packet-capture session, summary, export, incident-bundle, evidence-spine, risk-register, runbook, juicy-lesson, hygiene, and archive-map docs around that boundary so Derive-generated raw capture artifacts stay `packet-records-only` by default while stronger sideband/decryption-material cases remain explicit exceptions (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_artifact_contract.py`, wire it into `tools/hygiene.py`, refresh the curated-reference surface with the official pcapng draft, and regenerate generated discovery/version docs (`tools/check_packet_capture_artifact_contract.py`, `tools/hygiene.py`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-08r238

- Keep packet-capture review portable by accepting `adrs/ADR-0099-packet-capture-selector-compiler-boundary.md`, adding `docs/509-packet-capture-selector-compiler-boundary.md`, and introducing the canonical typed `packet.capture.selector` schema/example so `packet.capture.session` carries typed capture intent rather than a backend-specific filter string.
- Tighten the packet-capture session, summary, export, incident-bundle, evidence-spine, risk-register, runbook, hygiene, and archive-map docs around that selector/compiler boundary so backend filter expressions remain compiled detail while typed selectors stay authoritative (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/509-packet-capture-selector-compiler-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_selector_contract.py`, wire it into `tools/hygiene.py`, refresh the juicy-lesson / curated-reference surface, and regenerate the generated discovery/version surfaces (`tools/check_packet_capture_selector_contract.py`, `tools/hygiene.py`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-08r237

- Keep packet capture summary-first without overloading the learned-network lane: accept `adrs/ADR-0098-packet-capture-summary-review-surface-boundary.md`, add `docs/508-packet-capture-summary-review-surface-boundary.md`, and add the canonical typed `packet.capture.summary` schema/example so bounded capture has its own evidence-only review/export surface instead of borrowing `net-flow-summary`.
- Tighten the raw-packet, session, export, incident-bundle, evidence-spine, evidence-posture, tracing, risk-register, hygiene, and runbook docs so `packet.capture.summary` becomes the ordinary capture handoff object while raw packet payload export stays a stronger explicit exception (`docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, `docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/478-evidence-collection-posture-by-profile.md`, `docs/248-tracing-observability-as-evidence.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_summary_contract.py`, wire it into `tools/hygiene.py`, refresh the juicy-lesson / curated-reference surface, and regenerate the generated discovery/version surfaces (`tools/check_packet_capture_summary_contract.py`, `tools/hygiene.py`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-08r236

- Make the raw-packet lane implementable without normalizing `.pcap` folklore: accept `adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md`, add `docs/507-packet-capture-session-and-summary-first-export-boundary.md`, and add the canonical typed `packet.capture.session` schema/example so bounded capture is an authoritative session object with summary-first export by default.
- Tighten the packet-capture, export, incident-bundle, evidence-spine, evidence-posture, risk-register, hygiene, and runbook docs so packet capture stays lease-shaped and raw packet payload export stays an explicit stronger exception rather than the default support workflow (`docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/478-evidence-collection-posture-by-profile.md`, `docs/248-tracing-observability-as-evidence.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_session_contract.py`, wire it into `tools/hygiene.py`, refresh the juicy-lesson / curated-reference surface, and regenerate the generated discovery/version surfaces (`tools/check_packet_capture_session_contract.py`, `tools/hygiene.py`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## 2026-03-08r235

- Fix the raw-packet authority boundary as a narrow cross-profile decision: accept `adrs/ADR-0096-packet-capture-raw-sockets-and-fast-packet-io-boundary.md` and add `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, which separates packet capture / raw sockets / fast packet I/O from ordinary app/service networking and keeps netmap/VALE as a default-off explicit dataplane lane.
- Tighten the egress, diagnostics, BPF-risk, netgraph/netmap, device-authority, risk-register, hygiene, and runbook docs around that boundary so DNS evidence and bounded learn/audit do not quietly fall back to packet-capture folklore (`docs/201-network-egress-as-capability.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`, `docs/384-kernel-extensibility-bpf-and-jit-risk.md`, `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md`, `docs/459-outbound-network-posture-by-profile.md`, `docs/476-device-authority-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Add `tools/check_packet_capture_boundary.py` and wire it into `tools/hygiene.py`, then refresh the juicy-lesson / curated-reference and generated discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## 2026-03-08r234

- Fix the learn/audit network-policy lane as a bounded convergence contract: accept `adrs/ADR-0095-network-learn-audit-convergence-contract.md` and add `docs/505-network-learn-audit-convergence-contract.md`, which makes learn sessions explicitly time- and event-bounded, keeps `net-flow-summary` evidence-only, and preserves `net-egress-policy` as the only authoritative enforcement surface.
- Tighten the existing learned-network-policy, outbound-network, evidence-spine, risk-register, hygiene, and runbook docs around that contract so “observe first” cannot quietly become a standing permissive mode (`docs/328-learned-network-policies-from-flow-receipts.md`, `docs/459-outbound-network-posture-by-profile.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Add a typed `net-flow-summary` artifact plus a lightweight guardrail that keeps bounded-session metadata, canonical digest joins, and doc wiring aligned (`spec/net.flow.summary.schema.json`, `spec/examples/net.flow.summary.json`, `tools/check_learn_net_contract.py`, `tools/hygiene.py`).
- Refresh the juicy-lesson / curated-reference surface with current learn/audit-policy references, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-08r233

- Fix the DNS-evidence privacy/explainability boundary as a profile-shaped contract: accept `adrs/ADR-0094-dns-receipt-detail-and-export-posture-by-profile.md` and add `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`, which keeps `net-flow-receipt` as the normal export/review surface, keeps detailed DNS receipts local-first and bounded, and makes A–D differ mainly in how much qname detail may leave the box.
- Tighten the outbound-network, DNS-mediation, product-profile, telemetry-boundary, and risk-register docs so DNS evidence posture is now a compiled consequence of `network_egress` + `evidence` + `evidence_exports` rather than an open-ended implementation folkway (`docs/459-outbound-network-posture-by-profile.md`, `docs/305-dns-mediation-and-hostname-binding.md`, `docs/411-product-profiles-as-compilation-target.md`, `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`).
- Refresh the juicy-lesson / curated-reference surface with the DNS privacy and qname-minimization research inputs that motivated the narrower posture, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-08r232

- Reduce entropy in the product-profile artifact by accepting `adrs/ADR-0093-no-separate-telemetry-product-profile-key.md`, removing the overlapping `telemetry` default key from the allowlisted vocabulary, and explicitly collapsing observability posture onto `evidence`, `evidence_exports`, and `network_egress` (`docs/503-telemetry-is-not-a-product-profile-default-boundary.md`, `docs/501-product-profile-default-vocabulary-boundary.md`, `spec/product.profile.schema.json`, `spec/examples/product.profiles.json`).
- Tighten the profile core docs and decided product-profile risk item so future telemetry/export work lands on the existing posture surfaces instead of growing a second overlapping review vocabulary, and strengthen `tools/check_profile_default_vocabulary.py` so the removed `telemetry` key cannot quietly come back (`docs/411-product-profiles-as-compilation-target.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `tools/check_profile_default_vocabulary.py`).
- Refresh discovery/version surfaces and archive maps for the tightened profile vocabulary boundary (`docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-08r231

- Accept `adrs/ADR-0092-support-bundle-intake-typed-plan-and-receipt-profiles.md` and turn the official foreign support-bundle intake path into a typed, checkable spec surface by adding `spec/content.import.support-bundle.plan.schema.json` and `spec/content.import.support-bundle.receipt.schema.json`, which constrain the generic import lane for the canonical safe-open workflow without inventing new authority kinds (`docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`, `spec/examples/content.import.support-bundle.plan.json`, `spec/examples/content.import.support-bundle.receipt.json`).
- Tighten the existing support-bundle docs and decided risk item so the typed intake shapes, quarantine-preserving workflow, and timeline-first preview posture are explicit instead of living only in prose examples (`docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`).
- Add `tools/check_support_bundle_import_contract.py`, wire it into `tools/hygiene.py`, and refresh archive guidance/discovery surfaces so the specialized schemas, examples, and docs cannot drift apart silently (`tools/check_support_bundle_import_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-08r230

- Accept `adrs/ADR-0091-product-profile-default-vocabulary-boundary.md` and add `docs/501-product-profile-default-vocabulary-boundary.md` to fix the product-profile default-key boundary: `product.profiles.defaults` stays a flat symbolic compilation-target map, the default-key vocabulary becomes an explicit allowlist, and structured policy remains in dedicated specs instead of a second profile options tree.
- Tighten `spec/product.profile.schema.json` so `defaults` only allows the current stable vocabulary of profile keys, and reframe `docs/411-product-profiles-as-compilation-target.md` plus the risk register so the vocabulary boundary is explicit and no longer an open question (`spec/product.profile.schema.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`).
- Add `tools/check_profile_default_vocabulary.py`, wire it into `tools/hygiene.py`, and refresh archive guidance/discovery surfaces so schema, registry doc, and profile example cannot drift apart silently (`tools/check_profile_default_vocabulary.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`).

## 2026-03-08r229

- Accepted `adrs/ADR-0090-derive-unit-source-compile-receipt-and-runtime-boundary.md` and added `docs/500-derive-unit-source-compile-receipt-and-runtime-boundary.md` to fix the component-runtime source boundary: `derive.unit` is the reviewed source, `runtime.manifest` stays launch authority, `derive.unit.compile.receipt` is evidence-only, and `derive.unit` must choose exactly one runtime-byte source (`rootfs` xor `strata`).
- Added `spec/derive.unit.compile.receipt.schema.json` plus `spec/examples/derive.unit.compile.receipt.json`, tightened `spec/derive.unit.schema.json` and `spec/runtime.manifest.schema.json`, and rewired the canonical component/runtime examples to make the source→compiled joins mechanically checkable.
- Added `tools/check_derive_unit_contract.py`, wired it into `tools/hygiene.py`, and refreshed archive guidance/discovery surfaces (`docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`, generated indexes/context pack).

## 2026-03-07r228

- Fix the fuzzing promotion boundary as a checkable contract: accept an ADR that keeps `fuzz.receipt` evidence-only, makes `crash.case` the canonical minimized replay artifact with explicit reproducibility state, and makes required target classes + open crash-case state the gate surface instead of raw coverage percentages (`adrs/ADR-0089-fuzz-target-classes-and-flake-aware-promotion-boundary.md`, `docs/499-fuzz-target-classes-and-flake-aware-promotion-gate-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Add typed schemas/examples for `fuzz.receipt` and `crash.case`, then thread the decision through the existing fuzzing and bisection docs so flake-aware triage and replayable cases become mechanically representable (`spec/fuzz.receipt.schema.json`, `spec/crash.case.schema.json`, `spec/examples/fuzz.receipt.json`, `spec/examples/crash.case.json`, `docs/274-continuous-fuzzing-farm.md`, `docs/275-root-cause-certificates-and-bisection.md`, `docs/166-test-receipts-and-promotion-gates.md`, `docs/229-evidence-spine-overview.md`).
- Thread that decision into anti-drift product defaults by adding the stable `fuzzing` profile knob plus A/B/C/D notes/invariants, so the archive cannot slide back into one-size-fits-all fuzz gates or coverage-dashboard folklore (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`).
- Add a lightweight guardrail that mechanically checks the fuzz target-class join points and prevents drift across fuzz receipts, crash cases, profile defaults, and the core docs (`tools/check_fuzz_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with current official syzkaller and OSS-Fuzz guidance, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-07r227

- Fix the support-bundle intake boundary as a checkable contract: accept an ADR that keeps foreign support bundles on the safe-open import lane, records the execution boundary in `content.import.plan` / `content.import.receipt`, and stages deeper incident reproduction inside disposable workspaces instead of direct host-open folklore (`adrs/ADR-0088-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the existing content-import lane with a tiny execution contract (`isolation`, `network`, `lifetime`) and canonical support-bundle import examples so timeline-first preview and no-network disposable intake are mechanically representable (`spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`, `spec/examples/content.import.support-bundle.plan.json`, `spec/examples/content.import.support-bundle.receipt.json`).
- Reframe the incident/support, safe-open, origin-label, and replay docs so imported support artifacts stay foreign evidence, preview timeline metadata first, and push reproduction into disposable workspaces (`docs/216-incident-snapshots-and-support-bundles.md`, `docs/220-operational-time-travel-debugging.md`, `docs/267-sanitization-portal-and-disposable-sandboxes.md`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the safe-open support-bundle intake join points and prevents drift across schemas, examples, docs, and the decided risk item (`tools/check_safe_open_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh discovery/version wiring (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-07r225

- Make store retention / garbage collection posture a checkable product-shape decision: accept an ADR that keeps retention profile-shaped, separates soft `keep_generations` preference from hard `rollback_floor_generations`, and makes `store.gc.receipt.rollback_coverage` the compact answer to whether cleanup preserved recovery coverage (`adrs/ADR-0086-store-retention-and-gc-posture-by-profile.md`, `docs/496-store-retention-and-gc-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the existing GC lane by extending `store.gc.plan` / `store.gc.receipt` with rollback-floor / rollback-coverage fields, and by reframing roots/pins, boot-environment, profile, and evidence docs so retention preference stops masquerading as a hard safety floor (`spec/store.gc.plan.schema.json`, `spec/store.gc.receipt.schema.json`, `spec/examples/store.gc.plan.json`, `spec/examples/store.gc.receipt.json`, `docs/175-pins-roots-and-garbage-collection.md`, `docs/404-zfs-boot-environments-as-system-generations.md`, `docs/426-store-gc-plans-and-receipts.md`, `docs/229-evidence-spine-overview.md`, `docs/411-product-profiles-as-compilation-target.md`).
- Thread that decision into anti-drift product defaults by adding the stable `store_retention` profile knob plus A/B/C/D notes/invariants, so the archive cannot slide back into silent rollback-loss or hidden cleanup semantics (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`).
- Add a lightweight guardrail that mechanically checks the store-retention join points and prevents drift across product profiles, GC plan/receipt schemas, rollback coverage example wiring, and the core docs (`tools/check_store_gc_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with current official Nix GC-roots and OpenZFS hold/bookmark pointers, then regenerate generated discovery surfaces and version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-07r224

- Fix the frontend-authoring boundary as a checkable contract: accept an ADR that keeps compiled canonical JSON Spec/policy objects authoritative, makes `frontend.compile.receipt` explicitly evidence-only, and blesses JSON + HuJSON as the in-tree v0 authoring path while richer frontends remain adapter lanes (`adrs/ADR-0085-frontend-source-compile-receipt-and-canonical-ir-boundary.md`, `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Add a typed schema/example for `frontend.compile.receipt`, plus a canonical HuJSON→`trust-policy` example that binds source/compiler provenance to a real compiled output digest (`spec/frontend.compile.receipt.schema.json`, `spec/examples/frontend.compile.receipt.json`, `spec/examples/trust.policy.hujson`, `spec/examples/trust.policy.json`).
- Reframe the frontend / evaluator / evidence docs so source text stays authoring context, compile evidence stays evidence-only, and the blessed in-tree path remains conservative (`docs/79-derive-spec-frontends.md`, `docs/83-evaluator-minimalism.md`, `docs/149-human-policy-hujson-and-canonicalization.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).
- Add a lightweight guardrail that mechanically checks the frontend compile boundary and prevents schema/example drift across the canonical HuJSON source, compile receipt, and compiled trust-policy example (`tools/check_frontend_compile_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r223

- Fix the authority-budget boundary as a checkable contract: accept an ADR that keeps `authority.budget` authoritative, makes `authority.budget.check` explicitly evidence-only, and makes `authority.exception` the authoritative timeboxed field-scoped waiver for the generic component-runtime budget lane (`adrs/ADR-0084-authority-budgets-and-exception-boundary.md`, `docs/494-authority-budget-policy-check-and-exception-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the generic authority-budget lane around that decision by adding typed schemas/examples for `authority.budget`, `authority.budget.check`, and `authority.exception`, and by narrowing the canonical v0 dimension set to filesystem / network / devices / trust / observability instead of silently absorbing every privileged lane (`spec/authority.budget.schema.json`, `spec/authority.budget.check.schema.json`, `spec/authority.exception.schema.json`, `spec/examples/authority.budget.json`, `spec/examples/authority.budget.check.json`, `spec/examples/authority.exception.json`).
- Reframe the authority-budget / descriptor / evidence docs so component-runtime least-authority budgets stop overlapping with kernel-mutation, network-topology, firmware, reset, workload-identity, and operator-session authority lanes (`docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).
- Add a lightweight guardrail that mechanically checks the authority-budget join points, keeps the v0 dimension set stable, and prevents schema/example drift across budget/check/exception artifacts (`tools/check_authority_budget_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r222

- Fix the temporary-authority boundary as a checkable contract: accept an ADR that keeps lane-specific grant / lease / session objects authoritative, makes `lease.issue.receipt` and `lease.use.receipt` explicitly evidence-only, and requires `lease.envelope.target` / `lease.issue.receipt.target` to point at the authoritative temporary-authority object rather than a later action receipt (`adrs/ADR-0083-temporary-authority-grant-lease-and-use-boundary.md`, `docs/493-temporary-authority-grant-lease-and-use-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the generic lease lane around that decision by adding `authority_semantics` to `lease.issue.receipt` and `lease.use.receipt`, rewiring the canonical examples so `lease.envelope` + `lease.issue.receipt` point at `portal-grant`, and moving later action evidence to `lease.use.receipt.related` (`spec/lease.envelope.schema.json`, `spec/lease.issue.receipt.schema.json`, `spec/lease.use.receipt.schema.json`, `spec/examples/portal.grant.json`, `spec/examples/lease.envelope.json`, `spec/examples/lease.issue.receipt.json`, `spec/examples/lease.use.receipt.json`, `spec/examples/export.receipt.json`).
- Reframe the lease / evidence docs so grants, lease joins, issuance evidence, use evidence, and later action receipts stop overlapping (`docs/249-lease-registry-and-cross-lane-revocation.md`, `docs/252-lease-envelope-and-cross-lane-joins.md`, `docs/449-lease-issue-and-use-receipts.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the temporary-authority join points and prevents drift across grant/lease/session authority objects, lease envelopes, lease issue receipts, and lease use receipts (`tools/check_lease_authority_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r221

- Fix attestation result authority as a checkable contract: accept an ADR that keeps `attestation.receipt` explicitly evidence-only, keeps `attestation.admission.policy` as the action→requirement map, and requires authoritative action receipts to summarize attestation decisions via `attestation_verification` instead of treating verifier output as silent authority (`adrs/ADR-0082-attestation-results-evidence-and-admission-issue-boundary.md`, `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the attestation-admission lane around that decision by adding `authority_semantics` to `attestation.receipt`, adding `attestation_verification` summaries to `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt`, and wiring the canonical examples to `attestation.requirement` + `attestation.admission.policy` digests (`spec/attestation.receipt.schema.json`, `spec/secret.receipt.schema.json`, `spec/breakglass.receipt.schema.json`, `spec/workload.identity.issue.receipt.schema.json`, `spec/examples/attestation.requirement.json`, `spec/examples/attestation.admission.policy.json`, `spec/examples/attestation.receipt.json`, `spec/examples/secret.receipt.json`, `spec/examples/breakglass.grant.json`, `spec/examples/breakglass.receipt.json`, `spec/examples/secret.grant.json`, `spec/examples/workload.identity.issue.receipt.json`).
- Reframe the attestation / identity / secrets / recovery docs so verifier evidence, gate policy, and issued authority no longer overlap (`docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/181-workload-identity-and-secretless-deploys.md`, `docs/223-secrets-and-key-management-as-evidence.md`, `docs/236-breakglass-and-recovery-mode.md`, `docs/229-evidence-spine-overview.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the attestation-admission join points and prevents drift across requirements, admission policy, verifier receipts, and consuming authority receipts (`tools/check_attestation_admission_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r220

- Fix vulnerability verification as a checkable contract: accept an ADR that keeps `vuln.query.receipt` deterministic, makes `vuln-gate-receipt` explicitly evidence-only, and binds the optional vulnerability-verification lane to `release.authority.policy` plus a single `vulnerability_verification` summary on publish receipts (`adrs/ADR-0081-vulnerability-verification-evidence-and-publish-gate-boundary.md`, `docs/491-vulnerability-verification-evidence-and-publish-gate-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the vulnerability lane around that decision by adding `authority_semantics` to `vuln-gate-receipt`, wiring vulnerability-verification requirements into `release.authority.policy`, and collapsing publish-time vulnerability joins into `release.publish.receipt.vulnerability_verification` (`spec/vuln.gate.receipt.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/vuln.gate.receipt.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.publish.receipt.json`).
- Reframe the vulnerability / SBOM / VEX / authority docs so query receipts, gate receipts, and publication authority no longer overlap (`docs/60-vulnerability-intel-and-gates.md`, `docs/338-vulnerability-snapshots-query-receipts-and-openvex.md`, `docs/168-sboms-and-vex-as-evidence.md`, `docs/229-evidence-spine-overview.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the vulnerability-verification join points and prevents drift across vuln gate policy, query receipts, gate receipts, release authority policy, and publish receipts (`tools/check_vulnerability_verification_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r219

- Fix witness trust as a checkable contract: accept an ADR that makes `witness.policy` the authoritative roster/quorum/shortfall surface, keeps `log.checkpoint.receipt` evidence-only, and binds witness-policy evaluation to release transparency and release authority without letting monitor config or receipt contents silently redefine trust (`adrs/ADR-0080-witness-policy-and-roster-quorum-boundary.md`, `docs/490-witness-policy-and-roster-quorum-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the transparency lane around that decision by adding typed witness-policy schemas/examples, binding checkpoint receipts to `witness_policy_digest` + `quorum_verdict`, replacing inline witness quorum knobs with `witness_policy_digest` joins in monitor/release authority policy, and extending `release.publish.receipt.transparency_verification` to summarize the pinned witness-policy result (`spec/witness.policy.schema.json`, `spec/examples/witness.policy.json`, `spec/log.checkpoint.receipt.schema.json`, `spec/transparency.monitor.policy.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/log.checkpoint.receipt.json`, `spec/examples/transparency.monitor.policy.json`, `spec/examples/transparency.monitor.snapshot.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.transparency.entry.json`, `spec/examples/release.publish.receipt.json`).
- Reframe the transparency / witness / authority docs so witness networks remain coordination surfaces while witness trust becomes a portable review surface (`docs/257-release-capsules-and-transparency.md`, `docs/259-transparency-monitors-and-witness-gossip.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the witness-policy join points and prevents drift across witness policy, checkpoint receipts, monitor policy, release authority policy, and publish receipts (`tools/check_witness_policy_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r218

- Fix workflow verification as a checkable contract: accept an ADR that keeps `supplychain-layout-policy` as a workflow-constraint policy, makes `supplychain-verify-receipt` explicitly evidence-only, and binds the optional workflow-verification lane to `release.authority.policy` plus a single `supplychain_verification` summary on publish receipts (`adrs/ADR-0079-supplychain-verification-evidence-and-publish-gate-boundary.md`, `docs/489-supplychain-verification-evidence-and-publish-gate-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the supply-chain workflow-verification lane around that decision by adding `authority_semantics` to `supplychain-verify-receipt`, wiring workflow-verification requirements into `release.authority.policy`, and collapsing publish-time workflow joins into `release.publish.receipt.supplychain_verification` (`spec/supplychain.verify.receipt.schema.json`, `spec/supplychain.layout.policy.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/supplychain.verify.receipt.json`, `spec/examples/supplychain.layout.policy.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.publish.receipt.json`).
- Reframe the attestation / workflow / authority docs so provenance, layout verification, verifier summaries, and publication authority no longer overlap (`docs/202-in-toto-layouts-and-step-policy.md`, `docs/71-attestations-dsse-in-toto-slsa.md`, `docs/31-provenance-and-sbom.md`, `docs/229-evidence-spine-overview.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Add a lightweight guardrail that mechanically checks the workflow-verification join points and prevents drift across layout policy, verification receipts, release authority policy, and publish receipts (`tools/check_supplychain_verification_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r217

- Fix release transparency as a checkable contract: accept an ADR that keeps `release.publish.receipt` authoritative, makes `release.transparency.entry` / `log.checkpoint.receipt` / `transparency.monitor.snapshot` explicitly evidence-only, and binds the release-transparency lane to the governing `release.authority.policy` plus a single `transparency_verification` summary on publish receipts (`adrs/ADR-0078-release-transparency-evidence-and-monitor-gate-boundary.md`, `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the release-transparency lane around that decision by removing the vague `policy_digest` field from `release.transparency.entry`, requiring `authority_policy_digest`, adding checkpoint-receipt joins and monitor summary status, and collapsing publish-time transparency joins into `release.publish.receipt.transparency_verification` (`spec/release.transparency.entry.schema.json`, `spec/log.checkpoint.receipt.schema.json`, `spec/transparency.monitor.snapshot.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/release.transparency.entry.json`, `spec/examples/log.checkpoint.receipt.json`, `spec/examples/transparency.monitor.snapshot.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.publish.receipt.json`).
- Reframe the release-authority / transparency docs so publication authority, append-only evidence, witnessed checkpoints, and monitor state no longer overlap (`docs/257-release-capsules-and-transparency.md`, `docs/259-transparency-monitors-and-witness-gossip.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Add a lightweight guardrail that mechanically checks the release-transparency join points and prevents drift across authority policy, transparency entries, checkpoint receipts, monitor snapshots, and publish receipts (`tools/check_release_transparency_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r216

- Fix keyless publisher identity as a checkable contract: accept an ADR that keeps `publisher.identity.receipt` as **identity evidence only**, adds a bundle-first/offline-verification boundary for `sigstore-keyless`, and lets `release.authority.policy` / `release.publish.receipt` carry supplemental identity-evidence rules and decisions without weakening threshold publish authority (`adrs/ADR-0077-keyless-identity-evidence-and-offline-verification-boundary.md`, `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the keyless lane around that decision by updating `publisher.identity.receipt`, `release.authority.policy`, and `release.publish.receipt` schemas/examples so portable keyless evidence binds `sigstore_bundle_digest` + `verification_roots_digest` and publish receipts can explain whether identity evidence was accepted or rejected (`spec/publisher.identity.receipt.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/publisher.identity.receipt.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.publish.receipt.json`, `spec/examples/pki.trust.bundle.json`).
- Reframe the identity / authority docs so publisher identity, bundle-first verification, release authority, and the evidence spine no longer overlap or imply that CI identity is itself release authority (`docs/290-keyless-signing-and-publisher-identity-receipts.md`, `docs/333-sigstore-bundles-and-offline-verification.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Add a lightweight guardrail that mechanically checks the keyless-identity join points and prevents drift across identity receipts, bundle/trust-root bindings, release authority policy, and release publish receipts (`tools/check_keyless_identity_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r215

- Fix execution-integrity authority as a checkable contract: accept an ADR that keeps `exec.integrity.policy` / `exec.integrity.plan` / `exec.integrity.receipt` as the authoritative lane, binds execution-integrity planning to `runtime_manifest_digest` + `stratum_stack_digest` + `mount_view_digest`, keeps `exec-verify-snapshot` / `exec-verify-event` as backend observations, and narrows interpreters/loaders/writable bytes into one operable rule (`adrs/ADR-0076-exec-integrity-authority-and-verified-execution-boundary.md`, `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the verified-exec lane around that decision by updating authoritative plan/receipt schemas/examples, retargeting `exec.verify.policy.diff` to authoritative `exec.integrity.policy` objects, and switching change sets to `apply-exec-integrity` (`spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`, `spec/exec.verify.policy.diff.schema.json`, `spec/examples/exec.integrity.plan.json`, `spec/examples/exec.integrity.receipt.json`, `spec/examples/exec.verify.policy.diff.json`, `spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Reframe the evidence + review docs so policy intent, activation receipts, backend observations, and drift review no longer overlap or contradict each other (`docs/289-exec-integrity-policy-and-verified-execution.md`, `docs/233-verified-execution-as-evidence.md`, `docs/442-exec-verify-policy-diff-as-review-surface.md`, `docs/229-evidence-spine-overview.md`, `docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/97-non-negotiable-behaviors.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the execution-integrity join points and prevents drift across policy/plan/receipt/runtime-composition bindings, change-set ops, and the core docs (`tools/check_exec_integrity_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## 2026-03-07r214

- Make multi-origin runtime composition a checkable contract: accept an ADR that fixes `stratum.manifest` + `stratum.stack` + `mount.view` as the official runtime-composition lane, requires exactly one ABI anchor per stack, forbids silent host-library fallback, and binds runtime manifests/evidence to `stratum_stack_digest` + `mount_view_digest` (`adrs/ADR-0075-stratum-stack-and-runtime-composition-boundary.md`, `docs/485-stratum-stack-and-runtime-composition-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Add typed schemas/examples plus a lightweight guardrail that mechanically checks the runtime-composition join points and prevents drift across strata, compiled mount views, and runtime manifests (`spec/stratum.manifest.schema.json`, `spec/stratum.stack.schema.json`, `spec/mount.view.schema.json`, `spec/examples/stratum.manifest.json`, `spec/examples/stratum.stack.json`, `spec/examples/mount.view.json`, `spec/runtime.manifest.schema.json`, `spec/examples/runtime.manifest.json`, `tools/check_strata_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing runtime-composition docs so mount views, strata, and component/runtime manifests explicitly inherit the accepted boundary instead of leaving multi-origin userlands as folklore (`docs/264-mount-namespaces-and-union-views.md`, `docs/295-strata-and-multi-origin-userlands.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/110-juicy-os-lessons.md`).
- Regenerate discovery/version surfaces and refresh the top-level archive map for the accepted runtime-composition boundary (`docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-07r213

- Make origin-label handling a checkable contract: accept an ADR that fixes `content.origin` as the authoritative provenance object, keeps filesystem quarantine/origin labels pointer-only, and requires `content.import.receipt` to say whether metadata was preserved, rehydrated, cleared-by-policy, or laundering-suspected (`adrs/ADR-0074-origin-label-authority-and-anti-laundering-boundary.md`, `docs/484-origin-label-authority-and-anti-laundering-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the provenance / metadata lane so imports, exports, removable-media ingestion, query/index guidance, and non-negotiable behavior docs explicitly inherit the accepted authority boundary instead of leaving xattr-vs-CAS semantics implicit (`spec/content.import.receipt.schema.json`, `spec/examples/content.origin.json`, `spec/examples/content.import.plan.json`, `spec/examples/content.import.receipt.json`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`).
- Add a lightweight guardrail that mechanically checks the provenance-authority join points and prevents drift across `content.origin`, import receipts, and the new authority doc (`tools/check_content_origin_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official provenance-label / portal / extended-attribute pointers, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-07r212

- Make destructive reprovisioning a checkable contract: accept an ADR that fixes the official destructive reset/reseed lane as `reset.authorization` + `reset.receipt`, bound to `disk.layout.plan`, install payload digests, explicit target selectors, and profile-shaped authority signals instead of vague “signed reset bundles/markers” (`adrs/ADR-0073-destructive-reprovisioning-and-reset-authority.md`, `docs/483-destructive-reprovisioning-and-reset-authority.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `destructive_reprovision` profile knob, tightening the install/recovery and evidence docs to inherit the new boundary, and wiring typed reset artifacts into the archive’s shared install/recovery story (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/309-installation-and-recovery-as-derived-operations.md`, `docs/310-disk-layout-plans-and-receipts.md`, `docs/250-breakglass-and-recovery-workflows.md`, `docs/229-evidence-spine-overview.md`, `docs/473-installation-and-recovery-posture-by-profile.md`).
- Add typed schemas/examples plus a lightweight guardrail that mechanically checks the destructive-reprovision join keys and prevents drift across reset authorization, reset receipts, disk-layout evidence, and profile defaults (`spec/reset.authorization.schema.json`, `spec/reset.receipt.schema.json`, `spec/examples/reset.authorization.json`, `spec/examples/reset.receipt.json`, `tools/check_reset_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official Chromium OS recovery / developer-mode physical-presence lessons, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-07r211

- Make boot code admission a checkable contract: accept an ADR that binds `boot.manifest`, `boot.override.policy`, `boot.override.receipt`, `boot.attestation`, and `kmod.load.plan` / `kmod.load.receipt` into one constrained kernel-code admission story, and limit normal mutable boot overrides to `next-entry`, `boot-mode`, and `console-profile` (`adrs/ADR-0072-boot-code-admission-and-constrained-overrides.md`, `docs/482-boot-code-admission-and-constrained-overrides.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the boot + kernel-mutation lane so manifests carry policy digests, attestation exposes verified digests, kmod plan/receipt examples bind back to `boot_manifest_digest`, and the existing loader/manifest docs explicitly inherit the accepted boundary (`spec/boot.manifest.schema.json`, `spec/boot.attestation.schema.json`, `spec/kmod.load.plan.schema.json`, `spec/kmod.load.receipt.schema.json`, `spec/boot.override.policy.schema.json`, `spec/boot.override.receipt.schema.json`, `spec/examples/boot.manifest.json`, `spec/examples/boot.attestation.json`, `spec/examples/kmod.load.plan.json`, `spec/examples/kmod.load.receipt.json`, `spec/examples/boot.override.policy.json`, `spec/examples/boot.override.receipt.json`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/277-loader-verification-and-boot-config-constraints.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/284-bootenv-switching-as-evidence.md`, `docs/229-evidence-spine-overview.md`).
- Add a lightweight guardrail that mechanically checks the boot-admission join keys and prevents example/schema drift across manifest, override, attestation, and kmod receipts (`tools/check_boot_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons and regenerate discovery/version surfaces for the accepted boot boundary (`docs/110-juicy-os-lessons.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r210

- Make the human-scale debugging handoff contract explicit: accept an ADR that fixes the official support handoff as `incident.timeline` + `incident.bundle` + `bundle.plan` + `bundle.payload.manifest` + `bundle.build.receipt`, keeps `tar.zst` as the canonical payload format, and keeps `zip` as an explicit compatibility adapter (`adrs/ADR-0071-support-bundle-contract-and-timeline-first-handoff.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten incident/support bundle docs and examples so the default handoff is timeline-first and digest-bound instead of a mystery tarball (`docs/216-incident-snapshots-and-support-bundles.md`, `docs/419-incident-timelines-as-derived-artifacts.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/229-evidence-spine-overview.md`, `spec/incident.bundle.schema.json`, `spec/bundle.build.receipt.schema.json`, `spec/examples/incident.bundle.json`, `spec/examples/bundle.build.receipt.json`, `spec/examples/bundle.payload.manifest.json`).
- Add a lightweight guardrail that keeps the official support handoff contract wired and prevents example/schema drift on timeline-first support bundles (`tools/check_support_bundle_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with current official support-bundle / diagnostics pointers, then regenerate discovery surfaces and version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r209

- Make trust-bundle posture a checkable product-shape decision: accept an ADR that keeps fleet trust roots purpose-scoped and diff-gated with shadow trust blocking in official lanes, keeps workstation extra roots visible and trusted-UI-mediated, keeps general-OS system trust preferred with explicit local override, and makes fixed-purpose offline/strongly-approved trust bundles the production default for factory/regulatory shapes (`adrs/ADR-0070-trust-bundle-posture-by-profile.md`, `docs/480-trust-bundle-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `trust_bundles` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into invisible workstation root injection, app-shipped shadow trust in official fleet lanes, or ad-hoc live production CA edits (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing trust-bundle lane docs so artifact, shadow-trust, and trust-bundle-diff guidance explicitly inherit the new A/B/C/D boundary instead of leaving trust-store posture implicit (`docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/327-shadow-trust-and-system-ca-governance.md`, `docs/434-pki-trust-bundle-diff-as-review-surface.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official p11-kit trust-module, SPIFFE trust-bundle, FreeBSD `certctl`, and cert-manager trust-manager pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r208

- Make hardware-compatibility posture a checkable product-shape decision: accept an ADR that keeps fleet preflight blocking and cohort-aware for boot-critical/remote-management-floor failures, keeps workstation boot-floor failures trusted-UI-blocking with explicit consent for warnings, keeps general-OS preflight preferred with explicit override, and makes approved-hardware admission the production default for factory/regulatory shapes (`adrs/ADR-0069-hardware-compatibility-posture-by-profile.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `hardware_compatibility` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into blind fleet switches, surprise workstation hardware regressions, or faux-supported factory bundles (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing hardware inventory / compatibility docs so inventory refresh, preflight strength, and support-claim semantics explicitly inherit the new A/B/C/D boundary instead of leaving gate strength implicit (`docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official FreeBSD device-inspection/devmatch, systemd hwdb, fwupd hardware-ID, and Fuchsia driver-binding pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r207

- Make network-topology posture a checkable product-shape decision: accept an ADR that keeps fleet host topology activation-first and commit-confirmed with maintenance leases, keeps workstation risky host-topology changes trusted-UI-visible and rollbackable, keeps general-OS derived networking preferred with explicit local-admin fallback, and keeps production topology sealed/offline-windowed for factory/regulatory shapes (`adrs/ADR-0068-network-topology-posture-by-profile.md`, `docs/477-network-topology-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `networking` profile knob for B/C/D, sharpening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into remote-brick shell folklore, silent workstation exposure drift, or ad-hoc live production topology edits (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing host-networking docs so topology, substrate mapping, and authority-budget guidance explicitly inherit the new A/B/C/D boundary instead of leaving host-topology mutation implicit (`docs/322-network-topology-and-firewall-as-derived-operations.md`, `docs/64-networking-modes-mapping.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official FreeBSD networking, systemd-networkd, Junos commit-confirmed, and OpenWrt UCI rollback pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r206

- Make evidence-collection posture a checkable product-shape decision: accept an ADR that keeps fleet evidence bounded but always on, keeps workstation evidence locally useful and user-exportable without ambient support telemetry, keeps general-OS local retention viable without hidden collector dependencies, and makes bundled/redacted evidence the production default for factory/regulatory shapes (`adrs/ADR-0067-evidence-collection-posture-by-profile.md`, `docs/478-evidence-collection-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by tightening A–D evidence notes/invariants/forbidden lanes, adding the stable `evidence` profile knob for C, and extending the product-profile guardrail so the archive cannot drift back into hidden collector dependencies, ambient workstation telemetry, or faux-redacted factory evidence posture (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing evidence lanes so the evidence spine, structured event log, support bundles, inspect-style diagnostics, and flight recorder docs explicitly inherit the new A/B/C/D boundary instead of leaving collection posture implicit (`docs/229-evidence-spine-overview.md`, `docs/215-structured-event-log-as-evidence.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/302-structured-diagnostics-inspect-trees.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official OpenTelemetry, systemd, Fuchsia diagnostics, and Red Hat `sos report` pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r205

- Make device-authority posture a checkable product-shape decision: accept an ADR that keeps fleet service compartments compiled-minimal and lease-expanded, keeps workstation raw sensitive devices in the trusted host with portal-first app access, preserves explicit raw-device compatibility fallback for general-OS viability, and makes compiled-minimal sealed device authority the production default for factory/regulatory shapes (`adrs/ADR-0066-device-authority-posture-by-profile.md`, `docs/476-device-authority-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `device_authority` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into ambient raw-device authority for fleet/workstation shapes or faux-sealed production device posture (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing device-authority lanes so device grants and devfs-view docs explicitly inherit the new A/B/C/D boundary instead of leaving raw device-node posture implicit (`docs/278-device-grants-and-devfs-rulesets.md`, `docs/323-devfs-views-plans-and-receipts.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official FreeBSD jails/devfs and Qubes device-security pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r204

- Make kernel-mutation posture a checkable product-shape decision: accept an ADR that keeps fleet kernel mutation activation-first and maintenance-leased, keeps workstation risky host-kernel mutation trusted-UI-visible, preserves explicit local-admin fallback for general-OS viability, and makes preload-only plus lockdown the production default for factory/regulatory shapes (`adrs/ADR-0065-kernel-mutation-posture-by-profile.md`, `docs/475-kernel-mutation-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `kernel_mutation` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into ambient runtime sysctl folklore, silent workstation host mutation, or faux-lockdown production claims (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing kernel-mutation lanes so sysctls, kmods, lockdown, and drift surfaces explicitly inherit the new A/B/C/D boundary instead of leaving runtime mutation posture implicit (`docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/230-lockdown-levels-and-securelevel.md`, `docs/429-sysctl-diff-as-drift-surface.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official FreeBSD/OpenBSD securelevel, sysctl, and module-path pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r203

- Make high-risk approval posture a checkable product-shape decision: accept an ADR that keeps fleet shared-trust mutations digest-bound/role-separated/quorum-shaped by default, keeps workstation personal-risk actions trusted-UI user-consent-first, keeps general-OS single-principal local-admin viability without hidden reviewer dependencies, and requires offline/OOB-capable role-separated quorum for factory/regulatory production mutations (`adrs/ADR-0064-high-risk-approval-posture-by-profile.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `high_risk_approvals` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into requester-self-approval for fleet/factory shared-trust mutations or reviewer-theater defaults for workstation/general-OS basics (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing approval lanes so two-person integrity, multiparty approvals, and release authority explicitly inherit the new A/B/C/D boundary instead of leaving quorum posture implicit (`docs/107-two-person-integrity.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`, `docs/260-release-authority-policy-and-key-management.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official TUF, Uptane, Vault control-group, and GitHub deployment-protection pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r202

- Make installation-and-recovery posture a checkable product-shape decision: accept an ADR that keeps fleet install/recovery target-device-bound and additive by default, keeps workstation destructive storage changes trusted-UI-guided and encrypted-root-first, keeps general-OS guided/classic install choice explicit, and requires target-bound offline-capable recovery plus signed reset authority for factory/regulatory shapes (`adrs/ADR-0063-installation-and-recovery-posture-by-profile.md`, `docs/473-installation-and-recovery-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `installation_recovery` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into wrong-disk automation, surprise workstation wipes, hidden destructive compatibility paths, or ad-hoc factory reset folklore (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing install/recovery lanes so the shared workflow docs explicitly inherit the new A/B/C/D boundary instead of leaving destructive authority and recovery-media expectations implicit (`docs/309-installation-and-recovery-as-derived-operations.md`, `docs/310-disk-layout-plans-and-receipts.md`, `docs/360-derived-recovery-images-and-minimal-userspace.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official OpenBSD `bsd.rd`, FreeBSD `bsdinstall`, systemd-repart, and ZFSBootMenu install/recovery pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r201

- Make update-delivery and release posture a checkable product-shape decision: accept an ADR that keeps fleet updates health-gated and rollout-shaped, keeps workstation apply/reboot trusted-UI-visible and deferrable, keeps general-OS transactional viability free of hidden coordinator requirements, and requires approved offline bundles or mirror kits with quarantine→promote as the factory/regulatory production default (`adrs/ADR-0062-update-delivery-and-release-posture-by-profile.md`, `docs/472-update-delivery-and-release-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by tightening A–D update notes/invariants/forbidden lanes and extending the product-profile guardrail so the archive cannot slide back into surprise workstation host updates, coordinator-dependent general-OS viability, opaque fleet updater folklore, or online-only factory delivery paths (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing update lanes so health-gated updates, rollout/assignment guidance, offline bundles, air-gap mirror kits, and channel lessons explicitly inherit the new A/B/C/D delivery boundary instead of leaving profile defaults implicit (`docs/112-health-gated-updates.md`, `docs/177-fleet-coordinated-rollouts.md`, `docs/138-offline-signed-update-bundles.md`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/89-update-channel-lessons-freebsd-update.md`).
- Refresh juicy lessons with the accepted boundary so “bytes authority vs rollout/assignment/finalization vs offline carrier” stays discoverable and amnesia-resistant (`docs/110-juicy-os-lessons.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r200

- Make firmware-update posture a checkable product-shape decision: accept an ADR that keeps fleet firmware mutation policy-gated and maintenance-shaped, keeps workstation firmware apply trusted-UI-visible and consent-first, keeps general-OS firmware handling user-choice with explicit adapters, and requires offline-staged firmware workflows for factory/regulatory shapes by default (`adrs/ADR-0061-firmware-update-posture-by-profile.md`, `docs/471-firmware-update-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by sharpening A–D firmware notes/invariants/forbidden lanes and extending the product-profile guardrail so the archive cannot slide back into fleet updater folklore, silent workstation firmware changes, or online-only factory firmware paths (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing firmware lane docs so platform-provenance and capsule guidance explicitly inherit the new product-shape default instead of leaving A/B/C/D posture implicit (`docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`, `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`, `docs/221-firmware-updates-as-artifacts.md`).
- Refresh firmware lessons + curated references with the accepted boundary and current official UEFI 2.11 / LVFS / NIST firmware-resiliency pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r199

- Make workload-identity / credential-issuance posture a checkable product-shape decision: accept an ADR that keeps fleet service identity short-lived/digest-bound and headless, keeps workstation AppVM/dev-service identity separate from human login/account authority, keeps general-OS static-token flows adapter-shaped, and forbids shipped static shared production secrets in factory/regulatory shapes by default (`adrs/ADR-0060-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/470-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `workload_identity` profile knob, sharpening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into token sprawl, human/workload identity confusion, or shipped production shared secrets (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing identity lane docs so workload identity, PKI lifecycle, and dynamic service identity explicitly inherit the new product-shape default instead of leaving A/B/C/D posture implicit (`docs/181-workload-identity-and-secretless-deploys.md`, `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/240-dynamic-service-identities.md`).
- Refresh workload-identity lessons + curated references with the accepted boundary and current official SPIFFE/SPIRE, Kubernetes bound-token, and Vault dynamic-credential pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r198

- Make platform-provenance / attestation-admission posture a checkable product-shape decision: accept an ADR that keeps fleet measured posture receipted and available for sensitive admissions, keeps workstation posture visible/exportable without making remote attestation a surprise hard dependency for ordinary local use, keeps general-OS attestation optional/exportable with explicit gates, and requires retained measured posture for production/factory-sensitive admissions by default (`adrs/ADR-0059-platform-provenance-and-attestation-admission-posture-by-profile.md`, `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by refining the stable `platform_provenance` profile knob, sharpening A–D notes/invariants, and extending the product-profile guardrail so the archive cannot slide back into attestation theater, verifier-dependent workstation breakage, or production evidence-without-gating (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing attestation lane docs so evidence, admission policy, and admission-policy diffs explicitly inherit the new product-shape default instead of leaving A/B/C/D posture implicit (`docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`).
- Refresh attestation lessons + curated references with the accepted boundary and current official measured-boot / Keylime / Trusted Launch pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r197

- Make trustworthy-time posture a checkable product-shape decision: accept an ADR that requires authenticated quorum/LKGT posture for fleet expiry-sensitive gates, makes workstation degraded time visible and gates sensitive actions, keeps authenticated time preferred with explicit fallback in general OS, and requires bounded offline signed-time or authenticated-quorum bootstrap for factory/regulatory shapes (`adrs/ADR-0058-trustworthy-time-posture-by-profile.md`, `docs/468-trustworthy-time-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `time_authority` profile knob, refining A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into silent unauthenticated time fallback or airgap-time waiver folklore (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing trustworthy-time lane so the BSD-friendly backend doc explicitly inherits the new product-shape default instead of leaving fleet/workstation/factory posture implicit (`docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`).
- Refresh time lessons + curated references with the accepted boundary and current official NTS / Roughtime pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r196

- Make operator-access posture a checkable product-shape decision: accept an ADR that keeps fleet operator access JIT/certificate-based and role-shell-first, makes workstation admin local-presence-first with remote shell admin exceptional, keeps general-OS static-key remote admin adapter-shaped, and forbids standing vendor/admin keys in factory/regulatory images by default (`adrs/ADR-0057-operator-access-posture-by-profile.md`, `docs/467-operator-access-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `operator_access` profile knob, refining A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into permanent bastions, standing workstation remote admin, or shipped factory maintenance keys (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing operator-access lane so the headless SSH/role-shell doc explicitly inherits the new product-shape default instead of leaving workstation/general-OS/factory posture implicit (`docs/311-operator-access-leases-and-ssh-certs.md`).
- Refresh operator-access lessons + curated references with accepted posture and current official SSH-cert / doas / session-recording pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r195

- Make export-boundary posture a checkable product-shape decision: accept an ADR that keeps fleet evidence export brokered/ticketed/encrypted, makes workstation sharing recipient-visible and redaction-aware, keeps general-OS adapter fallback explicit, and requires minimal redacted strongly approved export for factory/regulatory shapes (`adrs/ADR-0056-export-boundary-posture-by-profile.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `evidence_exports` profile knob, refining A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into ambient upload folklore or invisible remembered support export authority (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing export lane so the portal + diff docs explicitly inherit the product-shape default instead of leaving approval severity purely implicit (`docs/251-export-policies-and-support-bundle-portal.md`, `docs/433-export-policy-diff-as-review-surface.md`).
- Refresh export lessons + curated references with the accepted boundary and current official support/export pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r194

- Make data-at-rest posture a checkable product-shape decision: accept an ADR that encrypts mutable state by default for fleet hosts, makes lost-device/login-bounded user state the workstation default, keeps encryption preferred with explicit compatibility fallback for general OS, and requires encrypted production state plus attested/quorum maintenance unlock for factory/regulatory shapes (`adrs/ADR-0055-data-at-rest-posture-by-profile.md`, `docs/465-data-at-rest-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `data_at_rest` profile knob, refining A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into image-baked unlock secrets or ambient workstation auto-unlock (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing ZFS encryption lane so substrate capability does not masquerade as product policy: file/URL key locations stay adapter territory unless mediated by explicit broker/evidence workflow (`docs/409-zfs-encryption-and-key-management.md`).
- Refresh encryption/home-state lessons + curated references so the accepted boundary stays discoverable and current (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Close the remaining schema/example coverage hole for portable-home, AppVM-storage, and restore artifacts so `check_spec_example_coverage.py` stays green (`spec/examples/home.attach.receipt.json`, `spec/examples/home.unlock.receipt.json`, `spec/examples/home.lock.receipt.json`, `spec/examples/appvm.storage.plan.json`, `spec/examples/appvm.storage.receipt.json`, `spec/examples/restore.plan.json`, `spec/examples/restore.receipt.json`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r193

- Make backup / restore posture a checkable product-shape decision: accept an ADR that treats fleet hosts as replaceable state-replication systems, keeps workstation recovery explicit via exports or home replication, leaves general-OS backup choice open, and requires replication plus restore drills for factory/regulatory shapes (`adrs/ADR-0054-backup-and-restore-posture-by-profile.md`, `docs/464-backup-and-restore-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Turn that decision into anti-drift product defaults by refining the stable `backups` profile knob, wiring backup/recovery notes + invariants into A–D, and extending the profile guardrail so recovery posture cannot quietly slide back into full-host image folklore or mystery sync (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh backup/recovery wiring, juicy lessons, and curated references so the accepted boundary stays discoverable and current (`docs/316-backups-and-restores-as-derived-operations.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`, `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Close an existing hygiene hole by adding the missing portable-home, AppVM-storage, and restore artifact schemas named by the archive (`spec/home.attach.receipt.schema.json`, `spec/home.unlock.receipt.schema.json`, `spec/home.lock.receipt.schema.json`, `spec/appvm.storage.plan.schema.json`, `spec/appvm.storage.receipt.schema.json`, `spec/restore.plan.schema.json`, `spec/restore.receipt.schema.json`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r192

- Make human identity / home-state posture a checkable product-shape decision: accept an ADR that keeps fleet hosts on operator-account defaults, makes portable login-mounted homes the workstation default, keeps whole-home AppVM mounts exceptional, preserves host-account compatibility in general OS, and keeps production/factory identities separate (`adrs/ADR-0053-human-identity-and-home-state-posture-by-profile.md`, `docs/463-human-identity-and-home-state-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Reduce entropy in the product profile artifact by replacing the workstation-only `portable_homes` knob with a stable cross-profile `home_identity` default, refine profile invariants/forbidden lanes, and extend the product-profile guardrail so home-state drift is caught mechanically (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh portable-home/AppVM-storage wiring and current references so the accepted boundary stays discoverable (`docs/269-portable-home-areas-and-user-records.md`, `docs/270-appvm-storage-private-volatile-and-home-areas.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `docs/420-context-pack.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r191

- Make private-key / crypto-operation posture a checkable product-shape decision: accept an ADR that keeps fleet key use headless and brokered, workstation key use presence-gated and vault-preferred, general-OS compatibility explicit/adapter-shaped, and appliance/factory key use offline-or-quorum by default (`adrs/ADR-0052-private-key-and-crypto-op-posture-by-profile.md`, `docs/462-private-key-and-crypto-op-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into the product profile artifact by adding a stable `private_keys` default, refining profile invariants/forbidden lanes, and letting generated profile/context surfaces summarize the new posture (`spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`).
- Extend the product-profile guardrail so private-key posture drift is caught mechanically, and refresh crypto-lane/runbook/reference wiring with current split-key / keystore pointers (`tools/check_product_profiles.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/306-crypto-operations-portal-and-split-keys.md`, `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `docs/420-context-pack.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r190

- Make remote assistance a checkable product-shape decision: accept an ADR that keeps fleet support operator/TTY-shaped, workstation support visible and secure-attention-gated for control, general-OS support explicit/leased, and appliance support absent by default outside maintenance-shaped workflows (`adrs/ADR-0051-remote-assistance-posture-by-profile.md`, `docs/461-remote-assistance-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into the product profile artifact by adding a stable `remote_assistance` default, refining profile invariants/forbidden lanes, and letting generated profile/context surfaces summarize the new posture (`spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`).
- Extend the product-profile guardrail so remote-assistance posture drift is caught mechanically, refresh remote-assistance/current-reference wiring, and normalize duplicated tail numbering in the risk register (`tools/check_product_profiles.py`, `docs/291-remote-assistance-sessions-as-evidence.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `docs/420-context-pack.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `CHANGELOG.md`).

## 2026-03-06r189

- Make inbound exposure a checkable product-shape decision: accept an ADR that keeps listener exposure brokered across A–D, makes loopback the low-friction default, and allows trusted-UI consent for non-local exposure only where a human product shape exists and the approval lands in a lease or durable policy object (`adrs/ADR-0050-inbound-listen-posture-by-profile.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into the product profile artifact by adding a stable `network_ingress` default, refining profile invariants/forbidden lanes, and letting generated profile/context surfaces summarize the new posture (`spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`).
- Extend the product-profile guardrail so inbound-listen posture drift is caught mechanically, and refresh listen-broker wiring + current references/lessons (`tools/check_product_profiles.py`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `docs/420-context-pack.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r188

- Make outbound network posture a checkable product-shape decision: accept an ADR that keeps egress brokered across A–D, allows interactive consent only where the product shape includes a human, and requires hostname-based policy to use brokered DNS for the governed lane (`adrs/ADR-0049-outbound-network-posture-by-profile.md`, `docs/459-outbound-network-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into the product profile artifact by adding stable `network_egress` + `dns_resolution` defaults, refining profile invariants/forbidden lanes, and letting generated profile/context surfaces summarize the new posture (`spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`).
- Extend the product-profile guardrail so outbound-network / DNS posture drift is caught mechanically, and refresh juicy lessons + curated references with current networking-policy pointers (`tools/check_product_profiles.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `docs/420-context-pack.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `README.md`).

## 2026-03-06r187

- Make removable-media / USB posture a checkable product-shape decision: accept an ADR that bans trusted-plane automount by default, keeps removable media quarantine-first across A–D, and makes per-profile USB-isolation stance explicit without pretending every hardware edge case is solved (`adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`, `docs/458-removable-media-and-usb-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread the decision into the product profile artifact by adding stable `removable_media` + `usb_isolation` defaults, refining profile invariants/forbidden lanes, and letting generated profile/context surfaces summarize the new posture (`spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`).
- Extend the product-profile guardrail so removable-media / USB drift is caught mechanically, and refresh juicy lessons + curated references with the explicit local-policy fallback lesson (`tools/check_product_profiles.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-06r186

- Make the workstation runtime boundary explicit instead of aspirational: accept an ADR that keeps profile **B** host execution scoped to trusted UI/brokers while general interactive apps are **AppVM-first**, and capture the boundary in a focused wiring doc (`adrs/ADR-0047-workstation-host-ui-and-appvm-boundary.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/268-desktop-appvms-and-portalized-apps.md`).
- Turn that decision into a checkable compilation-target default: refine the workstation product profile runtime posture, forbid host-side general app execution by default, mark the desktop stance risk item as decided, and narrow the remaining open question to implementation details (`spec/examples/product.profiles.json`, `docs/266-open-questions-and-risk-register.md`).
- Add a profile-drift guardrail so B cannot silently regress back into an ambiguous host-app model (`tools/check_product_profiles.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with the accepted workstation boundary and current Qubes GUI virtualization pointer, then refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r185

- Eliminate spec-example drift warnings by validating long-lived *variant* examples via thin wrapper schemas: add `microvm.stop.plan.force` and `microvm.stop.receipt.denied` wrapper schemas that `$ref` the base stop plan/receipt contracts and pin the example semantics (keeps the core surface stable while making variants mechanically checkable) (`spec/microvm.stop.plan.force.schema.json`, `spec/microvm.stop.receipt.denied.schema.json`, `spec/examples/microvm.stop.plan.force.json`, `spec/examples/microvm.stop.receipt.denied.json`, `docs/98-archive-hygiene.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r184

- Stabilize the microVM lifecycle “why” surface by centralizing the v0 reason-code vocabulary in a registry doc, capturing the governance rule in an accepted ADR, and adding a hygiene guardrail that prevents example receipts from inventing ad-hoc reason codes (`docs/456-microvm-receipt-reason-code-registry.md`, `adrs/ADR-0046-microvm-reason-code-registry.md`, `tools/check_microvm_reason_code_registry.py`, `tools/hygiene.py`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/99-llm-runbook.md`).
- Add a denied stop example receipt that demonstrates the two-code pattern (`denied-by-policy` + `force-stop-denied`) and is mechanically constrained by the registry guardrail (`spec/examples/microvm.stop.plan.force.json`, `spec/examples/microvm.stop.receipt.denied.json`).
- Refresh curated references with concrete stable-vocabulary cues (gRPC status codes; systemd symbolic exit-status names) and extend juicy lessons so the registry remains discoverable (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r183

- Make microVM lifecycle receipts operationally deterministic: require non-empty `reasons[]` with stable `reasons[].code` on non-success outcomes (denied/failed/timeout), capture the rule as an accepted ADR, enforce it in the microVM receipt schemas, and add a hygiene guardrail so it can’t drift back into log-only folklore (`adrs/ADR-0045-microvm-receipt-reason-codes.md`, `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`, `tools/check_microvm_receipt_reason_requirements.py`, `tools/hygiene.py`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/110-juicy-os-lessons.md`, `docs/99-llm-runbook.md`).
- Refresh curated references with high-signal cues for structured, machine-readable error details and stable reason-code vocabularies, then refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/32-curated-references.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r182

- Make microVM launches more forensic and spec-able by recording attached host↔guest IO crossings in the receipt: add `assigned.io_channels` (vsock/virtio-console/nmdm/stdio) and update the example receipt (keeps runtime crossings queryable for incident bundles) (`spec/microvm.launch.receipt.schema.json`, `spec/examples/microvm.launch.receipt.json`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/110-juicy-os-lessons.md`).
- Capture the IO-channel evidence rule as an accepted ADR so A–D behavior doesn't drift into log-only folklore (`adrs/ADR-0044-microvm-io-channels-in-receipts.md`).
- Refresh curated references with concrete vsock semantics pointers and regenerate generated discovery surfaces; refresh wiring/version stamps (`docs/32-curated-references.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r181

- Make microVM Plan→Receipt digests unambiguous and implementable: define `plan_digest = sha256(utf8(JCS(plan)))` and capture the rule in an ADR; update the microVM lifecycle wiring doc and receipt schema descriptions to match (`adrs/ADR-0043-microvm-plan-digest-sha256.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`).
- Add a drift guardrail: `tools/check_microvm_example_plan_digests.py` verifies example receipt `plan_digest` values match computed sha256(JCS(plan)), and update the example plan/receipt pairs to use real sha256 digests and consistent cross-links (`spec/examples/microvm.launch.plan.json`, `spec/examples/microvm.launch.receipt.json`, `spec/examples/microvm.stop.plan.json`, `spec/examples/microvm.stop.receipt.json`, `tools/hygiene.py`).
- Refresh curated references with RFC 8785 JCS implementation pointers and extend juicy lessons with a durable “content identity must be checkable” rule of thumb; refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `docs/99-llm-runbook.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r180

- Make microVM stop **spec-able** by introducing `microvm.stop.plan` + `microvm.stop.receipt` (schemas + examples) and wiring stop into the `derive-vmmd` control-plane contract and the evidence spine so terminations are auditable and queryable (`spec/microvm.stop.plan.schema.json`, `spec/examples/microvm.stop.plan.json`, `spec/microvm.stop.receipt.schema.json`, `spec/examples/microvm.stop.receipt.json`, `docs/29-vm-control-plane.md`, `docs/229-evidence-spine-overview.md`, `docs/455-microvm-launch-plans-and-receipts.md`).
- Decide conservative stop semantics that keep A–D coherent: bounded `graceful` vs explicit `force`, idempotent `already-stopped`, and optional `expect_running_plan_digest` safety guard (`adrs/ADR-0042-microvm-stop-semantics.md`, `docs/455-microvm-launch-plans-and-receipts.md`).
- Extend juicy lessons + curated references so “no silent kills” and backend stop primitives stay discoverable, then refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r179

- Decide strict microVM launch idempotency so retries are safe and A–D behavior does not fork: on a host, `derive-vmmd` is strict-idempotent by `(instance_id, plan_digest)`; digest changes under the same identity are denied (replacement becomes explicit future Plan→Receipt work) (`adrs/ADR-0041-microvm-instance-idempotency.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/29-vm-control-plane.md`).
- Add a juicy lesson that makes “no surprise restarts” a stable rule of thumb for fleets and workstations (`docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r178

- Make microVM launch behavior spec-able by introducing a digest-bound Plan→Receipt join key: `microvm.launch.plan` + `microvm.launch.receipt` (schemas + examples) and a tight wiring doc for `derive-vmmd` (`docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.launch.plan.schema.json`, `spec/examples/microvm.launch.plan.json`, `spec/microvm.launch.receipt.schema.json`, `spec/examples/microvm.launch.receipt.json`).
- Wire launch receipts into the evidence spine and control-plane invariants, and add a juicy lesson that makes “launch is evidence (even on denial)” a stable rule of thumb (`docs/229-evidence-spine-overview.md`, `docs/29-vm-control-plane.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## 2026-03-04r177

- Make a hard, scope-preserving decision about the microVM orchestration boundary: DeriveBSD ships a **host-local** microVM enforcement plane (verify → enforce → receipt) and treats distributed scheduling as an external, killable adapter concern (`adrs/ADR-0040-microvm-orchestration-host-local.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`).
- Add an amnesia-resistor convention for the risk register: tag decided items with **[DECIDED]** and exclude them from generated “top open questions” surfaces; update generators accordingly and add a warning check to keep decided items pinned to ADRs (`tools/gen_context_pack.py`, `tools/gen_risk_register_index.py`, `tools/check_open_questions_decisions.py`, `tools/hygiene.py`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r176

- Add a killable ecosystem interop lane for standard attestations by documenting an in-toto/SLSA export adapter and introducing a typed export report artifact: `attestation.adapter.intoto.report` (schema + example) (keeps DeriveBSD receipts as the source of truth while enabling downstream verifier tooling) (`docs/454-intoto-slsa-adapter-lane.md`, `spec/attestation.adapter.intoto.report.schema.json`, `spec/examples/attestation.adapter.intoto.report.json`).
- Wire the new lane into adapter discipline, the evidence spine, juicy lessons, and curated references (add current SLSA v1.2 pointers) so the interop remains discoverable, killable, and amnesia-resistant (`docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r175

- Make Capsicum capability-set drift mechanically reviewable by introducing typed preopen map artifacts and a compact diff surface: `preopen.map` + `preopen.map.diff` (schemas + examples) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/453-preopen-map-diff-as-review-surface.md`, `spec/preopen.map.schema.json`, `spec/examples/preopen.map.json`, `spec/preopen.map.diff.schema.json`, `spec/examples/preopen.map.diff.json`).
- Wire `preopen.map.diff` into the canonical diff surface registry, drift bundle posture guidance, and the evidence spine so “what handles/rights changed?” stays explainable and gateable without forks; refresh Capsicum launcher + component descriptor docs with schema pointers (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`).
- Extend the canonical risk-flag vocabulary with stable preopen-map drift reason codes and refresh curated references with core Capsicum primitives (`spec/examples/risk.flag.registry.json`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r174

- Make sysctl drift explainable without bulk inventory by introducing a bounded observation artifact: `sysctl.snapshot` (schema + example) plus a tight wiring doc (keeps drift detection and support bundles self-describing without forcing forks) (`docs/452-sysctl-snapshot-as-evidence-artifact.md`, `spec/sysctl.snapshot.schema.json`, `spec/examples/sysctl.snapshot.json`).
- Tighten sysctl drift evidence by allowing `sysctl.event` to point at a snapshot digest (`snapshot_digest`) and wire snapshots into the evidence spine + kernel knobs lane (`spec/sysctl.event.schema.json`, `spec/examples/sysctl.event.json`, `docs/229-evidence-spine-overview.md`, `docs/318-kernel-tunables-and-sysctls-as-evidence.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r173

- Make policy evaluator code drift mechanically reviewable by introducing a typed policy module diff surface: `policy.module.diff` (schema + example) plus a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/451-policy-module-diff-as-review-surface.md`, `spec/policy.module.diff.schema.json`, `spec/examples/policy.module.diff.json`).
- Wire `policy.module.diff` into the canonical diff surface registry, drift bundle posture guidance, and the evidence spine; extend the canonical risk-flag vocabulary with stable policy-module drift reason codes (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.


## 2026-02-28r172

- Add a guardrail that keeps per-diff review-surface docs uniform and mechanically jumpable: `tools/check_diff_review_docs.py` enforces Tier placement, requires the canonical `Registry→Diff→Gate` token, and requires schema+example pointers; wire it into `python3 tools/hygiene.py` and document the invariant in archive hygiene (`tools/check_diff_review_docs.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`).
- Entropy-reducing refactor: add an explicit “The artifacts” schema/example block to the adapter-kill and impurity-waiver diff wiring docs so reviewers can jump directly to contracts (`docs/444-adapter-kill-policy-diff-as-review-surface.md`, `docs/445-impurity-waiver-policy-diff-as-review-surface.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r171

- Make `/dev` authority drift mechanically reviewable by introducing a typed devfs view diff surface: `devfs.view.diff` (schema + example) plus a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/450-devfs-view-diff-as-review-surface.md`, `spec/devfs.view.diff.schema.json`, `spec/examples/devfs.view.diff.json`).
- Wire `devfs.view.diff` into the canonical diff surface registry, drift bundle posture guidance, and the evidence spine; extend the canonical risk-flag vocabulary with stable `/dev` exposure reason codes (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r170

- Complete the Broker→Lease→Receipt evidence pattern by introducing generic lease issuance + use receipts: `lease.issue.receipt` and `lease.use.receipt` (schemas + examples) plus a tight wiring doc (`docs/449-lease-issue-and-use-receipts.md`, `spec/lease.issue.receipt.schema.json`, `spec/examples/lease.issue.receipt.json`, `spec/lease.use.receipt.schema.json`, `spec/examples/lease.use.receipt.json`).
- Update the lease registry and evidence spine to treat issuance/use as first-class evidence (and fix a small lease-envelope reference miswire); update the pattern catalog to point at the canonical receipts (`docs/249-lease-registry-and-cross-lane-revocation.md`, `docs/229-evidence-spine-overview.md`, `docs/397-pattern-catalog.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r169

- Make exported support bundles self-describing by introducing a typed bundle payload member manifest artifact: `bundle.payload.manifest` (schema + example) plus a tight wiring doc (bytes→members binding as evidence) (`docs/448-bundle-payload-manifest-as-evidence-artifact.md`, `spec/bundle.payload.manifest.schema.json`, `spec/examples/bundle.payload.manifest.json`).
- Tighten bundle build receipts to optionally bind the payload manifest digest (`bundle.build.receipt.output.payload_manifest_digest`) and refresh the deterministic export lane doc + evidence spine so plan→bytes→members stays replayable and explainable (`spec/bundle.build.receipt.schema.json`, `spec/examples/bundle.build.receipt.json`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/229-evidence-spine-overview.md`).
- Update curated references with a primary OCI image manifest/digest pointer and refresh wiring/version stamps (`docs/32-curated-references.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r168

- Make offline mirror kits self-describing by introducing a typed kit manifest artifact: `mirror.kit.manifest` (schema + example) plus a tight wiring doc for evidence/receipt binding (`docs/447-mirror-kit-manifest-as-evidence-artifact.md`, `spec/mirror.kit.manifest.schema.json`, `spec/examples/mirror.kit.manifest.json`).
- Tighten mirror-kit import receipts to record the kit manifest digest when present (`mirror.import.receipt.source.kit_manifest_digest`), and refresh the air-gap mirror-kit lane doc + juicy lesson so operators can always answer “what exactly was on that kit?” with receipts (`spec/mirror.import.receipt.schema.json`, `spec/examples/mirror.import.receipt.json`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r167

- Make trust-policy drift mechanically reviewable by introducing a typed diff surface: `trust.policy.diff` (schema + example) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/446-trust-policy-diff-as-review-surface.md`, `spec/trust.policy.diff.schema.json`, `spec/examples/trust.policy.diff.json`).
- Wire `trust.policy.diff` into the canonical diff registry, drift bundle posture guidance, and the evidence spine so “what signatures/attestations are accepted?” drift stays explainable and gateable without forks; extend the canonical risk-flag vocabulary with a stable trust-policy drift reason code (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r166

- Make “known impurity” non-ambient by introducing an explicit impurity waiver policy and a gateable drift surface: `impurity.waiver.policy` + `impurity.waiver.policy.diff` (schema + examples) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/445-impurity-waiver-policy-diff-as-review-surface.md`, `spec/impurity.waiver.policy.schema.json`, `spec/impurity.waiver.policy.diff.schema.json`, `spec/examples/impurity.waiver.policy.json`, `spec/examples/impurity.waiver.policy.diff.json`).
- Wire `impurity.waiver.policy.diff` into the canonical diff registry, drift bundle posture guidance, the evidence spine, and the determinism-check juicy lesson so reproducibility posture drift stays explainable and gateable without forks; add the primary Nix impurity reference to curated references (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/367-reproducible-generations-and-determinism-checks.md`).
- Extend the canonical risk-flag vocabulary with impurity waiver drift reason codes (`impurity-waiver-added`, `impurity-waiver-extended`, `impurity-waiver-scope-broadened`, `impurity-default-relaxed`) and refresh wiring/version stamps (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r165

- Add an amnesia-resistor guardrail that keeps the meta-engineering "design law" docs discoverable: `tools/check_meta_doc_discoverability.py` requires every numbered doc >=397 to be linked from `docs/00-index.md` or `docs/110-juicy-os-lessons.md`; wire it into `python3 tools/hygiene.py` and document the invariant in archive hygiene (`tools/check_meta_doc_discoverability.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r164

- Make adapter lanes *actually killable* by introducing an explicit adapter posture policy and a gateable diff surface: `adapter.kill.policy` + `adapter.kill.policy.diff` (schema + examples) with a tight wiring doc mapping it to Adapter→Shadow→Replace + Registry→Diff→Gate (`docs/444-adapter-kill-policy-diff-as-review-surface.md`, `spec/adapter.kill.policy.schema.json`, `spec/adapter.kill.policy.diff.schema.json`, `spec/examples/adapter.kill.policy.json`, `spec/examples/adapter.kill.policy.diff.json`).
- Wire `adapter.kill.policy.diff` into the canonical diff surface registry, drift bundle posture guidance, and the evidence spine so “interop toggles” stay explainable and gateable without forks; update adapter lane discipline and the killability juicy lesson (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/110-juicy-os-lessons.md`).
- Extend the canonical risk-flag vocabulary with adapter enablement/scope reason codes and refresh wiring/version stamps (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r163

- Make measured boot explainable and replayable by introducing a typed canonical boot event log artifact: `boot.eventlog.canon` (schema + example) plus a tight wiring doc for bundle/export posture and verifier ergonomics (`docs/443-boot-eventlog-canon-as-evidence-artifact.md`, `spec/boot.eventlog.canon.schema.json`, `spec/examples/boot.eventlog.canon.json`).
- Flesh out the measured-boot lane to treat `boot.eventlog.canon` as the canonical object behind `boot.attestation.tpm.eventlog_digest`, and add an explicit `eventlog_canon` identifier to boot attestation evidence for deterministic replay/verifier behavior (`docs/176-measured-boot-attestation.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `spec/boot.attestation.schema.json`, `spec/examples/boot.attestation.json`, `spec/examples/boot.manifest.json`).
- Wire the new evidence artifact into the evidence spine and measured-boot discovery surface; extend curated references with primary TCG CEL/PFP/event-log-processing specs and refresh version stamps (`docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r162

- Make verified-execution posture drift mechanically reviewable by introducing a typed policy diff surface: `exec.verify.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/442-exec-verify-policy-diff-as-review-surface.md`, `spec/exec.verify.policy.diff.schema.json`, `spec/examples/exec.verify.policy.diff.json`).
- Wire `exec.verify.policy.diff` into the canonical diff surface registry, drift bundle posture guidance, the evidence spine, and the verified-exec juicy lesson so “runtime integrity posture” stays explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the canonical risk-flag vocabulary with verified-exec drift reason codes (`exec-verify-disabled`, `exec-verify-relaxed`, `exec-verify-exception-added`) and refresh wiring/version stamps (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r161

- Make incident/support bundle plan drift mechanically reviewable by introducing a typed bundle plan diff surface: `bundle.plan.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/441-bundle-plan-diff-as-review-surface.md`, `spec/bundle.plan.diff.schema.json`, `spec/examples/bundle.plan.diff.json`).
- Wire `bundle.plan.diff` into the canonical diff surface registry and update the bundle export lane + juicy lessons to reference the stable diff surface (`docs/430-diff-surface-registry.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r160

- Add a guardrail that keeps the canonical risk-flag registry wired to real review surfaces: `tools/check_risk_flag_typical_sources.py` validates that each `typical_sources` entry in `risk.flag.registry` points at a real schema under `spec/` and that any `*.diff` sources are listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`).
- Wire the new check into `python3 tools/hygiene.py` and document the invariant in archive hygiene guidance (`docs/98-archive-hygiene.md`).
- Refresh discovery/version stamps (`docs/00-index.md`, `README.md`, `docs/110-juicy-os-lessons.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## 2026-02-28r159

- Make remote attestation admission drift mechanically reviewable by introducing a typed admission policy diff surface: `attestation.admission.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/440-attestation-admission-policy-diff-as-review-surface.md`, `spec/attestation.admission.policy.diff.schema.json`, `spec/examples/attestation.admission.policy.diff.json`).
- Wire `attestation.admission.policy.diff` into the canonical diff surface registry, drift bundle posture-diff guidance, the evidence spine, and the Keylime/admission juicy lesson so “what is attestation-gated?” stays explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the open-questions/risk register with the remaining admission-policy drift/gate questions and extend the canonical risk-flag registry with admission drift reason codes (`docs/266-open-questions-and-risk-register.md`, `spec/examples/risk.flag.registry.json`).
- Bump version stamps, update discovery wiring (`docs/00-index.md`, `README.md`), and regenerate generated discovery surfaces.

## 2026-02-28r158

- Make kernel module policy drift mechanically reviewable by introducing a typed module policy diff artifact: `kmod.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/439-kmod-policy-diff-as-review-surface.md`, `spec/kmod.policy.diff.schema.json`, `spec/examples/kmod.policy.diff.json`).
- Wire `kmod.policy.diff` into the canonical diff surface registry, drift bundle posture-diff guidance, and the evidence spine; update the kernel module lane and discovery surfaces so “privileged code allowlists” remain explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`).
- Extend the canonical risk-flag vocabulary with kmod policy drift reason codes (e.g. `kmod-policy-runtime-load-enabled`) so gates and review UI can consistently reason about module policy posture changes (`spec/examples/risk.flag.registry.json`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`, `README.md`), and regenerate generated discovery surfaces.

## 2026-02-28r157

- Make time-source posture drift mechanically reviewable by introducing a typed time source policy diff surface: `time.source.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/438-time-source-policy-diff-as-review-surface.md`, `spec/time.source.policy.diff.schema.json`, `spec/examples/time.source.policy.diff.json`).
- Extend the canonical risk-flag vocabulary with time authority drift reason codes (`time-source-added`, `time-quorum-relaxed`, `time-bootstrap-relaxed`, etc.) so gates and review UI can consistently reason about time posture drift (`spec/examples/risk.flag.registry.json`).
- Wire `time.source.policy.diff` into the canonical diff surface registry, drift bundle posture-diff guidance, the evidence spine, and the trustworthy-time discovery surface (keeps time as evidence explainable and policy-gateable without forks) (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## 2026-02-28r156

- Harden discovery-surface drift control by extending `tools/check_discovery.py` to require (a) the newest `## New in <version>` block in `docs/00-index.md` is the **first** such block and (b) the index `Last updated:` stamp matches the newest release (prevents stale top-of-file release notes from lingering) (`tools/check_discovery.py`, `docs/00-index.md`, `docs/98-archive-hygiene.md`).
- Update discovery/version stamps and regenerate generated discovery surfaces.

## 2026-02-28r155

- Add an incremental guardrail that ties diff wiring docs to the canonical `risk_flags` vocabulary: wiring docs listed in the diff surface registry must declare a `## Risk flags` section (or be explicitly allowlisted), preventing “diff exists but gates have no reason-code surface” drift (`tools/check_diff_wiring_risk_flags.py`, `tools/baselines/diff_wiring_missing_risk_flags.txt`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/430-diff-surface-registry.md`).
- Refactor the sandbox/sysctl/export diff wiring docs to declare minimal starter risk-flag sets using canonical ids (keeps posture drift gateable and explainable without forks) (`docs/432-sandbox-profile-diff-as-review-surface.md`, `docs/429-sysctl-diff-as-drift-surface.md`, `docs/433-export-policy-diff-as-review-surface.md`).
- Update discovery/version stamps and regenerate generated discovery surfaces.

## 2026-02-28r154

- Add a Tier C optional lane for **split secrets brokers** (Split GPG / Split SSH style): keep private keys in a more trusted compartment and delegate bounded crypto operations via Broker→Lease→Receipt; keep interop killable via Adapter→Shadow→Replace (`docs/437-split-secrets-brokers.md`).
- Wire the lane into discovery and citation surfaces (juicy lessons + curated references) and bump version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).
- Capture remaining split-secrets/broker-identity questions by extending the crypto operations portal risk entry (keeps the open-questions register as the source of truth) (`docs/266-open-questions-and-risk-register.md`).


## 2026-02-27r153

- Make boot-critical closure drift mechanically reviewable by introducing a typed boot manifest diff surface: `boot.manifest.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/436-boot-manifest-diff-as-review-surface.md`, `spec/boot.manifest.diff.schema.json`, `spec/examples/boot.manifest.diff.json`).
- Wire `boot.manifest.diff` into the canonical diff surface registry, drift bundle posture-diff guidance, and the evidence spine + measured-boot lesson so “what did we boot?” stays explainable (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the canonical risk-flag vocabulary with boot drift reason codes (`bootloader-changed`, `kernel-image-changed`, `cmdline-profile-changed`) and refresh discovery/version wiring (`spec/examples/risk.flag.registry.json`, `README.md`).

## 2026-02-27r152

- Add a canonical risk-flag vocabulary registry (`risk.flag.registry`) so `risk_flags` reason codes used by diff summaries and gates stay explicit, stable, and profile-aware without forks (`docs/435-risk-flags-registry-and-gate-vocabulary.md`, `spec/risk.flag.registry.schema.json`, `spec/examples/risk.flag.registry.json`).
- Add a drift guardrail (`tools/check_risk_flag_registry.py`) wired into `python3 tools/hygiene.py` to prevent ad-hoc risk-flag strings (enforces canonical kebab-case ids in spec examples and in gate docs lines mentioning `risk_flags`).
- Entropy-reducing refactor: normalize existing diff examples + gate docs to canonical kebab-case risk flags, update curated references, update discovery wiring, and regenerate generated discovery surfaces.

## 2026-02-27r151

- Entropy-reducing refactor: extend the canonical diff surface registry to include a per-diff wiring doc pointer column, so every review surface has a direct jump-to for gate semantics + bundle attachment (`docs/430-diff-surface-registry.md`).
- Add a new drift guardrail (`tools/check_diff_surface_registry_wiring.py`) and wire it into `python3 tools/hygiene.py`; document the invariant in archive hygiene (`docs/98-archive-hygiene.md`).
- Update discovery/version wiring and regenerate generated discovery surfaces (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-27r150

- Make trust root drift mechanically reviewable by introducing a typed PKI trust bundle diff artifact: `spec/pki.trust.bundle.diff.schema.json`, `spec/examples/pki.trust.bundle.diff.json`, plus a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/434-pki-trust-bundle-diff-as-review-surface.md`).
- Wire `pki.trust.bundle.diff` into the canonical diff surface registry and drift bundle guidance (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`) and into the evidence spine and trust roots discovery surfaces (`docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the trust bundle open-question block with explicit drift/gating questions and refresh version stamps + regenerate generated discovery surfaces (`docs/266-open-questions-and-risk-register.md`, `docs/00-index.md`).

## 2026-02-27r149

- Make data-egress boundary drift mechanically reviewable by introducing a typed export policy diff artifact: `spec/export.policy.diff.schema.json`, `spec/examples/export.policy.diff.json`, plus a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/433-export-policy-diff-as-review-surface.md`).
- Wire export boundary diffs into the canonical diff surface registry and drift bundle guidance (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`) and into the evidence spine so exports are explainable (`docs/229-evidence-spine-overview.md`).
- Extend juicy lesson #122 with export boundary drift discipline (`docs/110-juicy-os-lessons.md`), add the primary sosreport upstream reference to the curated pointer map (`docs/32-curated-references.md`), and capture remaining export-boundary drift questions (`docs/266-open-questions-and-risk-register.md`).
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r148

- Make sandbox posture changes mechanically reviewable by introducing a typed sandbox promise-profile diff artifact: `spec/sandbox.profile.diff.schema.json`, `spec/examples/sandbox.profile.diff.json`, plus a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/432-sandbox-profile-diff-as-review-surface.md`).
- Update the canonical diff surface registry to include `sandbox.profile.diff` (`docs/430-diff-surface-registry.md`) and reduce entropy in drift bundle guidance by removing redundant diff lists while still calling out posture diffs (`docs/395-drift-bundles-and-review-summaries.md`).
- Wire sandbox posture drift into the evidence/discovery surfaces (evidence spine + juicy lessons) and bump version stamps + regenerate generated discovery surfaces (`docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`).

## 2026-02-27r147

- Add a juicy-lessons citation guardrail (`tools/check_juicy_lesson_references.py` + `tools/baselines/juicy_urls_allowlist.txt`), wire it into `python3 tools/hygiene.py`, and document it in `docs/98-archive-hygiene.md` (blocks new uncataloged URLs in `docs/110-juicy-os-lessons.md` without forcing retroactive churn).
- Add a conservative Tier C stabilization lane note plus a typed receipt artifact for explicit determinism normalizers: `build.stabilizer.receipt` (schema + example) and `docs/431-build-stabilizers-and-determinism-normalizers.md` (`spec/build.stabilizer.receipt.schema.json`, `spec/examples/build.stabilizer.receipt.json`).
- Extend curated references with primary reproducible-builds normalization sources and refresh version stamps + regenerate generated discovery surfaces.

## 2026-02-27r146

- Add a canonical diff surface registry as a stable review surface (`docs/430-diff-surface-registry.md`) and refactor drift bundle guidance to reference it (`docs/395-drift-bundles-and-review-summaries.md`).
- Add a new drift guardrail (`tools/check_diff_surface_registry.py`) and wire it into `python3 tools/hygiene.py`, preventing new `*.diff` schemas from landing without explicit registry wiring.
- Document the new guardrail in archive hygiene (`docs/98-archive-hygiene.md`) and bump version stamps + regenerate generated discovery surfaces.

## 2026-02-27r145

- Make kernel knob posture drift reviewable by introducing a typed sysctl plan diff artifact: `spec/sysctl.diff.schema.json`, `spec/examples/sysctl.diff.json`, plus a tight wiring doc mapping the lane to Plan→Receipt + Registry→Diff→Gate and drift bundles (`docs/429-sysctl-diff-as-drift-surface.md`).
- Wire `sysctl.diff` into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`), extend juicy lesson #183 with “planned sysctl diffs” (`docs/110-juicy-os-lessons.md`), and refresh the kernel mutation control open question block (`docs/266-open-questions-and-risk-register.md`).
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r144

- Make platform posture drift reviewable by introducing a typed firmware inventory diff artifact: `spec/fw.inventory.diff.schema.json`, `spec/examples/fw.inventory.diff.json`, plus a tight wiring doc mapping the lane to Registry→Diff→Gate and drift bundles (`docs/428-fw-inventory-diff-as-drift-surface.md`).
- Wire `fw.inventory.diff` into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`) and extend juicy lesson #187 with “firmware posture diffs” (`docs/110-juicy-os-lessons.md`).
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r143

- Add a release-scope stamp guardrail: `tools/check_release_last_updated.py` requires docs mentioned in the newest `CHANGELOG.md` entry to be stamped `Last updated: <version>` (keeps doc changes mechanically visible without retroactive churn). Wired into `python3 tools/hygiene.py` and documented in `docs/98-archive-hygiene.md`.
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r142

- Make `/etc` drift reviewable by introducing a typed diff artifact: `spec/etc.config.diff.schema.json`, `spec/examples/etc.config.diff.json`, plus a tight wiring doc that maps the lane to Registry→Diff→Gate and bundles (`docs/427-etc-config-diff-as-a-drift-surface.md`).
- Wire `etc.config.diff` into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`) and add a juicy lesson subchapter on `/etc` drift discipline (`docs/110-juicy-os-lessons.md`).
- Extend curated references with the FreeBSD `etcupdate(8)` primary reference (keeps citations centralized): `docs/32-curated-references.md`.
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r141

- Make retention **explainable** by introducing typed store GC artifacts: `spec/store.gc.plan.schema.json`, `spec/store.gc.receipt.schema.json` plus examples, and a tight wiring doc: `docs/426-store-gc-plans-and-receipts.md` (Plan→Apply→Receipt + policy gates).
- Close a paper-artifact gap by adding typed pin receipts used by GC roots: `spec/pin.add.receipt.schema.json`, `spec/pin.rm.receipt.schema.json` plus examples (aligns `docs/175-pins-roots-and-garbage-collection.md` and RFC-0110).
- Wire GC receipts into the evidence spine and refresh GC ergonomics guidance (`docs/229-evidence-spine-overview.md`, `docs/175-pins-roots-and-garbage-collection.md`); extend juicy lesson #58 with “retention as evidence” (`docs/110-juicy-os-lessons.md`).
- Extend curated references with primary Nix GC documentation (`docs/32-curated-references.md`).
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r140

- Add a new drift guardrail: `tools/check_doc_patterns.py` enforces that meta-engineering docs (numeric prefix >=397) declare a `**Patterns:**` metadata line mapping the doc to the pattern catalog (skips generated navigation surfaces).
- Entropy-reducing refactor: add `**Patterns:**` metadata to the existing meta-doc range (>=397) and tighten the pattern catalog + LLM runbook to treat explicit pattern mapping as part of the stable review surface.
- Wire the new check into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`.
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r139

- Add an optional TPM-sealed secrets lane with typed, diffable PCR policies: `docs/425-tpm-sealed-secrets-and-pcr-policies.md`, `spec/tpm.pcr.policy.schema.json`, `spec/examples/tpm.pcr.policy.json`.
- Add a release drift guardrail: `tools/check_release_curated_references.py` ensures numbered docs mentioned in the newest `CHANGELOG.md` entry don't introduce external URLs without also adding them to `docs/32-curated-references.md` (keeps citations centralized for new work).
- Wire the new guardrail into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`; update curated references with TPM sealing + PCR measurement sources.
- Extend juicy lesson #59 with TPM-sealed secrets as a high-leverage optional lane (`docs/110-juicy-os-lessons.md`).
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r138

- Add a schema drift guardrail: `tools/check_schema_kind_matches_filename.py` enforces that schemas with dotted `kind` names keep a stable schema naming discipline (e.g. `spec/mirror.import.receipt.schema.json` declares kind `mirror.import.receipt`) (prevents quiet kind/filename mismatch drift).
- Wire the new check into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`.
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r137

- Add a changelog format guardrail (`tools/check_changelog_format.py`) and wire it into hygiene to keep release notes compact and diff-friendly.
- Normalize CHANGELOG spacing to reduce diff noise and improve discovery ergonomics.
- Bump version stamps and regenerate generated discovery surfaces.

## 2026-02-27r136

- Make bundle-min *explainable and replayable* by adding a typed build receipt: `spec/bundle.build.receipt.schema.json`, `spec/examples/bundle.build.receipt.json`, and wire it into deterministic export/bundle guidance (`docs/253-bundle-plans-and-deterministic-exports.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`).
- Reduce drift/entropy by defining the incident bundle include-knob surface once and reusing it: `spec/incident.bundle.schema.json` now exposes `#/$defs/include_knobs`, and `spec/bundle.plan.schema.json` references it (keeps selection plans aligned with bundle include knobs).
- Bump version stamps and regenerate generated discovery surfaces.


## 2026-02-27r135

- Make the air-gap mirror kit lane concrete with typed Plan→Receipt artifacts for quarantine-first imports and policy-gated promotion: `spec/mirror.import.plan.schema.json`, `spec/mirror.import.receipt.schema.json`, `spec/mirror.promote.plan.schema.json`, `spec/mirror.promote.receipt.schema.json` plus matching examples, and update `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`.
- Add a new drift guardrail to prevent “paper artifacts”: `tools/check_changelog_artifact_mentions.py` enforces that docs referenced by the newest `CHANGELOG.md` entry only mention `*.plan`/`*.receipt`/etc artifacts that have schemas in `spec/`; wire it into `tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`.
- Extend curated references with the Uptane Standard and add a new juicy lesson on offline update ergonomics (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`).


## 2026-02-27r134

- Add an optional forward-secure event log sealing lane (tamper-evident local evidence) by introducing `event.seal.receipt` (schema + example) and wiring it into the evidence spine: `docs/424-forward-secure-event-log-sealing.md`, `spec/event.seal.receipt.schema.json`, `spec/examples/event.seal.receipt.json`, updates to `docs/215-structured-event-log-as-evidence.md`, `docs/229-evidence-spine-overview.md`, and juicy lesson 288 in `docs/110-juicy-os-lessons.md`.
- Reduce amnesia by extending the context pack generator to include a compact “Recent changes” section sourced from `CHANGELOG.md` (Markdown + JSON): `tools/gen_context_pack.py`, regenerated `docs/420-context-pack.md`, `docs/_generated/context_pack.json`.
- Update curated references with official FSS/digest-chain sources and bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).


## 2026-02-27r133

- Make the “reproducible generations” lane actionable by adding typed artifacts for determinism checks: `spec/repro.check.plan.schema.json`, `spec/repro.check.receipt.schema.json` plus examples, and update `docs/367-reproducible-generations-and-determinism-checks.md`.
- Wire `repro.check.receipt` into review ergonomics as an optional drift-bundle attachment (`docs/395-drift-bundles-and-review-summaries.md`) and regenerate the artifact index (`docs/418-artifact-index.md`, `docs/_generated/artifact_index.json`).
- Bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`).

## 2026-02-27r132

- Add **persist sets** as a first-class registry (`persist.set.registry`) so “what is allowed to persist” becomes a stable diff surface (impermanence/stateless-root lesson) (`docs/423-persist-sets-and-ephemeral-root.md`, `spec/persist.set.registry.schema.json`, `spec/examples/persist.set.registry.json`).
- Strengthen anti-amnesia release wiring: `tools/check_discovery.py` now enforces that numbered docs mentioned in the newest `CHANGELOG.md` entry are discoverable from the index or juicy lessons, and that they appear in the matching `docs/00-index.md` “New in …” block (prevents orphan docs + stale release notes).
- Update discovery wiring + curated references for the new lane and bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/98-archive-hygiene.md`, `README.md`).
## 2026-02-27r131

- Add a first-class **invariant registry** as a stable diff surface (Registry → Diff → Gate), so “must never break” rules are diffable, gateable, and referenceable (`docs/422-invariant-registry-and-design-invariants.md`, `spec/invariant.registry.schema.json`, `spec/examples/invariant.registry.json`).
- Tighten meta-engineering wiring: design review intake now asks which invariants a proposal touches (prevents slow weakening by omission) (`docs/348-design-review-rubric-and-feature-intake.md`).
- Fix a subtle amnesia drift hole: the context pack generator now extracts **all** backticked items from the runbook’s must-read list (so grouped bullets can’t silently drop required docs), and the runbook list now uses one doc per bullet for stable review surfaces.
- Add a new guardrail to prevent refresh-path erosion: `tools/check_must_read_set.py` (wired into `tools/hygiene.py`).
- Update discovery wiring + references accordingly and bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/98-archive-hygiene.md`, `README.md`).

## 2026-02-27r130

- Add a research **disposable workspace** lane (Template → Lease → Dispose), translating Qubes TemplateVM/DisposableVM into DeriveBSD patterns, receipts, and optional activation ergonomics (`docs/421-disposable-workspaces-and-template-microvms.md`; wired from `docs/110-juicy-os-lessons.md` and `docs/00-index.md`).
- Add a new guardrail to keep external citations durable: enforce that **meta docs** (>=397) only introduce external URLs if they are also listed in `docs/32-curated-references.md` (`tools/check_curated_references.py`; wired into `tools/hygiene.py`), and backfill missing references for existing meta docs.
- Tighten version stamp discipline by extending `tools/check_version.py` to also validate the `Last updated:` tag in `docs/00-index.md` (in addition to README + `docs/110-juicy-os-lessons.md`).

## 2026-02-27r129

- Promote the **context pack** from “a tool output” to a first-class generated discovery surface: add `docs/420-context-pack.md` + `docs/_generated/context_pack.json` and extend `tools/gen_context_pack.py` with deterministic `--write` / `--json` outputs.
- Wire the context pack into anti-amnesia guardrails: `tools/check_generated_docs.py` validates it, and `tools/check_discovery.py` requires it to be linked from `docs/00-index.md`.
- Update discovery + hygiene wiring accordingly (`docs/00-index.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-27r128

- Add a first-class **incident timeline** artifact (`incident.timeline`) as a typed, digest-bound human-scale orientation surface (schema + example + doc: `spec/incident.timeline.schema.json`, `spec/examples/incident.timeline.json`, `docs/419-incident-timelines-as-derived-artifacts.md`).
- Wire timelines into the evidence spine and incident bundle story: evidence overview now lists `incident.timeline`, incident bundles can include the timeline digest, and causality graphs explicitly pair with timeline views (`docs/229-evidence-spine-overview.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/246-causality-graphs-and-minimal-evidence-bundles.md`, `docs/220-operational-time-travel-debugging.md`).
- Refresh the structured output contract with an incident timeline domain output example and update curated references with DFIR timeline prior art (Plaso/Timesketch) (`docs/87-structured-output-contract.md`, `docs/32-curated-references.md`).

## 2026-02-27r127

- Make **A–D profile identifiers** unambiguous and mechanically checkable: add `spec/product.profile_aliases.json` mapping letter aliases (A–D) to canonical profile ids.
- Strengthen guardrails: `tools/check_doc_metadata.py` now accepts either A–D or canonical profile ids and normalizes to canonical ids (detecting duplicates like `A` + `fleet_host`).
- Improve discovery surfaces: the generated product profile matrix now shows both alias + canonical id (and notes where aliases are defined), and the context pack includes the alias field.

## 2026-02-27r126

- Add a generated **artifact index** (Markdown + JSON) mapping `kind` → canonical schema → example(s), as a first-class discovery surface for typed outputs (`docs/418-artifact-index.md`, `docs/_generated/artifact_index.json`, `tools/gen_artifact_index.py`).
- Fix a drift hole: `tools/check_generated_docs.py` now actually checks the risk register index outputs (and also validates the artifact index), so generated docs can't silently stale.
- Add a lightweight **spec example coverage** guardrail and wire it into hygiene, ensuring each plan/receipt/event/report/registry/diff schema has a matching example (`tools/check_spec_example_coverage.py`, `tools/hygiene.py`).
- Wire the new discovery surface into the runbook/index/context pack and extend curated references + juicy lessons accordingly.

## 2026-02-27r125

- Add a typed **platform provenance report** artifact (`platform-report`) with schema + example (`spec/platform.report.schema.json`, `spec/examples/platform.report.json`) and wire it into the firmware/platform lifecycle story (`docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`).
- Refactor firmware documentation to reduce naming drift: align the high-level firmware lane doc with the existing `fw.update.*` and `fw.*inventory*` artifacts, and wire `platform-report` as a digest-first umbrella rather than a competing inventory format (`docs/221-firmware-updates-as-artifacts.md`, `docs/229-evidence-spine-overview.md`).
- Tighten the structured output contract to include canonical domain outputs for platform probing and firmware update planning/apply (`docs/87-structured-output-contract.md`).
- Extend curated references with firmware/UEFI tooling (fwupd/LVFS, FreeBSD fwget/efivar) and add DICE as an optional platform identity lane; add a new juicy lesson tying platform provenance + firmware receipts into the evidence model (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Strengthen the doc metadata guardrail by validating Tier/Profiles/Pillars values (not just presence) for meta-engineering docs (`tools/check_doc_metadata.py`, `docs/98-archive-hygiene.md`).

## 2026-02-27r124

- Add a first-class **policy trace** artifact (schema + example) and bind `derive explain-policy --json --trace` to a stable trace shape (`spec/policy.trace.schema.json`, `spec/examples/policy.trace.json`, `docs/416-policy-trace-format-and-explain-surfaces.md`).
- Refine policy meta-docs to reference `trace_digest` and the trace schema, and extend the structured-output contract to treat `--trace` output as typed by domain (`docs/85-policy-engine-options-and-traces.md`, `docs/93-policy-decision-records.md`, `docs/87-structured-output-contract.md`).
- Update discovery surfaces and curated references for policy explanation/decision-log prior art; bump version wiring and stamps.


## 2026-02-27r123

- Add a generated **risk register index** (markdown + JSON) so the canonical long-form register remains scannable and machine-usable (`docs/415-risk-register-index.md`, `docs/_generated/risk_register.json`, `tools/gen_risk_register_index.py`).
- Add a simple **risk register lint** and wire it into hygiene so each numeric item names its failure mode explicitly (`tools/check_risk_register.py`, `tools/hygiene.py`).
- Extend generated-doc and discovery wiring guardrails to cover the new risk index, and update runbook/index/hygiene docs accordingly (`tools/check_generated_docs.py`, `tools/check_discovery.py`, `tools/gen_context_pack.py`, `docs/99-llm-runbook.md`, `docs/00-index.md`, `docs/98-archive-hygiene.md`).
- Refactor discovery surfaces: fix tail wiring/last-updated placement in juicy lessons; update risk register to remove stale stamps and add missing `Risk:` lines (`docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`).

## 2026-02-27r122

- Add a generated **doc catalog** summary page plus a full JSON index (navigation/memory prosthetic for humans and LLMs) (`docs/414-doc-catalog.md`, `docs/_generated/doc_catalog.json`, `tools/gen_doc_catalog.py`).
- Extend the generated-doc guardrail to cover the doc catalog outputs and keep discovery surfaces from silently drifting (`tools/check_generated_docs.py`, `docs/98-archive-hygiene.md`).
- Wire the doc catalog into the runbook + index, and treat it as a first-class amnesia-resistor; add a small curated-reference pointer for documentation/navigation tooling (`docs/00-index.md`, `docs/99-llm-runbook.md`, `tools/check_discovery.py`, `tools/gen_context_pack.py`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-27r121

- Add a generated **A–D product profile matrix** doc plus a generator + stale-check so profile defaults/invariants stay mechanically visible and don't drift (`docs/412-product-profile-matrix.md`, `tools/gen_product_profile_matrix.py`, `tools/check_generated_docs.py`).
- Add a lightweight **doc metadata** guardrail for the meta-engineering doc range (>=397): new docs must declare Tier/Profiles/Pillars near the top; wire check into hygiene (`tools/check_doc_metadata.py`, `tools/hygiene.py`, plus metadata blocks across docs 397–411).
- Add a tight ZFS replication operations doc focused on **resume tokens**, **bookmarks**, and **encryption-aware** replication, and wire it into backup/distribution lanes + profile defaults (`docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`, `docs/316-backups-and-restores-as-derived-operations.md`, `docs/126-zfs-send-distribution.md`, `spec/examples/product.profiles.json`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-27r120

- Make A–D viability **mechanical**: add first-class product profiles as compilation targets (`docs/411-product-profiles-as-compilation-target.md`) plus a schema+example artifact (`spec/product.profiles.schema.json`, `spec/product.profile.schema.json`, `spec/examples/product.profiles.json`).
- Add anti-amnesia repo tooling: an LLM runbook and a deterministic context-pack generator (`docs/99-llm-runbook.md`, `tools/gen_context_pack.py`).
- Add a lightweight discovery-surface check and wire it into `tools/hygiene.py` so new releases stay wired (`tools/check_discovery.py`, `docs/98-archive-hygiene.md`, `docs/00-index.md`).
- Promote two previously under-specified cross-profile cliffs to first-class docs: **data at rest** (ZFS encryption + key lanes + receipts) and **desktop viability constraints** (`docs/409-zfs-encryption-and-key-management.md`, `docs/410-desktop-viability-checklist.md`).
- Tighten meta-engineering: design-review rubric now requires tier + profile applicability for new work; discovery surfaces and references updated; risk register extended (`docs/348-design-review-rubric-and-feature-intake.md`, `docs/32-curated-references.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-27r119

- Add a **spec schema conventions + evolution** guide and a lightweight **schema linter** so artifact shapes stay consistent and tooling remains generic (`docs/407-spec-schema-conventions-and-evolution.md`, `tools/lint_spec_schemas.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`).
- Add a bounded **ABI compatibility adapter lane** doc (Linuxulator / WSL 1→2 lesson) so “run Linux binaries” remains an explicit, policy-gated choice with clear upgrade paths to Linux microVMs (`docs/408-abi-compatibility-lanes-linuxulator-vs-microvms.md`).
- Wire the new work into discovery surfaces (index, curated references, juicy lessons) and bump version metadata (`docs/00-index.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`, `README.md`).

## 2026-02-27r118

- Add a reproducible **interactive VM test driver + artifact capture** discipline (NixOS/openQA-shaped) so multi-node scenario tests are easy to debug and always export content-addressed evidence (`docs/405-interactive-vm-tests-and-artifact-capture.md`).
- Add **UAPI fuzz descriptors** as a registry-aligned, syzkaller-shaped lane (link harness/descriptor digests directly from UAPI surfaces so fuzz gates become mechanical) (`docs/406-uapi-fuzz-descriptors-and-conformance.md`).
- Tighten meta-engineering wiring: design-review rubric now explicitly asks for scenario/integration test gates on boot/network/update-path changes, and links to the interactive driver (`docs/348-design-review-rubric-and-feature-intake.md`).
- Wire the new lanes into existing surfaces: scenario tests and test receipts now point at the driver ergonomics; UAPI registry and fuzz-farm docs now point at the fuzz descriptor lane; curated references and juicy lessons extended; discovery index updated; version stamps bumped (`docs/188-scenario-tests-multimachine.md`, `docs/166-test-receipts-and-promotion-gates.md`, `docs/362-uapi-surface-registry-and-compat-gates.md`, `docs/274-continuous-fuzzing-farm.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).

## 2026-02-27r117

- Add **SWHID fallback + long-term source availability** guidance (hash-first fetcher with policy-governed multi-origin resolvers; mirror-kit-friendly) (`docs/403-swhid-fallback-and-long-term-source-availability.md`).
- Add a crisp **ZFS boot environments ↔ system generations contract** (receipt-backed identity, health-gated commit, GC/retention integration) (`docs/404-zfs-boot-environments-as-system-generations.md`).
- Wire these into supply-chain and operability surfaces: supply chain doc now includes URL-rot resilience; mirror kits can optionally carry sources; system activation and health-gated updates reference the BE contract; curated references and discovery paths updated; juicy lessons and risk register updated; version stamps bumped (`docs/14-supply-chain.md`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/06-system-activation.md`, `docs/112-health-gated-updates.md`, `docs/32-curated-references.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`, `README.md`).

## 2026-02-27r116

- Add a crisp **v0 cutline + feature tiering discipline** to keep the project shippable while preserving ambitious optional lanes (`docs/401-v0-cutline-and-feature-tiers.md`).
- Add **adapter lane + strangler discipline** guidance so interop layers (ports/pkg, OCI, full TUF, pkgbase) remain bounded, receipted, and *killable* (`docs/402-adapter-lanes-and-strangler-discipline.md`).
- Extend the pattern catalog with **Adapter → Shadow → Replace** as an explicit meta-pattern for interop without forever-legacy (`docs/397-pattern-catalog.md`).
- Tighten meta-engineering wiring: design-review rubric now requires an adapter plan when interop bridges are introduced; scope and risk register link to the new tiering/adapter discipline; discovery surfaces and references updated; version stamps bumped (`docs/348-design-review-rubric-and-feature-intake.md`, `docs/22-scope-and-direction.md`, `docs/266-open-questions-and-risk-register.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).

## 2026-02-27r115

- Add an underused FreeBSD networking lane: **netgraph + netmap/VALE as derived network fabrics** (`docs/400-netgraph-and-netmap-as-derived-network-fabrics.md`).
- Extend host networking as a derived operation to include optional netgraph/netmap backends (still policy-gated + receipted) and wire into discovery surfaces (`docs/322-network-topology-and-firewall-as-derived-operations.md`, `docs/00-index.md`).
- Update juicy lessons index with a new netgraph/netmap item and extend curated references with the key man pages/articles (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Tighten meta-engineering guardrails: add a “pattern fit” prompt to the design review rubric and link design principles to the pattern catalog (`docs/348-design-review-rubric-and-feature-intake.md`, `docs/12-design-principles.md`, `docs/397-pattern-catalog.md`).

## 2026-02-27r114

- Add a **pattern catalog** to keep new subsystems in a small set of reusable shapes (`docs/397-pattern-catalog.md`).
- Add an optional **Zig toolchain wedge** for pragmatic cross-compiling of C/C++ dependency mass (`docs/398-zig-toolchain-wedge-and-cross-compilation.md`).
- Add **evidence queries over fact tables** (osquery-shaped ergonomics, but derived + receipted) (`docs/399-evidence-queries-and-fact-tables.md`).
- Wire the new docs into discovery surfaces (index + juicy lessons + references) and refresh version stamps.

## 2026-02-27r113

- Add **drift bundles** (`drift.bundle`) as the default review attachment: one typed object that summarizes and links all drift surfaces and attached evidence (`docs/395-drift-bundles-and-review-summaries.md`, `spec/drift.bundle.schema.json`, `spec/examples/drift.bundle.json`).
- Add **closure diffs** (`closure.diff`) to make “new code ingestion” reviewable (added/removed store paths, new origins, risk tags) and to complement blast-radius review (`docs/396-closure-diffs-and-new-code-surfaces.md`, `spec/closure.diff.schema.json`, `spec/examples/closure.diff.json`).
- Wire the new artifacts into meta-engineering guardrails and discovery surfaces (design principles + rubric + blast-radius doc + surface-registry meta-pattern + index + references + juicy lessons + README) and bump archive version metadata.

## 2026-02-27r112

- Add **policy tests as first-class artifacts**: introduce `policy.test.suite` + `policy.test.report` schemas and examples, and document regression vectors + optional mutation testing (`docs/393-policy-tests-suites-and-mutation.md`, `spec/policy.test.suite.schema.json`, `spec/policy.test.report.schema.json`, and examples).
- Add an optional **policy analysis lane** (automated reasoning complements tests for high-assurance authorization surfaces) (`docs/394-policy-analysis-and-automated-reasoning.md`).
- Wire the new lane into meta-engineering guardrails and discovery surfaces (design principles + design-review rubric + indexes + references) (`docs/12-design-principles.md`, `docs/348-design-review-rubric-and-feature-intake.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).

## 2026-02-27r111

- Make crypto drift reviewable: add `crypto.registry` + `crypto.diff` schemas and examples, and document the gating model (`docs/391-crypto-surface-registry-and-agility-gates.md`, `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`, and examples).
- Standardize non-exportable keys as policy objects: introduce `crypto.key.policy` (backend binding, subject selectors, quorum/presence hooks) with schema + example (`docs/392-crypto-key-policies-and-nonexportable-handles.md`, `spec/crypto.key.policy.schema.json`, `spec/examples/crypto.key.policy.json`).
- Extend blast-radius diffs to optionally include a `crypto` section (umbrella report can carry crypto drift) and bump schema to v1.3 (`spec/blast_radius.diff.schema.json`, `spec/examples/blast_radius.diff.json`, `docs/106-blast-radius-diff.md`).
- Wire crypto drift into meta-engineering guardrails: update the design principles, surface registry pattern, and the design-review rubric (`docs/12-design-principles.md`, `docs/379-surface-registry-pattern.md`, `docs/348-design-review-rubric-and-feature-intake.md`).
- Extend juicy lessons + curated references with crypto drift and misuse-resistant library pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh discovery/version stamps (`docs/00-index.md`, `README.md`) and bump archive version metadata.

## 2026-02-27r110

- Add an optional **CHERI capability-hardware lane** doc (memory safety + compartmentalization as an explicit platform target; conventional vs hybrid vs purecap is honest and reviewable) (`docs/387-cheri-capability-hardware-and-memory-safety-lane.md`).
- Add a focused **remote attestation admission** doc (Keylime-shaped lessons) and introduce `attestation.admission.policy` so “what is gated by attestation?” becomes a typed, diffable artifact (`docs/388-remote-attestation-admission-and-enrollment.md`, `spec/attestation.admission.policy.schema.json`, `spec/examples/attestation.admission.policy.json`).
- Add an optional **chaos/failure-injection lane** as plans + receipts (fault injection is temporary authority, not SSH folklore) (`docs/389-chaos-experiments-and-fault-injection-as-leases.md`, `spec/chaos.experiment.plan.schema.json`, `spec/chaos.experiment.receipt.schema.json`, and examples).
- Add an optional **measured launch / DRTM** doc (TrenchBoot-shaped late-launch integrity lane) and wire it into the measured boot story (`docs/390-measured-launch-and-drtm-trenchboot-lane.md`).
- Refresh discovery/version surfaces (index blocks, juicy lessons, curated references, README) and bump archive version metadata.

## 2026-02-27r109

- Add an explicit stance on **kernel programmability risk** (BPF/JITs as authority + parser hazard), and map it into the existing registry/diff surfaces (`docs/384-kernel-extensibility-bpf-and-jit-risk.md`).
- Add **deprecation lifecycle discipline** (no silent removals): introduce `deprecation.notice` as a first-class object and document removal receipts (`docs/385-deprecation-policies-and-removal-receipts.md`, `spec/deprecation.notice.schema.json`, `spec/examples/deprecation.notice.json`).
- Make **UserEnv activation** a derived operation with plans/receipts (atomic profile switch + rollback UX) (`docs/386-userenv-activation-plans-and-receipts.md`, `spec/userenv.activate.plan.schema.json`, `spec/userenv.activate.receipt.schema.json`, and examples).
- Tighten the design-review rubric to require deprecation notices for compatibility breaks and to treat in-kernel JIT lanes as reviewable drift surfaces (`docs/348-design-review-rubric-and-feature-intake.md`).
- Extend juicy lessons and curated references (BPF/eBPF threat model + deprecation policy + Nix profile generation refs), and bump discovery/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).

## 2026-02-27r108

- Add **trust boundary graphs + diffs** so threat boundary drift becomes a compiled, reviewable artifact (`docs/380-trust-boundary-graphs-and-threat-diff.md`, `spec/trust.boundary.graph.schema.json`, `spec/trust.boundary.diff.schema.json`, and examples).
- Extend blast-radius diffs to optionally include **trust boundary drift** (`spec/blast_radius.diff.schema.json`, `spec/examples/blast_radius.diff.json`) and update the taxonomy doc (`docs/106-blast-radius-diff.md`).
- Add an optional lane for **information-flow labels + explicit declassification** (labels at import/portal/export edges; downgrades as receipted transforms) (`docs/381-information-flow-labels-and-declassification.md`, `spec/flow.label.schema.json`, `spec/declass.request.schema.json`, `spec/declass.receipt.schema.json`, and examples).
- Standardize **surface id conventions** (namespacing + stability) to keep registry/diff artifacts usable at scale (`docs/383-surface-ids-namespacing-and-stability.md`).
- Tighten the feature intake rubric to require `trust.boundary.diff` when new crossings are introduced, and refresh archive hygiene stamps (`docs/348-design-review-rubric-and-feature-intake.md`, `docs/98-archive-hygiene.md`).
- Extend curated references and juicy lessons with threat modeling + DIFC pointers and bump version metadata (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).

## 2026-02-27r107

- Add an optional **deterministic concurrency lane** (deterministic scheduling for debug/CI) to shrink replay capsules and tame heisenbugs (`docs/377-deterministic-concurrency-lane.md`), and wire it into the replay-capsule story (`docs/194-debugging-by-lease-and-replay-capsules.md`).
- Add a focused note on **denial-driven policy suggestions**: denials as structured evidence → reviewable policy patches (never auto-approve), integrating with the existing `policy.suggestion` lane and permission-center model (`docs/378-denial-driven-policy-suggestions.md`).
- Add the **surface registry pattern** as a reusable meta-engineering rule (registry + diff + gate + receipt) and connect it to existing contract/UAPI/parser/authority drift surfaces (`docs/379-surface-registry-pattern.md`).
- Expand the optional unikernel lane notes with MirageOS and reproducible unikernel build lessons, and tighten the manifest-as-contract framing (`docs/145-unikernel-lane-rump-solo5.md`).
- Refactor and extend curated references: add deterministic concurrency + unikernel references, add Seatbelt/SBPL profiling references, and remove duplicated Plan 9 archival entries (`docs/32-curated-references.md`).
- Update discovery/version surfaces and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`).

## 2026-02-27r106

- Add a first-class **parser surface registry + diff** so “new parsers” (untrusted bytes → structured objects) become machine-checkable, reviewable drift surfaces (`spec/parser.registry.schema.json`, `spec/parser.diff.schema.json`, and examples).
- Add a focused meta-engineering doc defining parser drift + fuzz gates, and wire it into the surface taxonomy (blast-radius diffs) and review workflow (`docs/376-parser-surface-registry-and-fuzz-gates.md`, `docs/106-blast-radius-diff.md`, `docs/374-authority-diff-schema-and-review-workflows.md`).
- Extend the blast-radius diff schema to allow an optional `parsers` section and update the example accordingly (`spec/blast_radius.diff.schema.json`, `spec/examples/blast_radius.diff.json`).
- Tighten the feature intake rubric so new/broadened parsers must be registered and carry a fuzz/conformance (or proof) story (`docs/348-design-review-rubric-and-feature-intake.md`).
- Refresh curated references and proof-lane docs to include IPC review discipline, fuzzing expectations, and EverParse as an under-copied high-assurance parser wedge (`docs/32-curated-references.md`, `docs/373-proof-artifacts-and-formal-verification-lanes.md`).
- Update discovery surfaces and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`).

## 2026-02-27r105

- Add a machine-checkable **authority diff** artifact (schema + example) so “new authority” becomes a policy-keyable, reviewable diff object (`spec/authority.diff.schema.json`, `spec/examples/authority.diff.json`) and document the review workflow (`docs/374-authority-diff-schema-and-review-workflows.md`).
- Wire `authority.diff` into the authority-graph substrate and blast-radius diff guidance (`docs/366-capability-graphs-and-authority-diff-surfaces.md`, `docs/106-blast-radius-diff.md`) and cross-link from contract diff gates (`docs/370-contract-registries-and-api-diff-gates.md`).
- Tighten the diagnostics ecosystem story by defining an Archivist-style **diagnostics query plane** (selectors + leases + snapshot artifacts) that plugs into the Permission Center and evidence spine (`docs/372-inspect-style-structured-introspection.md`, complements `docs/302-structured-diagnostics-inspect-trees.md`).
- Add an optional lane concept for **proof artifacts** (formal verification outputs treated as supply-chain evidence: bundles + receipts + replay), grounded in seL4 lessons (`docs/373-proof-artifacts-and-formal-verification-lanes.md`).
- Add Genode routing lessons (policy-driven init, nested subsystems, explicit resources) to reinforce hierarchical capability distribution as an under-copied scalability win (`docs/375-genode-init-and-capability-routing-lessons.md`).
- Extend discovery and reference surfaces (juicy lessons items 231–234, curated references for Fuchsia diagnostics protocols, seL4, Genode) and bump archive version metadata (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`, `README.md`).


## 2026-02-27r104

- Add a first-class **contract registry + diff gate** concept (treat userland interfaces like versioned contract surfaces) and wire it into the authority-graph substrate (`docs/370-contract-registries-and-api-diff-gates.md`, `docs/366-capability-graphs-and-authority-diff-surfaces.md`).
- Add a “permission center” concept so portals/brokers/leases can be reviewed, revoked, and auto-expired in one place, with privacy-report-style summaries (`docs/371-permission-center-and-authority-introspection.md`, `docs/369-consent-ledgers-and-permission-review-ui.md`).
- Add schemas + examples for `contract.registry`, `contract.diff`, `uapi.registry`, and `uapi.diff` so registry/diff objects are machine-checkable (`spec/*.schema.json`, `spec/examples/*`).
- Update the blast-radius diff schema to allow optional sections for **contracts**, **UAPI**, and **resources**, matching the documented blast-radius surface taxonomy (`spec/blast_radius.diff.schema.json`, `docs/106-blast-radius-diff.md`).
- Extend discovery/reference surfaces (index wiring, curated references, and juicy lessons items 227–230) and bump archive version metadata (`docs/00-index.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`, `README.md`).


## 2026-02-27r103

- Add an authority-graph substrate so “new authority” can be reviewed as a generation-scoped `authority.graph` snapshot and a diff between generations (`docs/366-capability-graphs-and-authority-diff-surfaces.md`), and wire it into the feature intake rubric (`docs/348-design-review-rubric-and-feature-intake.md`).
- Extend blast-radius diffs to explicitly cover contracts/UAPI/resources and tie the concept to authority-graph diffs (`docs/106-blast-radius-diff.md`, `docs/362-uapi-surface-registry-and-compat-gates.md`).
- Add a reproducible *system generation* lane concept (determinism checks + receipts + diffoscope artifacts) to make fleet drift and supply-chain compromise easier to detect (`docs/367-reproducible-generations-and-determinism-checks.md`).
- Add pledge/unveil-style promise mapping notes so developers can write least-authority intents that compile to Derive promise profiles (`docs/368-pledge-unveil-style-promises-and-derive-profiles.md`).
- Add a consent-ledger/permission-review UI concept to prevent portals and brokers from devolving into silent, permanent exceptions (`docs/369-consent-ledgers-and-permission-review-ui.md`).
- Refactor the juicy lessons index to fix the misplaced `Last updated` tag and add items 223–226, plus extend curated references and index wiring (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`).
- Bump archive version metadata.

## 2026-02-27r102

- Add a kernel UAPI surface registry + compatibility gates concept so syscalls/ioctls/sysctls/devnodes are treated as first-class contract surfaces (`docs/362-uapi-surface-registry-and-compat-gates.md`) and wire it into the design principles + feature intake rubric (`docs/12-design-principles.md`, `docs/348-design-review-rubric-and-feature-intake.md`).
- Add a driver safety tiering posture (Rust-first, user-mode by default, isolate legacy in driver domains) (`docs/363-driver-safety-tiering-rust-and-user-mode.md`) and cross-link it from device backend isolation (`docs/172-device-backend-isolation-bhyve.md`).
- Add an optional live patching lane that treats hotpatching as derived, timeboxed “hotpatch capsules” with apply/remove receipts (`docs/364-live-patching-lane-hotpatch-capsules.md`).
- Add userspace filesystem server notes (puffs/FUSE lessons) to pull filesystem complexity out of kernel space into supervised components (`docs/365-userspace-filesystems-puffs-fuse.md`).
- Extend discovery surfaces: main index wiring, curated references, and juicy lessons items 219–222 (`docs/00-index.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Bump archive version metadata.


## 2026-02-27r101

- Add a capability hygiene style guide that makes attenuation/revocation patterns mechanical (facets, proxies, leases, indirection, membranes) (`docs/357-capability-attenuation-revocation-and-membranes.md`).
- Add a Unified Boot Capsule note (UKI-shaped) to make the boot payload a single signed/measurable artifact with eventlog replay ergonomics (`docs/358-unified-boot-capsules-and-measured-boot-receipts.md`).
- Add slot-based A/B update discipline notes (Android/ChromeOS) to keep boot assessment and rollback semantics crisp even when using ZFS boot environments (`docs/359-slot-based-updates-and-boot-assessment-lessons.md`).
- Add a recovery-environment ergonomics note: derive minimal repair userspaces as normal artifacts (LinuxBoot/u-root lessons) (`docs/360-derived-recovery-images-and-minimal-userspace.md`).
- Add a boundary-safety note from Tock: keep crossing APIs small/synchronous, treat syscall edges as contract surfaces, and fuzz the boundary via harness lanes (`docs/361-safe-crossing-apis-and-boundary-bugs-lessons-from-tock.md`).
- Tighten meta-engineering guardrails: add an explicit “authority is engineered” design principle and require named attenuation/revocation patterns in feature intake (`docs/12-design-principles.md`, `docs/348-design-review-rubric-and-feature-intake.md`).
- Extend discovery surfaces: main index wiring and juicy lessons items 214–218 (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`).
- Bump archive version metadata.

## 2026-02-27r100

- Add a realm-builder-style hermetic integration testing lane where dependency injection is explicit capability routing, producing `testrealm.plan` + `testrealm.receipt` artifacts (`docs/354-realm-builder-style-hermetic-component-tests.md`).
- Add a userspace kernel/driver testing lane (NetBSD rump-kernel lesson) to make kernel CI + fuzzing cheaper and receipted (`docs/355-rump-kernels-and-userspace-driver-testing.md`).
- Add a WIT/Wasm Component Model contract-language note to standardize digestable interface surfaces for polyglot components (`docs/356-wasm-component-model-and-wit-contracts.md`), and wire it into object-capability RPC (`docs/183-object-capability-rpc.md`).
- Tighten the design-review rubric’s test-plan section to require hermetic integration tests + contract conformance tests for new surfaces (`docs/348-design-review-rubric-and-feature-intake.md`).
- Extend curated references with Realm Builder, rump-kernel, and WIT pointers (`docs/32-curated-references.md`) and extend juicy lessons with items 211–213 (`docs/110-juicy-os-lessons.md`).
- Bump archive version metadata.

## 2026-02-27r99

- Add OTP-inspired supervision semantics as a shared, lintable vocabulary for DeriveBSD’s restarters (strategy + restart intensity), with explicit receipts (`docs/349-supervision-trees-and-restart-strategies.md`), and wire into the service lifecycle doc (`docs/239-service-lifecycle-restarters-and-repo.md`).
- Add crash-only + ROC discipline as the default service reliability stance (MTTR-first recovery + recovery receipts) (`docs/352-crash-only-and-roc-for-system-services.md`).
- Add Plan 9 Venti/Fossil-inspired write-once evidence vault lane for receipts, trace slices, and incident bundles (`docs/350-venti-fossil-write-once-archive-store.md`), wired into the evidence spine and flight recorder docs.
- Add an optional “remote capabilities” lane (CapTP/OCapN) to keep cluster/remote control surfaces from devolving into bearer-token drift (`docs/353-captp-ocapn-remote-capabilities.md`).
- Fix a broken CapTP draft-spec link and cross-link OCapN material from `docs/183-object-capability-rpc.md`.
- Extend `docs/110-juicy-os-lessons.md` with items 206–210 and bump “Last updated” tags.

## 2026-02-27r98

- Add a meta-engineering guardrail: a design review rubric + feature intake template so new subsystems land as small, typed, revocable, evidence-producing surfaces (`docs/348-design-review-rubric-and-feature-intake.md`).
- Add four high-signal OS/ecosystem steals and wire them into DeriveBSD’s model:
  - Unit manifests as component declarations (Fuchsia capability routing ergonomics) (`docs/344-derive-unit-manifests-and-capability-routing.md`).
  - Immutable object stores + name→capability-set indirection (Amoeba Bullet/Directory server lessons) (`docs/345-amoeba-bullet-server-and-capability-directories.md`).
  - Resource governance as isolation+exposure+responsibility (Nemesis QoS/accounting mindset) (`docs/346-nemesis-isolation-exposure-responsibility.md`).
  - Checkpointable systems / orthogonal persistence lessons to tighten state-dataset boundaries (`docs/347-orthogonal-persistence-and-checkpointed-systems.md`).
- Tighten archive hygiene to require the rubric for new subsystems and bump stale hygiene metadata (`docs/98-archive-hygiene.md`).
- Update discovery and reference surfaces: index, juicy lessons (items 201–205), curated references, and version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).


## 2026-02-27r97

- Add three high-leverage “ecosystem steals” focused on **interfaces as contracts** and **capability-first IPC**:
  - Singularity lessons: manifest-based programs + contract channels (`docs/339-singularity-manifests-and-contract-channels.md`).
  - Solaris/illumos Doors lessons: FD-first lightweight RPC as capability IPC (`docs/341-doors-lightweight-capability-rpc.md`).
  - Inferno lessons: file-shaped control planes + per-process namespaces (`docs/340-inferno-styx-and-distributed-namespaces.md`).
  - Capability-kernel lessons: KeyKOS/EROS confinement and revocation by indirection (`docs/343-keykos-eros-capability-kernel-lessons.md`).
- Add a reliability direction from MINIX 3: restartable privileged subsystems with explicit state boundaries, expressed as restart budgets + receipts (`docs/342-minix-self-healing-and-reincarnation.md`).
- Tighten the archive’s guardrails by making “crossings are contracts” an explicit design principle and wiring the new references into object-capability RPC (`docs/12-design-principles.md`, `docs/183-object-capability-rpc.md`).
- Wire the new material into discovery surfaces and references (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`) and bump archive version metadata.

## 2026-02-26r96

- Flesh out the vulnerability lane as a first-class, replayable evidence workflow: expand ADR-0015 and RFC-0037, and rewrite the main design doc for vulnerability intel + gates (`docs/60-vulnerability-intel-and-gates.md`, `adrs/ADR-0015-vuln-gates-optional.md`, `rfcs/RFC-0037-vulnerability-gates.md`).
- Add a tight practice note on snapshot-addressed vuln datasets + deterministic query receipts, including why OpenVEX is a good default interchange for noise reduction (`docs/338-vulnerability-snapshots-query-receipts-and-openvex.md`).
- Add schemas + examples for the vulnerability workflow objects: `vuln.db.snapshot`, `vuln.query.receipt`, `vuln.gate.policy`, and `vuln.gate.receipt` (plus matching examples under `spec/examples/`).
- Add small Derive-native wrapper schemas for `sbom.statement` and `vex.statement` so SBOM/VEX evidence can be indexed and cross-linked without standardizing DSSE internals (`spec/sbom.statement.schema.json`, `spec/vex.statement.schema.json`, plus examples).
- Wire the lane into discovery + verification surfaces (index, juicy lessons, curated references, verification matrix) and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/92-verification-matrix.md`, `README.md`).

## 2026-02-26r95

- Flesh out the fleet rollout lane by standardizing multi-hop update path artifacts: add `rollout.graph`, `rollout.assignment`, and `rollout.traversal.receipt` schemas + examples (`spec/rollout.graph.schema.json`, `spec/rollout.assignment.schema.json`, `spec/rollout.traversal.receipt.schema.json`, and matching examples under `spec/examples/`).
- Refactor the fleet rollout doc to clearly separate single-release phasing (`rollout.policy`/`rollout.receipt`) from graph-based upgrade constraints (Cincinnati-shaped DAGs) and optional director assignments (`docs/177-fleet-coordinated-rollouts.md`).
- Add a concise “when you need graphs” note to the staged rollouts doc (`docs/258-staged-rollouts-and-cohorts.md`).
- Refresh curated rollout references with authoritative Cincinnati/Zincati/OSUS/Bottlerocket pointers and update the Omaha protocol link (`docs/32-curated-references.md`).
- Bump archive version metadata (`README.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-26r94

- Add a practical firmware update note focused on **UEFI capsules + ESRT** and fwupd-shaped real-world constraints (stage != apply; ESRT as status surface; conservative one-capsule-per-boot defaults) (`docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`).
- Add a Secure Boot **certificate rotation** note (2011→2023) framing key refresh as a first-class derived operation (inventory + UEFI var plans/receipts + cohort rollout) (`docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`).
- Tighten firmware lane docs and bootchain revocation notes to link the new practice/rotation material and make key refresh a non-optional part of the model (`docs/221-firmware-updates-as-artifacts.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/244-bootchain-revocation-and-allowlists.md`).
- Extend firmware schemas with optional ESRT-derived fields and explicit capsule planning constraints; refresh examples (`spec/fw.device.inventory.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, and matching examples under `spec/examples/`).
- Refresh curated references with authoritative UEFI/LVFS/fwupd sources plus Secure Boot certificate rotation guidance (Microsoft, Dell, Red Hat, LWN), and collapse accidental duplicate lines in the references doc (`docs/32-curated-references.md`).
- Wire the new lane into discovery surfaces and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`).

## 2026-02-26r93

- Add a concrete “boot assessment in practice” doc mapping systemd boot assessment + Fedora greenboot + A/B updates onto DeriveBSD's ZFS boot-environment lane (`docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`).
- Add typed gate-policy input: `boot.health.gate.policy` schema + example (required vs wanted checks, success points, retry bounds) (`spec/boot.health.gate.policy.schema.json`, `spec/examples/boot.health.gate.policy.json`).
- Extend boot health report and boot bless receipt schemas to optionally reference the gate-policy digest, and refresh examples (`spec/boot.health.report.schema.json`, `spec/boot.bless.receipt.schema.json`, `spec/examples/boot.health.report.json`, `spec/examples/boot.bless.receipt.json`).
- Refactor health-gated update docs and wire into discovery surfaces + curated references (`docs/112-health-gated-updates.md`, `docs/241-boot-try-counters-and-boot-assessment.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).

## 2026-02-26r92

- Remove tool-specific citation markers from docs and add a hygiene rule to prevent reintroducing them (`tools/check_consistency.py`).
- Tighten the keyless signing lane with a **bundle-first offline verification** doc plus a `sigstore.bundle` wrapper schema/example, and link publisher identity receipts to the bundle digest (`docs/333-sigstore-bundles-and-offline-verification.md`, `spec/sigstore.bundle.schema.json`, `spec/examples/sigstore.bundle.json`, `spec/publisher.identity.receipt.schema.json`).
- Add an **artifact knowledge graph** doc (GUAC-style) to make SBOM/VEX/provenance operational via local-first queries (`docs/334-artifact-knowledge-graph-and-supply-chain-queries.md`).
- Add `tools/check_version.py` and wire it into `tools/hygiene.py` so version metadata stays consistent (`README.md`, `CHANGELOG.md`).
- Wire new docs into discovery surfaces and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`).

## 2026-02-26r91

- Add a practical measured-boot/TPM attestation doc focusing on **PCR meaning discipline**, stable measurement boundaries (UKI-style thinking), and Keylime-style verifier architecture mapping to Derive artifacts (`docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md`).
- Tighten the measured-boot lane docs to emphasize **PCR registries** (published semantics) and add supporting references (`docs/176-measured-boot-attestation.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/245-boot-measurement-phases-and-pcr-separation.md`, `docs/32-curated-references.md`).
- Extend runtime verified-execution notes with fs-verity-style Merkle authenticity as additional prior art and add references (`docs/103-runtime-verified-execution.md`, `docs/32-curated-references.md`).
- Make TEE attestation reference objects explicitly **signed** (schema + example) and document the intent (`spec/tee.attestation.reference.schema.json`, `spec/examples/tee.attestation.reference.json`, `docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`).
- Update platform posture docs to explicitly call out the shared ‘receipt-first’ contract for TEE attestations (`docs/226-platform-posture-and-attestation-results-as-evidence.md`).
- Bump archive version metadata (`README.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-26r90

- Add an optional lane for **confidential microVMs** using TEEs (SEV-SNP/TDX/CCA) by treating vendor attestation as a first-class evidence lane: reference values, digest-first evidence objects, and signed verifier receipts (`docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`, `docs/331-tee-attestation-in-practice-snp-tdx-and-verifier-services.md`).
- Add schemas + examples for TEE attestation artifacts (`spec/tee.attestation.reference.schema.json`, `spec/tee.attestation.evidence.schema.json`, `spec/tee.attestation.receipt.schema.json`, plus matching examples under `spec/examples/`).
- Wire the lane into discovery surfaces and integration points (main index, juicy lessons, curated references, workload identity, hypervisor backend capabilities, and attester provisioning non-goals).
- Bump archive version metadata (`README.md`).

## 2026-02-26r89

- Add a generic **policy suggestion** artifact (`policy-suggestion`) to unify learn/audit workflows across lanes, with schema + example (`spec/policy.suggestion.schema.json`, `spec/examples/policy.suggestion.json`).
- Refactor learned-profile and learned-network docs to emit `policy.suggestion` objects (rather than bespoke `*.suggestion` pseudo-types) and link the new schema (`docs/326-learned-promise-profiles-and-observation-mode.md`, `docs/328-learned-network-policies-from-flow-receipts.md`).
- Add a first-class workflow for **learning resource budgets from observation** (usage → reviewable diffs) and wire it into discovery surfaces and resource-governance docs (`docs/329-learned-resource-budgets-and-observation-mode.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/285-hierarchical-resource-limits-compilation.md`).
- Refresh curated references to include VPA-style right-sizing and systemd resource-control patterns (`docs/32-curated-references.md`).
- Add `tools/hygiene.py` as a one-command wrapper for archive checks and document it (`docs/98-archive-hygiene.md`).
- Bump archive version metadata (`README.md`).

## 2026-02-26r88

- Add a first-class workflow for **learning network policy from observed flows** (audit mode → reviewable diffs), expressed in terms of egress classes and optional hostname bindings (`docs/328-learned-network-policies-from-flow-receipts.md`).
- Wire the network-learning lane into discovery surfaces (main index, juicy lessons) (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`).
- Refactor curated references to separate the main pointer map from an explicit appendix of concrete authoritative links, and add references for observe-first network policy generation (Cilium audit mode, Kubescape NetworkNeighborhood, Calico log rules) (`docs/32-curated-references.md`).
- Eliminate schema/example drift warnings by adding thin schemas for long-lived authoring-spec examples (`minimal.spec`, `system.spec`, `microvm.spec`), `runtime.manifest`, and a `derive.unit` specialization wrapper (`spec/*.schema.json` + existing `spec/examples/*.json`).
- Document the “examples should have matching schemas” rule in archive hygiene (`docs/98-archive-hygiene.md`) and bump version metadata (`README.md`).

## 2026-02-26r87

- Add an explicit **learn→review→enforce** lane for promise profiles (“observation mode”): run a unit, record accesses/denials, and emit a candidate profile patch as a diffable artifact (`docs/326-learned-promise-profiles-and-observation-mode.md`).
- Wire the learning loop into promise-profile docs and discovery surfaces (`docs/232-service-promise-profiles.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `docs/32-curated-references.md`).
- Add a dedicated note on preventing **shadow trust** (apps shipping their own CA roots) and link it into the trust-bundle lane (`docs/327-shadow-trust-and-system-ca-governance.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`).
- Add `tools/validate_spec_examples.py` to validate examples under `spec/examples/` against schemas under `spec/`, and document it in archive hygiene (`docs/98-archive-hygiene.md`).
- Tighten schema hygiene to reduce cross-schema friction: make `event.record` more extensible (source extensions; evidence can be array or structured object; broaden severity vocabulary) and fix a handful of example/schema mismatches uncovered by the validator.
- Bump archive version metadata (`README.md`).

## 2026-02-26r86

- Add “rootless jails” direction: lease-backed broker + hierarchical-jail delegation so ordinary users can spawn disposable compartments without host-root, while keeping jail creation privileged and auditable (`docs/325-rootless-jails-and-unprivileged-compartments.md`).
- Wire the rootless-jails lane into discovery surfaces (main index, juicy lessons, jail profiles, curated references) (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/150-jail-profiles-and-allowlist-knobs.md`, `docs/32-curated-references.md`).
- Upgrade archive consistency tooling: `tools/check_consistency.py` now also validates internal markdown links (in addition to RFC/ADR ids and backticked repo paths), and document the check (`docs/98-archive-hygiene.md`).
- Bump archive version metadata (`README.md`).

## 2026-02-26r85

- Fix archive consistency: add breakglass workflow doc and wire install/recovery flows to the canonical breakglass lane (`docs/250-breakglass-and-recovery-workflows.md`, `docs/309-installation-and-recovery-as-derived-operations.md`).
- Add a new “key distribution is a transparency problem” direction: transparent key directories + minimal tlogs (Go sumdb / Key Transparency shape) and wire it into discovery surfaces (`docs/324-transparent-key-directories-and-minimal-tlogs.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh packaged-base (pkgbase) grounding with additional primary references and a note about evolution (`docs/111-packaged-base-pkgbase.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Add “layer-aware update construction” notes to the bandwidth/delta story (bootc/rpm-ostree lesson) and update bootc references (`docs/139-bandwidth-efficient-deltas.md`, `docs/133-bootable-oci-host-images-bootc-lessons.md`).
- Bump archive version metadata (`README.md`, `docs/98-archive-hygiene.md`).

## 2026-02-26r84

- Formalize devfs views as a derived operation: compile promise profiles + device grants into `devfs.view.plan`, emit `devfs.view.receipt` on apply, and use `devfs.view.event` for drift/deny incidents (`docs/323-devfs-views-plans-and-receipts.md`, `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`, `spec/examples/devfs.view.*.json`).
- Tighten the device-grants lane to point at the devfs view plan/receipt/event objects and remove the prior open question (`docs/278-device-grants-and-devfs-rulesets.md`).
- Wire devfs views into the runtime-IR story (component descriptors) and day-0 defaults (non-negotiables), plus budgets, discovery surfaces, juicy lessons, and risk register (`docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/97-non-negotiable-behaviors.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`, `README.md`).

## 2026-02-26r83

- Add host networking substrate lane: treat link/bridge objects, addressing, routes, and pf substrate as derived operations (`net.topology.plan` → `net.topology.receipt`) with explicit drift/deny events (`net.topology.event`) (`docs/322-network-topology-and-firewall-as-derived-operations.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`, `spec/examples/net.topology.*.json`).
- Tighten pf + networking mode docs to reference topology receipts and drift posture (`docs/67-pf-anchors-per-instance.md`, `docs/64-networking-modes-mapping.md`).
- Add a non-negotiable behavior: host network topology is derived + receipted (no rc.conf folklore) (`docs/97-non-negotiable-behaviors.md`).
- Extend authority budgets with host network topology mutation as a budget dimension (`docs/298-authority-budgets-and-permission-drift-alarms.md`).
- Add a new risk-register item capturing networking drift and remote-brick failure modes (`docs/266-open-questions-and-risk-register.md`).
- Update discovery surfaces and references (index, juicy lessons, curated references) and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).

## 2026-02-26r82

- Add firmware lane: model firmware posture as evidence (`fw.inventory.receipt`) and treat firmware updates as derived operations spanning reboot stages (`fw.update.plan` → `fw.update.receipt`) (`docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/examples/fw.*.json`).
- Add UEFI variable mutation lane: treat boot/capsule/secureboot variable writes as digest-bound plans and receipts (`uefi.var.set.plan` → `uefi.var.set.receipt`) (`spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`, `spec/examples/uefi.var.set.*.json`).
- Wire firmware posture into compatibility gates and budgets, and add a new risk-register item for platform drift (`docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/266-open-questions-and-risk-register.md`).
- Add a non-negotiable behavior: firmware updates and UEFI variable writes are receipted, policy-gated operations (`docs/97-non-negotiable-behaviors.md`).
- Update discovery surfaces and references (index, juicy lessons, curated references) and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).

## 2026-02-26r81

- Add hardware inventory lane: treat host hardware facts and observed bindings as a privacy-safe evidence object (`docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `spec/hw.inventory.receipt.schema.json`, `spec/examples/hw.inventory.receipt.json`).
- Add hardware compatibility gate lane: preflight checks emit a typed report used to block risky generation switches unless breakglass (`docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.compat.report.schema.json`, `spec/examples/hw.compat.report.json`).
- Add inventory/fingerprinting as an authority budget dimension and wire the lane into budgets (`docs/298-authority-budgets-and-permission-drift-alarms.md`).
- Add a non-negotiable behavior: preflight hardware compatibility by default for host activation (`docs/97-non-negotiable-behaviors.md`).
- Wire into discovery surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/266-open-questions-and-risk-register.md`, `README.md`).

## 2026-02-26r80

- Add kernel tuning lane: treat boot tunables and runtime sysctls as derived operations with typed plans/receipts and explicit drift events (`docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `spec/sysctl.plan.schema.json`, `spec/sysctl.receipt.schema.json`, `spec/sysctl.event.schema.json`, `spec/examples/sysctl.*.json`).
- Add `kmod.event` schema + example for live monitoring/drift alarms and wire into kernel module policy doc (`spec/kmod.event.schema.json`, `spec/examples/kmod.event.json`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`).
- Add “kernel mutation” as an authority budget dimension and add a risk-register item capturing sysctl/kmod drift failure modes (`docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/266-open-questions-and-risk-register.md`).
- Update discoverability surfaces and pointers (index, juicy lessons, curated references) and bump archive version metadata (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).

## 2026-02-26r79

- Add backup lane docs: treat backups/restores as derived operations producing typed plans and receipts (state replication is policy-governed, not external scripting) (`docs/316-backups-and-restores-as-derived-operations.md`).
- Add restore drill notes: continuous recovery testing with quarantine microVM drills, digest-first receipts, and budget/export hygiene (`docs/317-restore-drills-and-continuous-recovery-testing.md`).
- Add schemas + examples: `backup.plan`, `backup.receipt`, and `restore.drill.receipt` (`spec/backup.plan.schema.json`, `spec/backup.receipt.schema.json`, `spec/restore.drill.receipt.schema.json`, `spec/examples/*.json`).
- Wire the lane into the index, juicy lessons, curated references, and risk register; bump archive version metadata.

## 2026-02-26r78

- Add “durable attestation” doc: treat posture as a bounded, queryable time series (receipt chaining + typed transition events + retention budgets) (`docs/315-durable-attestation-and-posture-timelines.md`).
- Extend `attestation.receipt` schema with an optional `timeline` linkage (chain id / sequence / prev receipt digest) and update example (`spec/attestation.receipt.schema.json`, `spec/examples/attestation.receipt.json`).
- Add event-log replay implementation references (tpm2_eventlog, go-eventlog) and extend curated references with measured-boot tooling pointers (`docs/313-boot-manifests-and-eventlog-replay.md`, `docs/32-curated-references.md`).
- Wire the durable-attestation lane into the index, juicy lessons, and risk register; bump archive version metadata.

## 2026-02-26r77

- Add first-class `boot.manifest` object (schema + example) so boot-critical closure can be referenced by Secure Boot binding and measured-boot replay (`spec/boot.manifest.schema.json`, `spec/examples/boot.manifest.json`).
- Add “make measured boot explainable” doc: boot manifests + event-log replay ergonomics, replay tooling hooks, and a clear anti-pattern warning against golden-PCR allowlists (`docs/313-boot-manifests-and-eventlog-replay.md`).
- Add attester provisioning + key lifecycle receipts doc, plus `attester.provision.receipt` schema + example to make enrollment/rotation auditable and operable (`docs/314-attester-provisioning-and-key-lifecycle-receipts.md`, `spec/attester.provision.receipt.schema.json`, `spec/examples/attester.provision.receipt.json`).
- Tighten measured-boot docs to reference the new objects and bump freshness (`docs/176-measured-boot-attestation.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/155-trust-bootstrap.md`).
- Update discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r76

- Add operator access as a leased, certificate-based capability lane (no permanent SSH keys): short-lived SSH certs, role shells, session admission via broker hooks, and wiring to recording + confirmable change-sets (`docs/311-operator-access-leases-and-ssh-certs.md`).
- Add `operator.session` evidence object (schema + example) so every operator session can be attributed, scoped, and correlated to leases/recordings (`spec/operator.session.schema.json`, `spec/examples/operator.session.json`).
- Add policy replay + counterfactual explanation notes to keep policy usable and non-mystical during incidents (`docs/312-policy-replay-and-counterfactual-explanations.md`).
- Update discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.


## 2026-02-26r75

- Make installation and recovery first-class derived operations (installer/recovery images as artifacts; install as change sets; idempotent retryable flows; factory reset as policy-gated) (`docs/309-installation-and-recovery-as-derived-operations.md`).
- Add disk layout plans/receipts: partitioning and pool topology are typed intents and evidence objects, not installer folklore (`docs/310-disk-layout-plans-and-receipts.md`, `spec/disk.layout.plan.schema.json`, `spec/disk.layout.receipt.schema.json`, `spec/examples/disk.layout.*.json`).
- Wire the new lane into discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r74

- Add practical secure-time backend notes (chrony NTS, ntpsec, ntpd-rs, Roughtime quorum) and map them onto DeriveBSD’s `system.time` broker + evidence objects (`docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`).
- Add time-monitor / lie-detection notes: treat time divergence like a transparency problem (proof bundles + monitors + typed alerts) (`docs/308-time-monitors-and-lie-detection.md`).
- Extend `time-event` schema with divergence actions (`quorum-failed`, `divergence-detected`, `misbehavior-proof-captured`) to make time trust failures first-class operational facts (`spec/time.event.schema.json`).
- Tighten TUF-inspired channel metadata doc with an explicit trustworthy-time dependency for expiry checks (`docs/61-channel-metadata-tuf-inspired.md`).
- Update discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r73

- Add a crypto operations portal note: treat signing/decryption as a portalized authority (operations by lease; keys non-exportable by default), borrowing Qubes “split GPG” and platform keystore lessons (`docs/306-crypto-operations-portal-and-split-keys.md`).
- Add crypto operation evidence objects (schemas + examples): `spec/crypto.op.request.schema.json`, `spec/crypto.op.receipt.schema.json`, `spec/examples/crypto.op.*.json`.
- Wire crypto ops into the secrets lane and the budget/drift model (`docs/223-secrets-and-key-management-as-evidence.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`).
- Update discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r72

- Concretize the PKI lane with first-class schemas for trust bundles and issuance plans/receipts (`spec/pki.trust.bundle.schema.json`, `spec/pki.issue.plan.schema.json`, `spec/pki.issue.receipt.schema.json`) and add examples.
- Add trust-store drift control notes: trust bundles as signed store objects, deterministic interop renderers (OpenSSL CAfile / optional p11-kit), and digest-pinned CA handle injection via preopen maps (`docs/304-trust-bundles-and-ca-injection-as-artifacts.md`).
- Add DNS mediation + hostname binding note: broker-resolved hostnames with optional DNS query receipts to avoid TOCTOU and make name lookups auditable (`docs/305-dns-mediation-and-hostname-binding.md`, `spec/net.dns.query.receipt.schema.json`).
- Tighten `net-flow-receipt` schema to optionally reference DNS provenance (`dns_query_receipt_digest`) and update examples (`spec/net.flow.receipt.schema.json`, `spec/examples/net.flow.receipt.json`).
- Extend component descriptor lane to declare PKI/trust dependencies; update `derive.unit` schema + example and wire PKI outputs into the compiled runtime manifests story (`spec/derive.unit.schema.json`, `spec/examples/derive.unit.web.service.json`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`).
- Extend authority budgets to cover trust/PKI and DNS evidence retention (avoid silent trust drift and privacy-toxic receipts) (`docs/298-authority-budgets-and-permission-drift-alarms.md`).
- Wire updates into discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r71

- Add structured diagnostics lane (Inspect-style trees) with an archivist-shaped ingestion/query surface; diagnostics are accessed by lease and exports are receipted (`docs/302-structured-diagnostics-inspect-trees.md`).
- Add flight recorder tracing lane: bounded circular buffers, promoted into incident bundles on triggers; governed by budgets and leases (`docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`).
- Extend component descriptors to declare diagnostics intent; update `derive.unit` schema + example and wire diagnostics into the “compiled runtime manifests” story (`spec/derive.unit.schema.json`, `spec/examples/derive.unit.web.service.json`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`).
- Extend authority budgets to include diagnostics/retention constraints (so observability doesn’t become ambient surveillance) (`docs/298-authority-budgets-and-permission-drift-alarms.md`).
- Wire these into discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r70

- Add an optional verified lazy rootfs lane (composefs/eStargz/Nydus-shaped): on-demand mounts as a policy-bound transport adapter with plans/receipts (`docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`).
- Add time-travel snapshots as leases ("previous versions" UX without ambient snapshot exposure): portalized snapshot views with policy re-check + evidence hooks (`docs/300-time-travel-snapshots-as-leases.md`).
- Add P2P distribution + swarm caches notes (Dragonfly lesson): treat P2P as an optional transport adapter, peers untrusted, bytes always verified (`docs/301-p2p-distribution-and-swarm-caches.md`).
- Extend component descriptor lane to reference rootfs trees and transport hints; update `derive.unit` schema and add a starter example (`spec/derive.unit.schema.json`, `spec/examples/derive.unit.web.service.json`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`).
- Wire these into discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r69

- Add a unifying “how it runs” source lane: component descriptors compiled into canonical runtime manifests (service graphs, capability routing, Capsicum preopen maps, mount views, stratum stacks, state footprints, promise profiles, health checks) (`docs/297-component-descriptors-and-compiled-runtime-manifests.md`).
- Add a stub `derive.unit` source schema to anchor the canonical IR discussion (`spec/derive.unit.schema.json`).
- Add authority budgets + permission drift alarms to stop capability creep early; budgets are policy objects evaluated against compiled IR with timeboxed exceptions as receipts (`docs/298-authority-budgets-and-permission-drift-alarms.md`).
- Wire both into discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r68

- Add an oblivious-sandboxing launcher note: standardize Capsicum adoption via preopen maps (directory FDs + rights masks), making capability mode the default for services (`docs/294-oblivious-sandboxing-launchers.md`).
- Add multi-origin userland “strata” notes (Bedrock-inspired): treat ecosystem trees as signed, digest-bound strata composed into explicit mount views, so “where did this come from?” is always answerable (`docs/295-strata-and-multi-origin-userlands.md`).
- Add a tight feature-harvest rubric to keep the archive ambitious without drifting (bake-in requires input+plan+receipt) (`docs/296-feature-harvest-rubric.md`).
- Tighten mount-view notes with Plan 9 namespace-group framing and stronger references (`docs/264-mount-namespaces-and-union-views.md`).
- Wire the new lanes into discoverability surfaces (index, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-26r67

- Expand "spec as data" frontend notes: add Nickel as a candidate authoring layer, tighten CUE/Pkl guidance, and emphasize compiler-digest pinning + traceability (`docs/79-derive-spec-frontends.md`).
- Add Haiku/BeOS BFS-inspired notes on attribute-indexed metadata + live queries, mapped to DeriveBSD origin labels, quarantine workflows, and evidence search (`docs/293-attribute-indexed-metadata-and-live-queries.md`).
- Wire both into discoverability surfaces (index, mile-high directions, juicy lessons, curated references, risk register) and bump archive version metadata.

## 2026-02-25r66

- Add a remote assistance lane: compose screencast/remote-control/data-transfer/network leases into a single session envelope, making support events visible, revocable, and bundle-friendly (`docs/291-remote-assistance-sessions-as-evidence.md`, `spec/support.session.schema.json`).
- Add a terminal session recording lane: tlog-shaped structured TTY recordings as leased authority (output-only by default) with typed metadata for replay/redaction/export (`docs/292-terminal-session-recording-as-evidence.md`, `spec/tty.session.recording.schema.json`).
- Wire both lanes into non-negotiables, the main index reading paths, juicy lessons, the risk register, and curated references.

## 2026-02-25r65

- Add an exec integrity lane: “no unverified execution” as a first-class, compilable policy with receipts; includes a MAC/veriexec backend sketch (`docs/289-exec-integrity-policy-and-verified-execution.md`).
- Add exec integrity evidence objects (schemas + examples): `spec/exec.integrity.policy.schema.json`, `spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`, `spec/examples/exec.integrity.*.json`.
- Add a keyless signing lane: Sigstore-shaped publisher identity receipts as digest-bound identity evidence (not promotion authority) (`docs/290-keyless-signing-and-publisher-identity-receipts.md`).
- Add `publisher.identity.receipt` schema + example: `spec/publisher.identity.receipt.schema.json`, `spec/examples/publisher.identity.receipt.json`.
- Wire both lanes into the main index, non-negotiables, mile-high directions, juicy lessons, curated references, and the risk register (`docs/00-index.md`, `docs/97-…`, `docs/99-…`, `docs/110-…`, `docs/32-…`, `docs/266-…`).


## 2026-02-25r64

- Tighten the workload identity + secretless deploys lane (SPIFFE/SPIRE-shaped): an identity broker issues short-lived credentials as leases, binds issuance to what is actually running (digest/attestation), and emits issuance receipts (`docs/181-workload-identity-and-secretless-deploys.md`).
- Add identity evidence objects (schemas + examples): `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`, `spec/examples/workload.identity.lease.json`, `spec/examples/workload.identity.issue.receipt.json`.
- Wire the lane into the networking brokers, the main index, mile-high directions, juicy lessons, curated references, and the risk register (`docs/281-…`, `docs/286-…`, `docs/00-index.md`, `docs/99-…`, `docs/110-…`, `docs/32-…`, `docs/266-…`).

## 2026-02-25r63

- Add a multiparty approvals lane: quorum approvals as evidence and explicit separation of duties (decide vs ship), grounded in existing consent request/receipt objects (docs/288-multiparty-approvals-and-separation-of-duties.md).
- Refactor two-person integrity to point at the generic approval substrate and wire into release authority, breakglass, and networking grant workflows (docs/107-two-person-integrity.md, docs/256-consent-ux-contract.md, docs/260-release-authority-policy-and-key-management.md).
- Update non-negotiables so high-risk operations are mediated and receipted (approvals are never social-only) (docs/97-non-negotiable-behaviors.md).
- Update index, mile-high directions, juicy lessons, curated references, and risk register for discoverability and to track approval-fatigue/bypass risks (docs/00-index.md, docs/99-…, docs/110-…, docs/32-…, docs/266-…).


## 2026-02-25r62

- Add a formal methods lane: design-level model checking (TLA+) treated as evidence, with a `modelcheck.receipt` contract and starter model scaffolding (`docs/287-formal-model-checking-and-invariants.md`, `docs/models/bootenv_switch.tla`, `docs/models/bootenv_switch.cfg`; new schema+example: `spec/modelcheck.receipt.schema.json`, `spec/examples/modelcheck.receipt.json`).
- Refactor reading-path numbering in the main index and wire the new lane into discoverability surfaces (index, mile-high directions, juicy lessons, curated references, risk register) (`docs/00-index.md`, `docs/99-…`, `docs/110-…`, `docs/32-…`, `docs/266-…`).

## 2026-02-25r61

- Add an inbound networking lane symmetric to outbound egress: inbound listen broker + listen classes + lease-based grants + listen receipts, compiled to PF anchors (socket activation / inetd lesson) (`docs/286-inbound-listen-broker-and-firewall-leases.md`; new schemas + examples: `spec/net.listen.policy.schema.json`, `spec/net.listen.grant.schema.json`, `spec/net.listen.receipt.schema.json`, `spec/examples/net.listen.*.json`).
- Refactor the main index to remove duplicated entries and wire in the new inbound lane; cross-link outbound networking to the inbound symmetry lane (`docs/00-index.md`, `docs/281-…`).
- Update juicy lessons, curated references, and risk register to track inbound exposure risks and improve discoverability (`docs/110-…`, `docs/32-…`, `docs/266-…`).

## 2026-02-25r60

- Made “switching boots” a first-class, evidencable operation: boot environment switch plan + receipt; adds `docs/284-bootenv-switching-as-evidence.md` and new schema+examples (`spec/bootenv.switch.plan.schema.json`, `spec/bootenv.switch.receipt.schema.json`, `spec/examples/bootenv.switch.plan.json`, `spec/examples/bootenv.switch.receipt.json`). Wired into ZFS BE docs and try-counter/health gate lanes (`docs/69-host-generations-bectl.md`, `docs/241-boot-try-counters-and-boot-assessment.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`).
- Added a tighter “how to compile resource policy” companion for `rctl/racct`: `docs/285-hierarchical-resource-limits-compilation.md` (wired into `docs/247-resource-budgets-and-limits-as-evidence.md` and `docs/143-resource-controls-rctl-racct-cpuset.md`), and expanded curated references with `rctl.conf(5)` + handbook pointers (`docs/32-curated-references.md`).

## 2026-02-25r59

- Add a first-class outbound networking lane: network egress broker + policy-defined egress classes + lease-based grants + flow receipts (Little Snitch/OpenSnitch lesson) (`docs/281-network-egress-broker-and-consent.md`; new schema + example: `spec/net.egress.policy.schema.json`, `spec/examples/net.egress.policy.json`; wired into `docs/00-index.md` and promise-profile linting in `docs/271-…`).
- Add an operable witness-network lane: witness cosigning checkpoints as a tunable quorum with offline verification as the default (`docs/282-witness-cosigning-checkpoints-and-witness-networks.md`; wired into `docs/00-index.md`, `docs/99-…`, `docs/110-…`, `docs/266-…`; minor tighten to `docs/259-…`).
- Tighten “trustworthy time” to align with existing time objects and LKGT: refactor the Roughtime/LKGT doc to use `time-proof-bundle` + time sync snapshots/receipts; add LKGT fields to time sync schema surfaces; add a bridge doc for NTS/Roughtime/LKGT wiring (`docs/142-…`, `docs/283-…`; schema tweaks: `spec/time.sync.snapshot.schema.json`, `spec/time.sync.receipt.schema.json`).
- Update mile-high directions, juicy lessons, curated references, and risk register for discoverability (`docs/99-…`, `docs/110-…`, `docs/32-…`, `docs/266-…`).

## 2026-02-25r58

- Add origin labels + quarantine attributes: a first-class “where did this file come from?” lane that standardizes imports across downloads/USB/shares and makes sanitize-first opening the default (`docs/280-origin-labels-and-quarantine-attributes.md`).
- Add import evidence objects (plan + receipt) and an origin record schema, plus examples (`spec/content.origin.schema.json`, `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`; `spec/examples/content.import.*.json`).
- Wire the lane into index, mile-high directions, juicy lessons, curated references, and risk register; cross-link from sanitization portal, USB quarantine workflow, and data-transfer portals (`docs/00-index.md`, `docs/99-…`, `docs/110-…`, `docs/32-…`, `docs/266-…`, `docs/267-…`, `docs/279-…`, `docs/205-…`).

## 2026-02-25r57

- Add a `/dev` authority lane: device grants + devfs rulesets so device-node exposure is explicit, lease-based, and evidencable (`docs/278-…`; wired into promise-profile vocabulary and device isolation domains).
- Add a USB quarantine + removable media workflow: no automount into the trusted domain, USB stacks in a device domain, and sanitize-then-import as the default for untrusted files (`docs/279-…`; cross-links to device isolation, input authority, sanitization portal, and airgap mirror kits).
- Update index, juicy lessons, curated references, and the risk register to make the device posture discoverable and tracked (`docs/00-index.md`, `docs/110-…`, `docs/32-…`, `docs/266-…`).

## 2026-02-25r56

- Add a kernel-module discipline lane: module allowlist policy + preload plan + load receipts so “what code was in the kernel?” is answerable (`docs/276-…`; new schemas + examples: `spec/kmod.*.schema.json`, `spec/examples/kmod.*.json`; wired into `docs/00-index.md`, `docs/110-…`, `docs/266-…`, and `docs/230-…`).
- Add a boot-loader verification sketch: verify kernel/modules for a chosen generation while keeping a constrained, receipted boot override surface (`docs/277-…`; wired into `docs/00-index.md`, `docs/110-…`, `docs/266-…`).
- Update curated references with securelevel + kld manpages and FreeBSD loader verification pointers (`docs/32-curated-references.md`).

## 2026-02-25r55

- Add a continuous fuzzing lane as evidence: fuzz receipts, crash cases, and corpus sets as first-class artifacts that can optionally gate promotion (`docs/274-continuous-fuzzing-farm.md`; wired into `docs/00-index.md`, `docs/110-…`, `docs/32-…`, `docs/266-…`; touches `docs/234-…`, `docs/166-…`).
- Add automated bisection + root-cause certificates: regression localization over Plan digests, optional ddmin-style difference minimization, and signed blame evidence objects for rollback/graft decisions (`docs/275-root-cause-certificates-and-bisection.md`; wired into `docs/00-index.md`, `docs/110-…`, `docs/99-…`, `docs/266-…`).
- Update curated references with syzkaller/syzbot, delta debugging, and git bisect pointers (`docs/32-curated-references.md`).

## 2026-02-25r54

- Add an operable sealed-secret lane for TPM-backed secrets: design explicitly around PCR brittleness with policy-authorized PCR policies, define how unseal attempts emit receipts, and map to measured-boot + ZFS encryption + portable homes (`docs/272-sealed-secrets-attested-unsealing.md`; wired into `docs/223-…`, `docs/269-…`, `docs/266-…`, `docs/00-index.md`, `docs/99-…`).
- Add an air-gap “happy path” lane: mirror kits + sneakernet updates with quarantine→promote semantics, strict verification + freshness policy, receipts, and optional delta packs (`docs/273-airgap-mirror-kits-and-sneakernet-updates.md`; wired into `docs/138-…`, `docs/266-…`, `docs/00-index.md`, `docs/99-…`).
- Extend juicy lessons + curated references with the new lanes (`docs/110-…`, `docs/32-…`).


## 2026-02-25r53

- Tighten the least-authority “promise profile” lane by defining a curated promise vocabulary + concrete lint rules to keep profiles reviewable and fail-closed (`docs/271-promise-profile-vocabulary-and-lint.md`), and wire it into pledge/unveil mindset + juicy lessons + index (`docs/117-…`, `docs/232-…`, `docs/110-…`, `docs/00-index.md`).
- Flesh out two previously too-thin ADRs into actionable, reviewable decisions:
  - TUF-inspired channel metadata ADR now specifies the minimal role set, client invariants, and evidence emission requirements (`adrs/ADR-0016-tuf-inspired-channel-metadata.md`).
  - in-toto + DSSE attestation ADR now clarifies envelope/statement responsibilities and how DeriveBSD binds Spec/Lock/Plan + policy evidence (`adrs/ADR-0004-attestations-intoto-dsse.md`).

## 2026-02-25r52

- Add “portable homes” ecosystem lane (systemd-homed lesson): home areas as portable encrypted containers with embedded user records, plus attach/unlock receipts (`docs/269-portable-home-areas-and-user-records.md`).
- Add a crisp AppVM persistence contract for desktop compartments: template + private + volatile (+ optional portable home mounts) (`docs/270-appvm-storage-private-volatile-and-home-areas.md`).
- Wire new lanes into the main index, mile-high directions, juicy lessons, curated references, and risk register; tighten desktop AppVM doc and user env doc to cross-link (`docs/00-index.md`, `docs/99-mile-high-directions.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/266-open-questions-and-risk-register.md`, `docs/268-desktop-appvms-and-portalized-apps.md`, `docs/162-user-environments.md`).

## 2026-02-25r51

- Add “human-scale safety” ecosystem lanes:
  - Sanitization portal + disposable sandbox workflow (Dangerzone lessons) (`docs/267-sanitization-portal-and-disposable-sandboxes.md`)
  - Desktop AppVMs + portalized apps stance (Qubes/Flatpak lessons) (`docs/268-desktop-appvms-and-portalized-apps.md`)
- Wire new lanes into the main index, mile-high directions, juicy lessons, and curated references (`docs/00-index.md`, `docs/99-mile-high-directions.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Tighten the open questions register to explicitly track desktop stance + safe file handling (`docs/266-open-questions-and-risk-register.md`).

## 2026-02-25r50

- Add new “greenfield ecosystem” design docs:
  - Feature flags + constraints as typed inputs (`docs/262-feature-flags-and-constraints.md`)
  - Flake-style input graphs + scoped registries (`docs/263-flake-style-input-graphs-and-registries.md`)
  - Filesystem views as capabilities (Plan 9 union lessons) (`docs/264-mount-namespaces-and-union-views.md`)
  - Portable service bundles (attach/detach ops tooling lane) (`docs/265-portable-service-bundles.md`)
  - Open questions + risk register (`docs/266-open-questions-and-risk-register.md`)
- Extend the “Juicy lessons” index with the new ecosystem items (`docs/110-juicy-os-lessons.md`).
- Update the main index and curated references for discoverability (`docs/00-index.md`, `docs/32-curated-references.md`).

## 2026-02-25r49

- Add transparency monitor + witness gossip lane: new doc + RFC; new `transparency.monitor.policy`, `transparency.monitor.snapshot`, and `transparency.monitor.alert.event` schemas + examples (`docs/259-…`, `rfcs/RFC-0191-…`, `spec/transparency.monitor.*.schema.json`, `spec/examples/transparency.monitor.*.json`).
- Add release authority policy lane: new doc + RFC; new `release.authority.policy`, `release.publish.receipt`, and `release.halt.event` schemas + examples; extend `release.capsule` bindings with optional authority/publish receipt digests; extend `release.transparency.entry` with optional `authority_policy_digest` (`docs/260-…`, `rfcs/RFC-0192-…`, `spec/release.*.schema.json`, examples).
- Add rollout privacy constraints: new doc + RFC; extend `rollout.policy` cohorting with optional `privacy` block (entropy budget, max cohorts, min bucket size, salt rotation) and update example (`docs/261-…`, `rfcs/RFC-0193-…`, `spec/rollout.policy.schema.json`).
- Tighten cross-linking and references: update main index, staged rollout doc, juicy lessons, and curated references.
## 2026-02-25r48

- Introduce a common transparency proof bundle schema `transparency.proof` and refactor `export.transparency.entry` to reference it; add example (`spec/transparency.proof.schema.json`, `spec/examples/transparency.proof.json`, updated `spec/export.transparency.entry.schema.json` + example).
- Add release capsule + publication transparency lane: new docs + RFC, new `release.capsule` and `release.transparency.entry` schemas + examples (`docs/257-…`, `rfcs/RFC-0189-…`, `spec/release.*.schema.json`, `spec/examples/release.*.json`).
- Add staged rollout + cohort lane: new doc + RFC, new `rollout.policy` and `rollout.receipt` schemas + examples (`docs/258-…`, `rfcs/RFC-0190-…`, `spec/rollout.*.schema.json`, `spec/examples/rollout.*.json`).
- Wire new concepts into the main index, juicy lessons, and curated references.

## 2026-02-25r47

- Add export transparency log lane: new doc + RFC, new `export.transparency.entry` schema + example; extend export policy/receipt and incident bundles with optional transparency digests (`docs/254-…`, `rfcs/RFC-0186-…`, `spec/export.transparency.entry.schema.json`, `spec/examples/export.transparency.entry.json`, `spec/export.policy.schema.json`, `spec/export.receipt.schema.json`, `spec/incident.bundle.schema.json`).
- Add policy-constrained transport adapters as evidence: new doc + RFC, new `transport.policy` + `transport.receipt` schemas + examples; wire optional digests into export policy/receipt + incident bundles (`docs/255-…`, `rfcs/RFC-0187-…`, `spec/transport.*.schema.json`, `spec/examples/transport.*.json`).
- Add a consent UX contract lane: new doc + RFC, new `consent.request` + `consent.receipt` schemas + examples; wire optional consent receipt digest into export receipts (`docs/256-…`, `rfcs/RFC-0188-…`, `spec/consent.*.schema.json`, `spec/examples/consent.*.json`).
- Tighten cross-linking: wire new export/transport/consent/transparency concepts into the main index, incident bundle guidance, juicy lessons, and curated references.

## 2026-02-25r46

- Add export policies + receipts + support-bundle export portal: new doc + RFC, new `export.policy` and `export.receipt` schemas + examples (`docs/251-…`, `rfcs/RFC-0183-…`, `spec/export.policy.schema.json`, `spec/export.receipt.schema.json`, `spec/examples/export.*.json`).
- Add lease envelope as a cross-lane join object: new doc + RFC, new `lease.envelope` schema + example, and extend `lease.snapshot` entries with optional `envelope_digest` (`docs/252-…`, `rfcs/RFC-0184-…`, `spec/lease.envelope.schema.json`, `spec/examples/lease.envelope.json`, `spec/lease.snapshot.schema.json`).
- Add `bundle.plan` as a typed selection+transform manifest for deterministic bundle-min exports: new doc + RFC, new schema + example, and extend incident bundles with optional plan/policy/receipt include knobs (`docs/253-…`, `rfcs/RFC-0185-…`, `spec/bundle.plan.schema.json`, `spec/examples/bundle.plan.json`, `spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`).
- Wire new concepts into evidence spine, incident bundle guidance, deterministic redaction notes, lease registry notes, juicy lessons, curated references, and main index.

## 2026-02-25r43

- Add SBAT-shaped bootchain revocation/allowlists as a first-class policy surface: new doc + RFC, and new `bootchain.policy` schema + example (`docs/244-bootchain-revocation-and-allowlists.md`, `rfcs/RFC-0176-bootchain-policy-and-revocation.md`, `spec/bootchain.policy.schema.json`, `spec/examples/bootchain.policy.json`).
- Add measured-boot phase marker ergonomics notes + RFC (`docs/245-boot-measurement-phases-and-pcr-separation.md`, `rfcs/RFC-0177-boot-measurement-phases.md`) and wire into measured-boot overview (`docs/176-measured-boot-attestation.md`).
- Add causality graphs as an evidence index + minimal bundle enabler: new doc + RFC, new `causality.graph` schema + example, and extend incident bundles to optionally include causality graph and bootchain policy digests (`docs/246-causality-graphs-and-minimal-evidence-bundles.md`, `rfcs/RFC-0178-causality-graphs-as-evidence.md`, `spec/causality.graph.schema.json`, `spec/examples/causality.graph.json`, `spec/incident.bundle.schema.json`).
- Tighten archive hygiene: refactor juicy lessons tail to remove duplicated numbering and add new items; extend curated references with SBAT/boot assessment and measured-boot phase sources; update main index + evidence spine links.

## 2026-02-25r42

- Add boot try-counters + automatic boot assessment deep dive (docs/241, RFC-0173) and introduce `boot-bless-receipt` schema + example.
- Generalize “commit confirmed” as confirmable change-sets with auto-revert semantics (docs/242, RFC-0174) and add `change-confirm-receipt` schema + example; extend `change-receipt` to carry confirmation window metadata.
- Make service ownership boundaries first-class evidence pointers: add service contract handle doc (docs/243, RFC-0175), add `svc-contract-handle` schema + example, and wire optional `contract_handle_digest` into `svc.snapshot` and `svc.event`.
- Refactor docs index to remove repeated 2026-02-25 section blocks; expand curated references + juicy lessons with boot assessment + generalized commit-confirmed lessons.

## 2026-02-25r41

- Add SMF-inspired service lifecycle + restarter separation deep dive (docs/239) and RFC-0171; tighten svc.event + svc.snapshot schemas with canonical state enum and optional instance_id; update examples.
- Add dynamic service identities concept (docs/240) and RFC-0172; extend svcdb schema + example with optional identity block for host services.
- Tighten FMA references (docs/213) and expand curated references (SMF restarter docs + DynamicUser sources); update index and juicy lessons.

## 2026-02-25r40

- Fix consistency-check regressions: correct breakglass doc reference to A/B lifecycle doc; add missing platform lockdown receipt + event schemas + examples.
- Add portal-activated services + socket activation doc (docs/238) and RFC-0170; extend svcdb schema docs and example with activation endpoints.
- Cross-link socket activation lesson to the new doc/RFC and update index.


## 2026-02-25r39

- Add process contracts / service boundary deep dive (docs/235, RFC-0167) and cross-link from service supervision.
- Add breakglass + recovery mode lane (docs/236, RFC-0168) with typed schemas + examples for breakglass grants/receipts/events.
- Add lint reports as typed artifacts (docs/237, RFC-0169, new schema + example) and wire into LLM-facing interface guidance.
- Fix incident bundle schema drift: add missing PKI include fields and extend bundle include knobs to cover breakglass receipts and lint reports.
- Update index, glossary, curated references, juicy lessons, and evidence spine cross-links.

## 2026-02-25r38

- Add anykernel / rump kernel inspired direction note (docs/234) and references (niche but high leverage for kernel testing and safer subsystem reuse).


## 2026-02-25r37

- Add promise profiles as typed artifacts (docs/232, RFC-0166, new schema + example) and wire into svcdb as optional `security.promise_profile_digest`.
- Add verified execution as an ops evidence lane (docs/233) with `exec-verify-*` schemas + examples; extend change sets with `apply-exec-verify` step op and update example ordering.
- Refactor RFC-0072 and verified-exec research notes to align with the evidence spine and current schema conventions.
- Update index, curated references, juicy lessons, evidence spine cross-links, and examples.

## 2026-02-25r36

- Add Evidence spine overview (docs/229) and wire it into the main reading path.
- Add lockdown levels as a first-class posture output (docs/230, RFC-0164).
- Add explicit A/B update lifecycle semantics over ZFS boot environments (docs/231, RFC-0165).


## 2026-02-24r35

- Add PKI + identity lifecycle lane: trust bundles, issuance plans, issuance receipts, and typed PKI events (docs/228, RFC-0163, new schemas + examples).
- Extend change sets with an `apply-pki` step op and update example ordering (`spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Extend incident bundle schema + example to reference PKI evidence (trust bundle + recent issuance receipts) by digest (metadata-first).
- Update index/glossary/curated references and add a new juicy lesson capturing “trust roots + cert renewals must be receipted”.

## 2026-02-24r34

- Add operational time discipline lane: inventories, plans, snapshots, receipts, requirements, and typed time events (docs/227, RFC-0162, new schemas + examples).
- Extend change sets with a `require-time-sync` step op and update example ordering (`spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Extend incident bundle schema + example to include time evidence digests by default when enabled.
- Wire time sync snapshots into health-gated updates as an optional gate input.
- Cross-link time discipline with the event journal, change sets, incident bundles, time authority docs, curated references, glossary, index, and juicy lessons.

## 2026-02-24r33

- Add platform posture + verifier receipts lane: `attestation-reference` → `attestation-receipt` (+ `attestation-requirement`), with a typed `attestation-event` stream (docs/226, RFC-0161, new schemas + examples).
- Extend secret grants to support attestation requirements/receipts as first-class constraints (`spec/secret.grant.schema.json`, example updated).
- Extend change sets with a `require-attestation` step op and update example ordering (`spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Extend incident bundle schema + example to include posture evidence digests (boot attestation + verifier receipts) by default when enabled.
- Cross-link measured boot, secrets, change sets, incident bundles, event journal, index/glossary, curated references, and juicy lessons.

## 2026-02-24r32

- Add a storage evidence lane: pool inventory, health snapshots, scrub plans/receipts, and typed storage events (docs/225, RFC-0160, new schemas + examples).
- Wire storage health into health-gated updates (optional gate input), change-set ordering, structured event journal, fault management inputs, and incident bundle defaults.
- Update incident bundle schema + example to reference storage evidence by digest (metadata-first).
- Fix and extend index + glossary ordering (and add storage terminology).

## 2026-02-24 (archive revision, crash artifacts + symbolication as evidence)

- Added crash lane: `crash-report` evidence + `crash-event` typed events (`docs/224-crash-artifacts-and-symbolication-as-evidence.md`, `rfcs/RFC-0159-crash-artifacts-and-symbolication-as-evidence.md`).
- Added schemas + examples (`spec/crash.report.schema.json`, `spec/crash.event.schema.json`, `spec/examples/crash.*.json`).
- Extended incident bundle schema + example to reference crash reports and (optional) dump digests (`spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`).
- Cross-linked service supervision, fault management, the event journal, and incident bundles to treat crashes as first-class evidence.


## 2026-02-24 (archive revision, secrets and key management as evidence)

- Added secrets lane: `secret-policy` + `secret-grant` + `secret-snapshot` + `secret-receipt` + `secret-event`; wired into the ops spine (`docs/223-secrets-and-key-management-as-evidence.md`, `rfcs/RFC-0158-secrets-and-key-management-as-evidence.md`).
- Added schemas + examples (`spec/secret.*.schema.json`, `spec/examples/secret.*.json`).
- Extended `change-set` schema + example with an `apply-secrets` step (`spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Extended incident bundle schema + example with safe secret snapshot/receipt pointers (`spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`).
- Updated index, glossary, curated references, and juicy lessons.

## 2026-02-24 (archive revision, resource governance as evidence)

- Added resource governance lane: `resource-policy` → `resource-receipt` → `resource-snapshot` + `resource-event`; wired into the ops spine (`docs/222-resource-governance-as-evidence.md`, `rfcs/RFC-0157-resource-governance-as-evidence.md`).
- Added schemas + examples: `resource-policy`, `resource-receipt`, `resource-snapshot`, `resource-event` (`spec/resource.*.schema.json`, `spec/examples/resource.*.json`).
- Extended `change-set` schema + example with an `apply-resource-policy` step (`spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Updated incident bundle defaults, event journal integration, and health-gated update checks to recognize resource snapshots/pressure as gate inputs.

## 2026-02-24 (archive revision, firmware updates as artifacts)

- Added firmware updates lane: inventory + explicit plans + receipts; wired into change sets, incident bundles, health gating, and the event journal (`docs/221-firmware-updates-as-artifacts.md`, `rfcs/RFC-0156-firmware-updates-as-artifacts.md`).
- Added schemas + examples: `fw-device-inventory`, `fw-update-plan`, `fw-update-receipt` (`spec/fw.*.schema.json`, `spec/examples/fw.*.json`).
- Extended `change-set` schema + example with an `apply-firmware` step (`spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Extended incident bundle schema + example with firmware inventory/receipt pointers (`spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`).
- Updated indexes, glossary, curated references, and juicy lessons to cross-link the new lane (`docs/00-index.md`, `docs/01-glossary.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-24 (archive revision, time-travel debugging as first-class ops evidence)

- Operationalized record/replay debugging by wiring replay capsules into the ops spine: change sets, incident bundles, and the structured event journal (`docs/220-operational-time-travel-debugging.md`, `rfcs/RFC-0155-replay-capsules-in-ops-spine.md`).
- Added `debug-event` schema + example for typed debug broker milestones in the structured journal (`spec/debug.event.schema.json`, `spec/examples/debug.event.json`).
- Extended `change-set` step schema + example with an optional record-on-failure hook referencing a `debug.record.grant` (`spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Extended incident bundle schema + example to explicitly reference replay capsule digests (`spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`).
- Updated indexes, glossary, curated references, and juicy lessons to cross-link the new lane (`docs/00-index.md`, `docs/01-glossary.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-24 (archive revision, change sets + apply engine)

- Added a unifying orchestration primitive: `change-set` (compose config/state/service transitions) + `change-receipt` (single execution outcome with per-step receipt pointers) (`docs/219-change-sets-and-apply-engine.md`, `rfcs/RFC-0154-change-sets-and-apply-engine.md`, schemas + examples under `spec/`).
- Added optional `correlation` identifiers to the common event envelope (`event.record`) for change-level grouping.
- Wired change receipts into health gating, event journal cross-links, incident bundle defaults, and the config/state lanes (`docs/112-health-gated-updates.md`, `docs/215-...`, `docs/216-...`, `docs/218-...`, `docs/217-...`).
- Updated index, glossary, curated references, and juicy lessons.

## 2026-02-24 (archive revision, configuration transactions + receipts)

- Added configuration transactions lane: `config-plan`, `config-snapshot`, `config-receipt` with optional commit-confirmed safety for risky changes (Junos/OpenWrt lessons) (`docs/218-configuration-transactions-and-receipts.md`, `rfcs/RFC-0153-configuration-transactions-and-receipts.md`, schemas + examples under `spec/`).
- Wired config evidence into health-gated updates, the event journal, service supervision, and incident bundles (`docs/112-health-gated-updates.md`, `docs/215-structured-event-log-as-evidence.md`, `docs/214-service-supervision-health-as-evidence.md`, `docs/216-incident-snapshots-and-support-bundles.md`).
- Updated index, glossary, curated references, and juicy lessons.

## 2026-02-24 (archive revision, state datasets + migrations as evidence)

- Added state datasets + migrations lane (Bottlerocket/OSTree/ZFS-hold lessons): `statedb`, `state-snapshot`, `state-migration-plan`, `state-migration-receipt` (`docs/217-state-datasets-and-migrations-as-evidence.md`, `rfcs/RFC-0152-state-datasets-and-migrations-as-evidence.md`, schemas + examples under `spec/`).
- Wired state evidence into health-gated updates and incident bundles (`docs/112-health-gated-updates.md`, `docs/216-incident-snapshots-and-support-bundles.md`) and cross-linked from the event journal doc (`docs/215-structured-event-log-as-evidence.md`).
- Updated index, glossary, curated references, and juicy lessons (and fixed a misplaced "Last updated" line in `docs/110-juicy-os-lessons.md`).

## 2026-02-24 (archive revision, incident snapshots + support bundles)

- Added incident/support bundle lane: `incident.bundle` evidence object + payload digest, enabling bounded, verifiable “support bundles” with privacy-safe defaults (`docs/216-incident-snapshots-and-support-bundles.md`, `rfcs/RFC-0151-incident-snapshots-and-support-bundles.md`).
- Added schema + example (`spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`).
- Linked bundles into health-gated rollback, fault management escalation, service supervision integration points (`docs/112-...`, `docs/213-...`, `docs/214-...`, `docs/215-...`).
- Updated index/glossary/curated references (`docs/00-index.md`, `docs/01-glossary.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-24 (archive revision, structured event journal as evidence)

- Added a host-local **structured event journal** lane (`event.record` envelope + `event.segment` segment metadata) to unify service, fault, and audit/policy events (`docs/215-structured-event-log-as-evidence.md`, `rfcs/RFC-0150-structured-event-journal-as-evidence.md`).
- Added schemas + examples (`spec/event.record.schema.json`, `spec/event.segment.schema.json`, `spec/examples/event.*.json`).
- Refactored `svc-event` and `fault-event` schemas to align with the common envelope (standard `at`, added `event_id`/`source` where missing) and linked fault/service events into the event journal (`docs/213-...`, `docs/214-...`, `docs/192-...`).
- Updated curated references with ETW / systemd journal / OpenTelemetry logs model pointers (`docs/32-curated-references.md`).

## 2026-02-24 (archive revision, service supervision + health evidence)

- Added a first-class service supervision data model: `svcdb` (compiled service database), `svc.snapshot` (runtime state), `svc.event` (supervision event stream) (`docs/214-service-supervision-health-as-evidence.md`, `rfcs/RFC-0149-service-supervision-health-evidence.md`).
- Added schemas + examples (`spec/svcdb.schema.json`, `spec/svc.snapshot.schema.json`, `spec/svc.event.schema.json`, `spec/examples/svc*.json`).
- Expanded SMF/s6-rc/service-jail references and tied service health into update health gating (`docs/114-service-manifests-smf-lessons.md`, `docs/173-compiled-service-database-bundles.md`, `docs/112-health-gated-updates.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, fault management architecture + ops self-healing evidence)

- Added an FMA-inspired **fault management** lane as evidence objects + policy-gated self-healing (`docs/213-fault-management-architecture.md`, `rfcs/RFC-0148-fault-management-architecture.md`).
- Added fault evidence schemas + examples (`spec/fault.*.schema.json`, `spec/examples/fault.*.json`).
- Wired health-gated updates to optionally consult `fault.snapshot` (`docs/112-health-gated-updates.md`).
- Updated indexes + curated references (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, portal sessions + permission store + location/print portals)

- Added portal primitives for **long-lived sessions** and **remembered permissions** (`docs/210-portal-sessions-and-permission-store.md`, `rfcs/RFC-0145-portal-sessions-and-permission-store.md`, `spec/portal.session.schema.json`, `spec/portal.permission.*.schema.json`, examples).
- Added **Location portal** lane (coarse-first, receipted) (`docs/211-location-portal.md`, `rfcs/RFC-0146-location-portal.md`, `spec/ui.location.*.schema.json`, examples).
- Added **Printing portal** lane (prepare/submit, brokered spool) (`docs/212-printing-portal.md`, `rfcs/RFC-0147-printing-portal.md`, `spec/ui.print.*.schema.json`, examples).
- Wired portal spine to reference session/permission conventions (`docs/179-portals-and-powerbox.md`, `docs/185-portal-consent-and-audit-receipts.md`, plus screencast/AV docs).
- Updated indexes and references (`docs/00-index.md`, `docs/01-glossary.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-24 (archive revision, screencast/remote desktop + AV capture portals)

- Added optional **ScreenCast + RemoteDesktop portal** lane: screen sharing and remote control as leased grants with optional receipts; paired remote control with input-authority posture (`docs/208-screencast-and-remote-desktop-portals.md`, `rfcs/RFC-0143-screencast-and-remote-desktop-portals.md`, `spec/ui.screencast.*.schema.json`, `spec/ui.remotedesktop.*.schema.json`, examples under `spec/examples/`).
- Added optional **camera + audio capture portal** lane: AV devices as brokered streams with leases/indicators and optional receipts (`docs/209-camera-and-audio-capture-portals.md`, `rfcs/RFC-0144-camera-and-audio-capture-portals.md`, `spec/ui.camera.*.schema.json`, `spec/ui.audio.capture.*.schema.json`, examples under `spec/examples/`).
- Wired these lanes into portals, main index, glossary, juicy lessons, and curated references (`docs/179-portals-and-powerbox.md`, `docs/00-index.md`, `docs/01-glossary.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Added a small note on policy-driven portal lockdown/kill-switches as prior art (XDG Lockdown backend) (`docs/179-portals-and-powerbox.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).


## 2026-02-24 (archive revision, notifications + input authority)

- Added optional **notification portal** lane: non-observing publish/withdraw via a host broker with receipts; click-to-activate routes through intent routing (`docs/206-notification-portal-non-observing.md`, `rfcs/RFC-0141-notification-portal-non-observing.md`, `spec/ui.notification.*.schema.json`, examples under `spec/examples/`).
- Added optional **input authority** lane: brokered input streams, Secure Attention Key (trusted prompt mode), and HID danger-class posture; introduced device classification evidence as policy input (`docs/207-input-authority-secure-attention-and-hid-risk.md`, `rfcs/RFC-0142-input-authority-secure-attention.md`, `spec/ui.input.stream.grant.schema.json`, `spec/ui.secure_attention.receipt.schema.json`, `spec/device.profile.schema.json`, examples under `spec/examples/`).
- Wired these lanes into portals, device domains, the main index, glossary, juicy lessons, and curated references (`docs/179-portals-and-powerbox.md`, `docs/204-device-isolation-domains.md`, `docs/00-index.md`, `docs/01-glossary.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, device domains + data transfer portals)

- Added optional **device isolation domains** (“driver VMs”) pattern for isolating risky hardware (USB/NIC/GPU) behind brokered attach/detach leases, with evidence-bearing grants/receipts (`docs/204-device-isolation-domains.md`, `rfcs/RFC-0139-device-isolation-domains.md`, `spec/device.attach.*.schema.json`, examples under `spec/examples/`).
- Added optional **data transfer portals** (clipboard / drag&drop) as capability grants with redaction-profile binding and optional transfer receipts (`docs/205-data-transfer-portals-clipboard-and-dnd.md`, `rfcs/RFC-0140-data-transfer-portals.md`, `spec/ui.datatransfer.*.schema.json`, examples under `spec/examples/`).
- Wired the new lanes into the portal and redaction “spine” docs (`docs/179-portals-and-powerbox.md`, `docs/195-deterministic-redaction-transforms.md`) and updated the index/juicy-lessons/reference pointers.

## 2026-02-24 (archive revision, in-toto layouts + full TUF adapter lane)

- Added optional supply-chain workflow policy lane based on in-toto **layouts** (step/functionary declaration) with evidence-bearing policy and verification receipts (`docs/202-in-toto-layouts-and-step-policy.md`, `rfcs/RFC-0137-in-toto-layouts-and-step-policy.md`, `spec/supplychain.layout.policy.schema.json`, `spec/supplychain.verify.receipt.schema.json`, examples under `spec/examples/`).
- Added optional **full TUF metadata adapter** lane for channel publishing/ingestion and delegations interoperability (`docs/203-full-tuf-metadata-adapter.md`, `rfcs/RFC-0138-full-tuf-metadata-adapter.md`).
- Updated cross-links: provenance/attestation docs now point to the layout lane; channel metadata notes point to the full TUF adapter; refreshed curated references and glossary.

## 2026-02-24 (archive revision, secure time + net egress capabilities)

- Added secure time bootstrapping lane (NTS + Roughtime shaped) with signed `time-source-policy` and `time-proof-bundle` evidence; extended `time-snapshot` with optional `proof_bundle_digest` (`docs/200-secure-time-bootstrapping.md`, `rfcs/RFC-0135-secure-time-bootstrapping.md`, `spec/time.source.policy.schema.json`, `spec/time.proof.bundle.schema.json`).
- Added network egress as a capability-mediated service (brokered egress grants + flow receipts) (`docs/201-network-egress-as-capability.md`, `rfcs/RFC-0136-network-egress-as-capability.md`, `spec/net.egress.grant.schema.json`, `spec/net.flow.receipt.schema.json`).
- Refreshed cross-links: Capsicum/Casper hardening and VNET compartments now point to the network egress lane; capability graph lint calls out `system.net` as a “danger edge”.

## 2026-02-24 (archive revision, bookmarks + intent routing)

- Added persistent file capability (bookmark) lane notes and RFC (security-scoped bookmarks / document-portal shaped; portal-claim flow; explicit revocation evidence) (`docs/198-persistent-file-capabilities-bookmarks.md`, `rfcs/RFC-0133-persistent-file-capabilities-bookmarks.md`).
- Added intent routing (plumber/intents) lane notes and RFC (typed intent requests; policy + rules resolution; capability-mediated handoff; route receipts) (`docs/199-intent-routing-and-plumbing.md`, `rfcs/RFC-0134-intent-routing-and-plumbing.md`).
- Added schemas + examples: `spec/fs.bookmark.schema.json`, `spec/fs.bookmark.revoke.schema.json`, `spec/intent.request.schema.json`, `spec/intent.route.receipt.schema.json` and examples under `spec/examples/`.
- Integrated new lanes into portals, main index, glossary, juicy lessons, and curated references (`docs/179-portals-and-powerbox.md`, `docs/00-index.md`, `docs/01-glossary.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, activation broker capsets + time/entropy authority)

- Added capability activation + escrow lane notes and RFC (generalized socket activation; restart-safe handle escrow; named capsets + claim receipts) (`docs/196-capability-activation-and-escrow.md`, `rfcs/RFC-0131-capability-activation-and-escrow.md`).
- Added time + entropy authority lane notes and RFC (time/RNG as policy-governed inputs; deterministic profiles; optional virtual clocks; time snapshots for replay) (`docs/197-time-and-rng-authority.md`, `rfcs/RFC-0132-time-and-rng-authority.md`).
- Added activation capset + claim schemas + examples (`spec/activation.capset.schema.json`, `spec/activation.claim.schema.json`, `spec/examples/activation.capset.json`, `spec/examples/activation.claim.json`).
- Added time authority grant + time snapshot schemas + examples (`spec/time.authority.grant.schema.json`, `spec/time.snapshot.schema.json`, `spec/examples/time.authority.grant.json`, `spec/examples/time.snapshot.json`).
- Wired new lanes into portals, process topology, host activation notes, scenario tests, repro capsules, main index, juicy lessons, and curated references (`docs/179-portals-and-powerbox.md`, `docs/96-process-topology.md`, `docs/86-host-activation-rcd-and-service-jails.md`, `docs/188-scenario-tests-multimachine.md`, `docs/39-repro-capsules.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/01-glossary.md`).

## 2026-02-24 (archive revision, replay capsules + deterministic redaction transforms)

- Added record/replay debugging lane notes and RFC (explicit recording grants; replay capsules; portal-mediated interactive workflows) (`docs/194-debugging-by-lease-and-replay-capsules.md`, `rfcs/RFC-0129-debugging-by-lease-and-replay-capsules.md`).
- Added deterministic redaction transforms lane notes and RFC (privacy filtering as signed, digestable artifacts + receipts) (`docs/195-deterministic-redaction-transforms.md`, `rfcs/RFC-0130-deterministic-redaction-transforms.md`).
- Added debug recording grant + replay capsule schemas + examples (`spec/debug.record.grant.schema.json`, `spec/debug.replay.capsule.schema.json`, `spec/examples/debug.record.grant.json`, `spec/examples/debug.replay.capsule.json`).
- Added redaction transform + receipt schemas + examples (`spec/redaction.transform.schema.json`, `spec/redaction.receipt.schema.json`, `spec/examples/redaction.transform.json`, `spec/examples/redaction.receipt.json`).
- Extended trace capsule schema with optional redaction proof bundle and tightened the meaning of `redaction_profile_digest` to reference `redaction.transform` artifacts (`spec/trace.capsule.schema.json`, `spec/trace.stream.grant.schema.json`, `spec/examples/trace.capsule.json`).
- Wired new lanes into repro capsules, observability evidence, portals, capability graph notes, main index, juicy lessons index, and curated references (`docs/39-repro-capsules.md`, `docs/120-observability-explainability-dtrace.md`, `docs/179-portals-and-powerbox.md`, `docs/189-capability-graph-lint-and-viz.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/192-observability-as-capability.md`, `docs/186-policy-modules-wasm.md`).

## 2026-02-24 (archive revision, observability-as-capability + resource budget grants)

- Added observability-as-capability lane notes and RFC (diagnostics routed as authority; leased trace grants; broker owns power tools) (`docs/192-observability-as-capability.md`, `rfcs/RFC-0127-observability-as-capability.md`).
- Added trace grant + trace capsule schemas + examples (`spec/trace.stream.grant.schema.json`, `spec/trace.capsule.schema.json`, `spec/examples/trace.stream.grant.json`, `spec/examples/trace.capsule.json`).
- Added resource budget capabilities lane notes and RFC (delegable envelopes; enforcement mapped to rctl/racct/cpuset; optional usage receipts) (`docs/193-resource-budget-capabilities.md`, `rfcs/RFC-0128-resource-budget-capabilities.md`).
- Added resource budget grant + usage receipt schemas + examples (`spec/resource.budget.grant.schema.json`, `spec/resource.budget.usage.schema.json`, `spec/examples/resource.budget.grant.json`, `spec/examples/resource.budget.usage.json`).
- Wired new lanes into observability evidence doc, resource governance, capability graph tooling, main index, juicy lessons index, and curated references (`docs/120-observability-explainability-dtrace.md`, `docs/65-resource-governance.md`, `docs/143-resource-controls-rctl-racct-cpuset.md`, `docs/189-capability-graph-lint-and-viz.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, cache witness quorums + DDC toolchain trust lane)

- Added cache witness quorum lane notes (Trustix-style reproducibility corroboration) and RFC (`docs/190-cache-witness-quorums-trustix.md`, `rfcs/RFC-0125-cache-witness-quorums.md`).
- Added cache witness statement + quorum receipt schemas + examples (`spec/cache.witness.statement.schema.json`, `spec/cache.witness.quorum.schema.json`, `spec/examples/cache.witness.statement.json`, `spec/examples/cache.witness.quorum.json`).
- Added DDC + bootstrappable toolchain lane notes and RFC (`docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`, `rfcs/RFC-0126-diverse-double-compiling-toolchain-trust.md`).
- Added toolchain DDC result schema + example (`spec/toolchain.ddc.result.schema.json`, `spec/examples/toolchain.ddc.result.json`).
- Wired the new lanes into cache trust docs, remote cache threat model, toolchain bootstrap notes, witness rebuilders, build records, and archive indexes/references.

## 2026-02-24 (archive revision, scenario tests + capability graph tooling)

- Added scenario tests as first-class artifacts (multi-machine; bhyve-native) (`docs/188-scenario-tests-multimachine.md`, `rfcs/RFC-0123-scenario-tests-multimachine.md`).
- Added scenario manifest schema + example (`spec/test.scenario.manifest.schema.json`, `spec/examples/test.scenario.manifest.json`).
- Added capability graph lint/viz lane (`docs/189-capability-graph-lint-and-viz.md`, `rfcs/RFC-0124-capability-graph-lint-viz.md`).
- Added capability graph schema + example (`spec/capability.graph.schema.json`, `spec/examples/capability.graph.json`).
- Extended `caproute` docs to reference `capability.graph` tooling view (`docs/140-capability-routing-manifests.md`).
- Extended test receipts doc with scenario test note (`docs/166-test-receipts-and-promotion-gates.md`).
- Updated system extensions doc with boot-timing limits (`docs/122-system-extensions.md`).
- Updated indexes/references (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, policy-as-Wasm + witnessed transparency checkpoints)

- Added policy modules compiled to WebAssembly lane notes and RFC (policy as digest-pinned artifacts; sandboxed runtime) (`docs/186-policy-modules-wasm.md`, `rfcs/RFC-0121-policy-modules-wasm.md`).
- Added policy module evidence schema + example (`spec/policy.module.schema.json`, `spec/examples/policy.module.json`).
- Added witnessed transparency checkpoints lane notes and RFC (split-view defense via witness cosigning / gossip) (`docs/187-witnessed-transparency-checkpoints.md`, `rfcs/RFC-0122-witnessed-transparency-checkpoints.md`).
- Added generic log checkpoint receipt schema + example (`spec/log.checkpoint.receipt.schema.json`, `spec/examples/log.checkpoint.receipt.json`).
- Integrated pointers into policy engine options/traces and transparency lane docs (`docs/85-policy-engine-options-and-traces.md`, `docs/30-policy-engine.md`, `docs/59-transparency-log-rekor.md`, `docs/131-sigsum-lightweight-transparency.md`).
- Updated main index, juicy lessons index, and curated references (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, attenuation tokens + portal consent receipts)

- Added attenuating delegation token lane notes and RFC (Macaroons/Biscuit-shaped) (`docs/184-attenuating-delegation-tokens.md`, `rfcs/RFC-0119-attenuating-delegation-tokens.md`).
- Added capability token metadata schema + example (redacted; store digests only) (`spec/capability.token.schema.json`, `spec/examples/capability.token.json`).
- Added portal consent + audit receipt notes and RFC (`docs/185-portal-consent-and-audit-receipts.md`, `rfcs/RFC-0120-portal-consent-receipts.md`).
- Added portal consent receipt schema + example (`spec/portal.consent.schema.json`, `spec/examples/portal.consent.json`).
- Integrated consent receipts + token lane pointers into portals, qrexec-style RPC policy, and credential broker docs (`docs/179-portals-and-powerbox.md`, `docs/135-qrexec-style-rpc-policy.md`, `docs/151-factotum-style-credential-broker.md`).
- Updated main index, juicy lessons index, and curated references (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, leases + object-capability RPC)

- Added capability lease + revocation pattern notes and RFC (`docs/182-capability-leases-and-revocation.md`, `rfcs/RFC-0117-capability-leases-and-revocation.md`).
- Added object-capability RPC lane notes and RFC (Cap'n Proto / OCapN lessons) (`docs/183-object-capability-rpc.md`, `rfcs/RFC-0118-object-capability-rpc.md`).
- Added portal revocation evidence schema + example (`spec/portal.revoke.schema.json`, `spec/examples/portal.revoke.json`) and extended portal grants with optional `lease_id` (`spec/portal.grant.schema.json`, `spec/examples/portal.grant.json`).
- Integrated leases + ocap RPC into portals, qrexec-style RPC policy, and capability routing docs (`docs/179-portals-and-powerbox.md`, `docs/135-qrexec-style-rpc-policy.md`, `docs/140-capability-routing-manifests.md`).
- Updated main index, juicy lessons index, and curated references (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, workload identity + secretless deploys)

- Added SPIFFE/SPIRE-shaped workload identity lane notes and RFC: host-local Workload Identity Agent issues short-lived identity documents (SVID-style) bound to derived plan/closure/runtime digests (`docs/181-workload-identity-and-secretless-deploys.md`, `rfcs/RFC-0116-workload-identity-and-secretless-deploys.md`).
- Added workload identity grant evidence schema + example (`spec/workload.identity.grant.schema.json`, `spec/examples/workload.identity.grant.json`).
- Extended secrets delivery and microVM injection docs with an identity-gated (secretless) lane (`docs/63-secrets-sealing-and-delivery.md`, `docs/28-config-and-secrets-injection.md`).
- Linked credential broker operations to workload identity as the preferred scaling pattern (`docs/151-factotum-style-credential-broker.md`).
- Updated the main index, juicy lessons index, and curated references to include the workload identity lane (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).

## 2026-02-24 (archive revision, attestation + staged rollouts + sigstore adapters)

- Added measured boot + remote attestation lane notes and RFC (RATS-shaped), defining evidence objects `boot.manifest` + `boot.attestation` and an optional verifier receipt pattern (`docs/176-measured-boot-attestation.md`, `rfcs/RFC-0111-measured-boot-attestation.md`).
- Added boot attestation JSON schema + example (`spec/boot.attestation.schema.json`, `spec/examples/boot.attestation.json`).
- Added fleet-coordinated staged rollout lane notes and RFC inspired by Cincinnati/Zincati and wave schedules (`docs/177-fleet-coordinated-rollouts.md`, `rfcs/RFC-0112-fleet-coordinated-rollouts.md`).
- Added Sigstore/Cosign keyless signing adapter lane notes and RFC to bridge OCI registry ecosystems without weakening Derive verification (`docs/178-sigstore-keyless-signing-adapter.md`, `rfcs/RFC-0113-sigstore-adapter.md`).
- Updated indexes and references (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`) and integrated pointers into Secure Boot, TPM identity, rollout, verification matrix, and OCI transport docs (`docs/51-secure-boot-integration.md`, `docs/70-tpm-and-host-identity.md`, `docs/35-workload-rollout-rollback.md`, `docs/92-verification-matrix.md`, `docs/74-oci-transport-and-layering.md`).

- Added portals / powerbox broker notes to make Capsicum and compartments usable for dynamic access without reintroducing ambient authority (`docs/179-portals-and-powerbox.md`, `rfcs/RFC-0114-portals-and-powerbox.md`).
- Added capability-mode dynamic linking strategy notes (link-then-cap + brokered plugin opens) (`docs/180-capability-mode-dynamic-linking.md`, `rfcs/RFC-0115-capability-mode-dynamic-linking.md`).
- Added portal grant evidence schema + example (`spec/portal.grant.schema.json`, `spec/examples/portal.grant.json`).
- Updated process topology, Capsicum hardening, pledge/unveil ergonomics, qrexec mapping, and curated references to point at portals + the dynamic linking pattern (`docs/96-process-topology.md`, `docs/49-capsicum-casper-hardening.md`, `docs/117-pledge-unveil-mindset.md`, `docs/135-qrexec-style-rpc-policy.md`, `docs/32-curated-references.md`).


## 2026-02-23 (archive revision, network compartments + variants + retention ergonomics)

- Added VNET jail lane notes: treat VNET jails + `epair(4)` as first-class **network compartments** for fetch/publish/control-plane domains (`docs/171-vnet-jails-network-compartments.md`, `rfcs/RFC-0106-vnet-jails-network-compartments.md`).
- Added hypervisor hardening lane notes: isolate emulated device backends as separate workers (inspired by OpenBSD `vmd(8)` device hardening work) (`docs/172-device-backend-isolation-bhyve.md`, `rfcs/RFC-0107-device-backend-isolation.md`).
- Added compiled service database + bundles notes (s6-rc lesson) to improve explainability while keeping `rc.d` as executor (`docs/173-compiled-service-database-bundles.md`, `rfcs/RFC-0108-compiled-service-database.md`).
- Added “specialisations/variants within a generation” notes for safe-mode and role-mode switching (`docs/174-specialisations-and-variants.md`, `rfcs/RFC-0109-specialisations-and-variants.md`).
- Added pins/roots + garbage-collection retention model notes (Nix GC-roots lesson) (`docs/175-pins-roots-and-garbage-collection.md`, `rfcs/RFC-0110-pins-roots-and-gc.md`).
- Updated juicy lessons index, main index, and curated references to link these additions (`docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `docs/32-curated-references.md`).

## 2026-02-23 (archive revision, repro variation harness + HuJSON policy + jail profiles)

- Added reproducibility variation harness notes (reprotest-style environment variation checks, diffoscope reports, optional stabilization lane) (`docs/148-reproducibility-variation-harness-reprotest.md`).
- Added HuJSON-based human policy sources compiled to JCS-canonical JSON for stable hashing and signing (`docs/149-human-policy-hujson-and-canonicalization.md`).
- Added jail profile notes treating FreeBSD jail allowlist knobs and devfs rulesets as derived, evidence-bearing policy outputs (`docs/150-jail-profiles-and-allowlist-knobs.md`).
- Updated juicy lessons index with items 40–42, updated main index, verification matrix, and curated references to link new lanes (`docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `docs/92-verification-matrix.md`, `docs/32-curated-references.md`).

## 2026-02-23 (archive revision, capability routing + build records)

- Added Fuchsia-inspired capability routing manifest notes (explicit authority grants as a derived, diffable graph) (`docs/140-capability-routing-manifests.md`, `rfcs/RFC-0092-capability-routing-manifests.md`).
- Added Debian `.buildinfo`-inspired Build Record notes to strengthen witness rebuilding and hostile-builder evidence (`docs/141-build-records-buildinfo-and-rebuilders.md`, `rfcs/RFC-0093-build-records-buildinfo.md`).
- Updated juicy lessons index and main index to link new items (`docs/110-juicy-os-lessons.md`, `docs/00-index.md`).
- Updated witness rebuilders doc to reference build records / `.buildinfo` practice (`docs/116-witness-rebuilders-diffoscope.md`).
- Updated curated references to include Fuchsia capability routing and Debian buildinfo pointers (`docs/32-curated-references.md`).
- Minor SMF + pledge/unveil ergonomics refinements (`docs/114-service-manifests-smf-lessons.md`, `docs/117-pledge-unveil-mindset.md`).

## 2026-02-23 (archive revision, RPC policy + REAPI + offline bundles + deltas + rollback indices)

- Added qrexec-style cross-compartment RPC policy notes (deny-by-default mediated calls + evidence objects) (`docs/135-qrexec-style-rpc-policy.md`).
- Added Remote Execution API (REAPI) mapping for builder pools (CAS + ActionCache semantics) (`docs/136-remote-execution-api-builder-pools.md`).
- Added activation-time anti-rollback notes (monotonic rollback indices; health-gated advancement) (`docs/137-anti-rollback-rollback-index.md`).
- Added offline signed update bundle lane notes (RAUC/fwup lessons; air-gap friendly artifact container) (`docs/138-offline-signed-update-bundles.md`).
- Added bandwidth-efficient delta lane notes (OSTree static deltas lessons; delta artifacts as first-class objects) (`docs/139-bandwidth-efficient-deltas.md`).
- Updated curated references, juicy lessons index, verification matrix, and main index to link these additions (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`, `docs/92-verification-matrix.md`, `docs/00-index.md`).

## 2026-02-23 (archive revision, transparency + OCI-host + declarative pipelines)

- Added Sigsum transparency lane notes (lightweight inclusion proofs + witness tree heads) (`docs/131-sigsum-lightweight-transparency.md`, `rfcs/RFC-0088-sigsum-transparency-lane.md`).
- Added SCITT ledger receipt lane notes for publishing attestations/provenance into transparent registries (`docs/132-scitt-ledger-receipts.md`, `rfcs/RFC-0089-scitt-ledger-receipts.md`).
- Added bootable-OCI host image transport notes (bootc lessons; DeriveBSD import/export over OCI as transport) (`docs/133-bootable-oci-host-images-bootc-lessons.md`, `rfcs/RFC-0090-bootable-oci-host-images.md`).
- Added declarative build pipeline notes (apko/melange/Wolfi lessons; optional restricted recipe lane) (`docs/134-declarative-image-pipelines-apko-melange.md`, `rfcs/RFC-0091-declarative-image-pipelines.md`).
- Updated verification matrix and main index to include optional transparency evidence and new docs (`docs/92-verification-matrix.md`, `docs/00-index.md`).
- Updated OCI transport doc with explicit “host OS over OCI” section (`docs/74-oci-transport-and-layering.md`).
- Updated curated references and juicy lessons index with new pointers (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).

## 2026-02-23 (archive revision)

- Expanded TUF-inspired channel metadata docs with concrete client-side invariants (`docs/61-channel-metadata-tuf-inspired.md`, `docs/62-replay-rollback-freeze.md`).
- Strengthened health-gated update notes with A/B-style “boot success is explicit” artifacts and additional references (`docs/112-health-gated-updates.md`).
- Added observability-as-explainability note integrating DTrace with audit evidence objects (`docs/120-observability-explainability-dtrace.md`).
- Expanded verified execution research notes (NetBSD veriexec + FreeBSD MAC/veriexec pointers; derived allowlist concept) (`docs/53-verified-exec-mac-veriexec.md`).
- Updated curated references with NetBSD veriexec, pledge/unveil man pages, Bottlerocket (TUF + rollback), TPM/measured boot pointer, and DTrace (`docs/32-curated-references.md`).
- Extended “Juicy OS lessons” index with image-first update patterns, verified-exec, and observability (`docs/110-juicy-os-lessons.md`).
- Updated index to link new observability doc (`docs/00-index.md`).

- Added new “juicy lessons” expansions:
  - Jailed hypervisor workers (bhyve-in-jail) (`docs/121-jailed-hypervisor-workers.md`).
  - System extensions for immutable bases (`docs/122-system-extensions.md`).
  - Ignition-style first-boot provisioning pattern (`docs/123-ignition-style-firstboot.md`).
  - virtio-9p as a restricted optional config channel (`docs/124-virtio-9p-injection-channel.md`).
  - Per-jail hardening knobs (secadm mindset) (`docs/125-hardening-knobs-per-jail.md`).
- Updated microVM posture + config injection docs to reflect jailed workers, virtio-9p caveats, and first-boot provisioning split (`docs/41-microvm-security-posture.md`, `docs/28-config-and-secrets-injection.md`).
- Expanded OCI transport notes with Kata Containers lessons for “microVM containers” compatibility lane (`docs/74-oci-transport-and-layering.md`).
- Expanded curated references with authoritative links for bhyve-in-jail, virtio-9p/p9fs, Ignition, system extensions, HardenedBSD secadm, and Kata (`docs/32-curated-references.md`).
- Extended “Juicy OS lessons” index with new items 13–17 (`docs/110-juicy-os-lessons.md`) and updated main index to link new docs (`docs/00-index.md`).

- Added `docs/00-index.md` as the primary navigation entry point.
- Refactored `README.md` to stay short and delegate navigation to the index.
- Fixed stale/broken internal references (RFC/ADR pointers); all backticked repo-path references now resolve.
- Added `adrs/ADR-0009-artifact-verification.md` to formalize mandatory digest+signature verification and replay protections.
- Made previously abbreviated doc pointers explicit (hardening + rollback/freeze docs).
- Added `docs/attic/` scaffolding for “stale but preserved” material.
- Expanded `docs/02-derive-core.md` with an explicit identity/digest chain (Spec→Lock→Plan→Artifact).
- Expanded `docs/09-cli-ux.md` with `verify/attest/vm` command stubs.

## 2026-02-23 (closure + verification pass)

- Added closure verification docs: `docs/90-closure-proof.md`, `docs/92-verification-matrix.md`.
- Added builder distrust doc: `docs/91-hostile-builders.md`.
- Added RFC: `rfcs/RFC-0060-closure-proofs.md`.
- Updated store/closure notes to point at closure proofs (`docs/56-store-layout-and-digests.md`).
- Updated security/supply-chain docs to reference closure proofs + hostile builders.
- Canonicalized bhyve IO notes: moved old `docs/attic/36-bhyve-io-channels-notes.md` into `docs/attic/` and made `docs/36-bhyve-io-channels.md` a pointer; expanded `docs/72-bhyve-io-channels.md` with vsock stance.
- Improved curated references (fixed mkimg link; added ZFS, rctl/cpuset, ATF/Kyua, nmdm, MAC/veriexec reviews).
- Added missing “Last updated” stamps across docs for consistent maintenance.

## 2026-02-23 (policy binding + blast-radius pass)

- Added policy decision records: `docs/93-policy-decision-records.md`.
- Added runtime blast-radius contract (microVM defaults + opt-ins): `docs/94-runtime-blast-radius-contract.md`.
- Added RFCs: `rfcs/RFC-0061-policy-decision-records.md`, `rfcs/RFC-0062-runtime-blast-radius-contract.md`.
- Added minimal schemas + examples for policy decisions and closure artifacts under `spec/`.
- Updated: `docs/02-derive-core.md`, `docs/30-policy-engine.md`, `docs/33-runtime-manifest-schema.md`, `docs/90-closure-proof.md`, `docs/92-verification-matrix.md`, `docs/00-index.md`.

## 2026-02-23 (explainability + trust-policy + least-authority pass)

- Added explainability contract: `docs/95-explainability-contract.md` (evidence-backed explain outputs).
- Added process topology guidance: `docs/96-process-topology.md` (role separation, least authority).
- Added RFCs: `rfcs/RFC-0063-explainability-contract.md`, `rfcs/RFC-0064-process-topology.md`.
- Added trust policy schema + example: `spec/trust.policy.schema.json`, `spec/examples/trust.policy.json`.
- Expanded trust/channels doc to make trust policy data-first: `docs/57-namespaces-channels-trust.md`.
- Expanded RFC-0034 with the new schema + pointers.
- Updated verification + trust docs to reference trust policy and explainability gating: `docs/92-verification-matrix.md`, `docs/46-cache-trust-model.md`, `docs/00-index.md`.


## 2026-02-23

- Integrated mile-high brainstorm directions into archive: deployments-as-commits, CAS everywhere, emergency grafts, runtime verified execution, builder tiers, foreign-binary compat view, blast-radius diffs, two-person integrity, ports adapter lane, repo signing UX.
- Added RFCs 0069–0078 and blast-radius diff schema + example.

## 2026-02-23 (archive revision, ecosystem feature harvest)

- Added ZFS send/recv distribution lane notes (treat replication streams as signed artifacts; quarantine/promote flow; encrypted raw send option) (`docs/126-zfs-send-distribution.md`) and linked from host/microVM ZFS docs.
- Added Uptane director-role lessons for separating “bytes authenticity” from “node assignment decisions” (`docs/127-uptane-director-targets.md`).
- Added SmartOS imgadm/IMGAPI lessons for image templates + metadata and mapped to DeriveBSD image descriptors (`docs/128-image-registry-imgadm-lessons.md`).
- Extended juicy lessons index with items 18–20 and updated verification matrix + main index to reference the new lanes.
- Extended curated references with OpenBSD syspatch/signify and OpenBSD 5.5 signed release notes, Uptane, ZFS send/receive, SmartOS image docs, and Firecracker jailer reference.

## 2026-02-23 (archive revision, template + bookmarks pass)

- Added template microVM + disposable instance design notes (Qubes disk model: base/private/volatile) (`docs/129-template-microvms-and-disposables.md`) and linked from control-plane compartmentalization (`docs/115-compartmentalized-control-planes.md`).
- Added OpenZFS bookmarks + redaction bookmarks notes (GC-friendly incremental replication + sanitized sends) (`docs/130-zfs-bookmarks-and-redaction.md`) and linked from ZFS send/recv transport lane (`docs/126-zfs-send-distribution.md`).
- Expanded Capsicum/Casper hardening plan with authoritative man page links and a daemon-by-daemon preopen/cap_enter sketch (`docs/49-capsicum-casper-hardening.md`).
- Tightened runtime verified execution note with explicit FreeBSD MAC framework + mac_bsdextended stepping-stone (`docs/103-runtime-verified-execution.md`).
- Updated verification matrix and juicy lessons index to reference new template/bookmark/redaction lanes (`docs/92-verification-matrix.md`, `docs/110-juicy-os-lessons.md`).
- Extended curated references with OpenZFS bookmark/redact, Qubes template docs, and FreeBSD MAC chapter (`docs/32-curated-references.md`).

## 2026-02-23 (archive revision, time + budgets + routing isolation pass)

- Added trustworthy time input notes (Roughtime + last-known-good time monotonicity) (`docs/142-trustworthy-time-roughtime.md`) and linked from verification matrix.
- Added policy-derived resource budgets for builders/jails/microVM runners (rctl/racct + cpuset) (`docs/143-resource-controls-rctl-racct-cpuset.md`) and linked from hostile-builder stance.
- Added routing isolation via multiple FIBs (setfib) as a complement to pf filtering (`docs/144-routing-isolation-fibs-setfib.md`) and linked from networking docs.
- Updated juicy lessons index (items 34–36), main index, and curated references.

## 2026-02-23 (archive revision, optional lanes: unikernels + ZFS encryption + doas)

- Added optional unikernel lane notes (Solo5 tender model + NetBSD rump-kernel tooling as prior art) and mapped to DeriveBSD artifact targets + runtime contracts (`docs/145-unikernel-lane-rump-solo5.md`).
- Added ZFS native encryption design notes for DeriveBSD generations/state, including key-use evidence objects and raw-send distribution considerations (`docs/146-zfs-native-encryption-for-generations.md`).
- Added minimal privilege escalation notes (doas-style) and mapped to derived escalation rule artifacts (`docs/147-doas-minimal-privilege-escalation.md`).
- Updated juicy OS lessons index with items 37–39 and updated main index + curated references to include the new lanes (`docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `docs/32-curated-references.md`).
- Updated verification matrix and secrets delivery notes to reference ZFS encryption key-use evidence (`docs/92-verification-matrix.md`, `docs/63-secrets-sealing-and-delivery.md`).

## 2026-02-23 (archive revision, credential broker + store hardening)

- Added factotum-style credential broker notes (protocol-agnostic agent; policy-scoped operations; evidence of secret use) (`docs/151-factotum-style-credential-broker.md`).
- Added store view minimization notes (hide non-required store paths from builders; derive `storeview.manifest`; enforce via mount composition) (`docs/152-store-view-minimization.md`).
- Added store immutability invariants notes (read-only datasets/snapshots; edge verification; TOCTOU framing) (`docs/153-store-immutability-and-toc-tou.md`).
- Updated non-negotiable behaviors, hostile builder stance, verification matrix, juicy lessons, curated references, and the main index to wire these in (`docs/97-non-negotiable-behaviors.md`, `docs/91-hostile-builders.md`, `docs/92-verification-matrix.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`).

## 2026-02-23 (feedback integration)

- Resolved **anti-rollback vs rollback** tension via scoped enforcement + explicit manual override (docs/154, ADR-0037).
- Added end-to-end **trust bootstrap** sketch with evidence requirements (docs/155).
- Added **toolchain trust tiers** and Rust bootstrap treatment (docs/156, ADR-0038).
- Documented **storeview performance/caching** mitigations (docs/157).
- Added **ports impurity taxonomy** and containment rules (docs/158).

## 2026-02-23 (Nix UX parity + FreeBSD-first scope tighten)

- Tightened scope to **FreeBSD-first** with no alternate host-OS pathways; removed seL4 docs/RFCs and scrubbed remaining cross-OS references (`docs/22-scope-and-direction.md`, `docs/11-why-bsd.md`, `adrs/ADR-0002-hypervisor-centric-derivebsd.md`).
- Made **DevShells** first-class (nix-shell/nix develop parity): added design doc + schema + example and wired into non-negotiable behaviors (`docs/159-devshells.md`, `spec/devshell.spec.schema.json`, `spec/examples/devshell.spec.json`, `adrs/ADR-0039-devshells-first-class.md`, `docs/97-non-negotiable-behaviors.md`).
- Clarified “extend it hard” posture: allow powerful frontends as **compilers** while keeping core evaluation code-free (`docs/79-derive-spec-frontends.md`, `docs/83-evaluator-minimalism.md`).
- Added overlay-transform notes as a deterministic analogue to Nix overlays (`docs/160-overlay-transforms.md`, `rfcs/RFC-0095-overlay-transforms.md`).
- Added module + options layer notes (NixOS-like composition + option discovery) (`docs/161-module-and-options-layer.md`, `rfcs/RFC-0096-module-and-options-layer.md`).
- Added user environment notes (Home-Manager analogue) (`docs/162-user-environments.md`, `rfcs/RFC-0097-user-environments.md`).
- Updated curated references to include Nix UX inspirations and removed Linux-only compatibility pointers (`docs/32-curated-references.md`).

## 2026-02-23 (ecosystem hardening harvest: CHERI + split crypto + pkg adapter + test receipts)

- Added optional **CHERI capability lane** notes (CheriBSD/CHERI as a BSD-native hardening accelerator) (`docs/163-cheri-capability-lane.md`, `rfcs/RFC-0098-cheri-capability-lane.md`).
- Added **split crypto domains** notes (Qubes split-GPG pattern; crypto operation receipts) (`docs/164-split-crypto-domains.md`, `rfcs/RFC-0099-split-crypto-domains.md`).
- Added optional **FreeBSD pkg repo adapter** notes (bridge Derive artifacts to pkg repos without weakening verification) (`docs/165-freebsd-pkg-repo-adapter.md`, `rfcs/RFC-0100-freebsd-pkg-repo-adapter.md`).
- Added **test receipts** as evidence objects + policy promotion gates (`docs/166-test-receipts-and-promotion-gates.md`, `rfcs/RFC-0101-test-receipts-and-promotion-gates.md`).
- Updated verification matrix and non-negotiable behaviors to reference crypto-op receipts and test receipts (`docs/92-verification-matrix.md`, `docs/97-non-negotiable-behaviors.md`).
- Extended juicy lessons index with items 46–49 and extended curated references accordingly (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Added a small DevShell ergonomics note: direnv-style hook as a wrapper over verified Plan outputs (`docs/159-devshells.md`).

## 2026-02-23 (hermeticity scaling + SBOM/VEX + build farm ops)

- Added sandboxfs-based storeview projection as an *optional* performance optimization for store view minimization (`docs/167-sandboxfs-accelerated-storeviews.md`, `rfcs/RFC-0102-sandboxfs-accelerated-storeviews.md`).
- Tightened SBOM story into evidence-bearing objects and added a companion VEX evidence concept (inventory is not exploitability) (`docs/168-sboms-and-vex-as-evidence.md`, `rfcs/RFC-0103-sbom-and-vex-evidence.md`).
- Added jobsets/build-farm orchestration notes (Hydra lessons mapped to DeriveBSD’s deterministic evaluation + promotion gates) (`docs/169-jobsets-and-build-farms.md`, `rfcs/RFC-0104-jobsets-and-build-farm.md`).
- Added remote cache threat model notes (poisoning/replay) and wired into cache trust posture (`docs/170-remote-cache-threat-model.md`, `rfcs/RFC-0105-remote-cache-threat-model.md`, `docs/46-cache-trust-model.md`).
- Updated storeview docs to point at sandboxfs optimization (`docs/152-store-view-minimization.md`, `docs/157-storeview-performance.md`).
- Updated SBOM format selection doc to reference VEX companion evidence (`docs/75-sbom-formats-spdx-cyclonedx.md`).
- Updated verification matrix, main index, juicy lessons index, and curated references to include the new lanes (`docs/92-verification-matrix.md`, `docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
