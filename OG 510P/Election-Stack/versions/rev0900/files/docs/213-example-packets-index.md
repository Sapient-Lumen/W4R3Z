# 213 — Example packets index

**Track:** Shared

> Generated file. Do not hand-edit. Source: scripts/gen_example_packets_index.py

Shipped example evidence packets are small, runnable packets intended to clarify the evidence API surface without embedding large artifacts.

## Index

| Packet directory | Envelope kind(s) | Payload schema(s) | Attachment rel(s) | Verify |
|---|---|---|---|---|
| `evidence_packet_ed25519_signed_minimal` | `hfv.coverage.report` | `schemas/CoverageReport.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_ed25519_signed_minimal` |
| `evidence_packet_ed25519_threshold2_minimal` | `hfv.coverage.report` | `schemas/CoverageReport.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_ed25519_threshold2_minimal` |
| `evidence_packet_election_parameters_bundle_minimal` | `hfv.election.parameters_bundle` | `schemas/ElectionParameterBundle.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_election_parameters_bundle_minimal` |
| `evidence_packet_enr_receipted` | `hfv.results.enr_update` | `schemas/ENRUpdate.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_enr_receipted` |
| `evidence_packet_governance_endorsement_update_minimal` | `hfv.governance.endorsement_update` | `schemas/EndorsementUpdate.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_governance_endorsement_update_minimal` |
| `evidence_packet_governance_reference_value_update_minimal` | `hfv.governance.reference_value_update` | `schemas/ReferenceValueUpdate.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_governance_reference_value_update_minimal` |
| `evidence_packet_incident_after_action_report_minimal` | `hfv.incident.after_action_report` | `schemas/AfterActionReport.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_incident_after_action_report_minimal` |
| `evidence_packet_incident_key_compromise_event_minimal` | `hfv.incident.key_compromise_event` | `schemas/KeyCompromiseEvent.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_incident_key_compromise_event_minimal` |
| `evidence_packet_inspection_challenge_schedule_minimal` | `hfv.inspection.challenge_schedule` | `schemas/ChallengeSchedule.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_inspection_challenge_schedule_minimal` |
| `evidence_packet_inspection_gossip_message_minimal` | `hfv.inspection.gossip_message` | `schemas/PublicInspectionGossipMessage.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_inspection_gossip_message_minimal` |
| `evidence_packet_liveness_beacon_minimal` | `hfv.coverage.liveness_beacon` | `schemas/LivenessBeacon.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_liveness_beacon_minimal` |
| `evidence_packet_minimal` | `hfv.coverage.report`; `hfv.inspection.suppression_report` | `schemas/CoverageReport.json`; `schemas/InspectionSuppressionReport.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_minimal` |
| `evidence_packet_official_channel_directory` | `hfv.public.official_channel_directory` | `schemas/OfficialChannelDirectory.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_official_channel_directory` |
| `evidence_packet_packet_verification_report_minimal` | `hfv.verifier.packet_verification_report` | `schemas/PacketVerificationReport.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_packet_verification_report_minimal` |
| `evidence_packet_provenance_build_provenance_minimal` | `hfv.provenance.build_provenance` | `schemas/VerifierProvenance.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_provenance_build_provenance_minimal` |
| `evidence_packet_public_notice` | `hfv.public.notice` | `schemas/PublicNotice.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_notice` |
| `evidence_packet_public_notice_feed` | `hfv.public.notice_feed` | `schemas/PublicNoticeFeed.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_notice_feed` |
| `evidence_packet_public_notice_signing_keyset_minimal` | `hfv.public.notice_signing_keyset` | `schemas/PublicNoticeSigningKeyset.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_notice_signing_keyset_minimal` |
| `evidence_packet_public_surface_parity_snapshot_minimal` | `hfv.public.surface_parity_snapshot` | `schemas/PublicSurfaceParitySnapshot.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_surface_parity_snapshot_minimal` |
| `evidence_packet_public_surface_security_snapshot_minimal` | `hfv.public.surface_security_snapshot` | `schemas/OfficialSurfaceSecuritySnapshot.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_surface_security_snapshot_minimal` |
| `evidence_packet_publication_compliance_minimal` | `hfv.coverage.publication_report`; `hfv.public.notice`; `hfv.publication.contract`; `hfv.publication.trigger_event` | `schemas/PublicNotice.json`; `schemas/PublicationContract.json`; `schemas/PublicationCoverageReport.json`; `schemas/PublicationTriggerEvent.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_publication_compliance_minimal` |
| `evidence_packet_publication_contract` | `hfv.publication.contract`; `hfv.publication.suppression_report` | `schemas/PublicationContract.json`; `schemas/PublicationSuppressionReport.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_publication_contract` |
| `evidence_packet_results_closeout_index_minimal` | `hfv.results.closeout_index` | `schemas/PrecinctCloseoutIndex.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_results_closeout_index_minimal` |
| `evidence_packet_results_cross_register_consistency_report_minimal` | `hfv.results.cross_register_consistency_report` | `schemas/CrossRegisterConsistencyReport.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_results_cross_register_consistency_report_minimal` |
| `evidence_packet_results_release_package_minimal` | `hfv.results.release_package` | `schemas/ResultsReleasePackage.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_results_release_package_minimal` |
| `evidence_packet_time_beacon_minimal` | `hfv.time.beacon` | `schemas/TimeBeacon.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_time_beacon_minimal` |
| `evidence_packet_verifier_capacity_roster_minimal` | `hfv.verifier.capacity_roster` | `schemas/VerifierCapacityRoster.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_verifier_capacity_roster_minimal` |
| `evidence_packet_verifier_report_minimal` | `hfv.verifier.report` | `schemas/VerifierReport.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_verifier_report_minimal` |
| `evidence_packet_well_known_discovery` | `hfv.public.well_known_discovery` | `schemas/WellKnownElectionStackDiscovery.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_well_known_discovery` |
| `evidence_packet_witness_liveness_dissent_report_minimal` | `hfv.witness.liveness_dissent_report` | `schemas/WitnessLivenessDissentReport.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_witness_liveness_dissent_report_minimal` |
| `evidence_packet_witness_set_change_minimal` | `hfv.witness.set_change` | `schemas/WitnessSetChange.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_witness_set_change_minimal` |
| `evidence_packet_witness_set_minimal` | `hfv.witness.set` | `schemas/WitnessSet.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_witness_set_minimal` |

Notes:
- Bundle packets contain multiple envelopes; single-envelope packets are minimal representatives for one envelope kind.
- Verification checks digests and pointer integrity; signatures in examples are placeholders unless stated otherwise.
