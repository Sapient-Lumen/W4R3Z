# 213 — Example packets index

**Track:** Shared

> Generated file. Do not hand-edit. Source: scripts/gen_example_packets_index.py

Shipped example evidence packets are small, runnable packets intended to clarify the evidence API surface without embedding large artifacts.

## Index

| Packet directory | Envelope kind(s) | Payload schema(s) | Attachment rel(s) | Verify |
|---|---|---|---|---|
| `evidence_packet_enr_receipted` | `hfv.results.enr_update` | `schemas/ENRUpdate.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_enr_receipted` |
| `evidence_packet_liveness_beacon_minimal` | `hfv.coverage.liveness_beacon` | `schemas/LivenessBeacon.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_liveness_beacon_minimal` |
| `evidence_packet_minimal` | `hfv.coverage.report`; `hfv.inspection.suppression_report` | `schemas/CoverageReport.json`; `schemas/InspectionSuppressionReport.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_minimal` |
| `evidence_packet_official_channel_directory` | `hfv.public.official_channel_directory` | `schemas/OfficialChannelDirectory.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_official_channel_directory` |
| `evidence_packet_packet_verification_report_minimal` | `hfv.verifier.packet_verification_report` | `schemas/PacketVerificationReport.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_packet_verification_report_minimal` |
| `evidence_packet_public_notice` | `hfv.public.notice` | `schemas/PublicNotice.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_notice` |
| `evidence_packet_public_notice_feed` | `hfv.public.notice_feed` | `schemas/PublicNoticeFeed.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_notice_feed` |
| `evidence_packet_public_surface_parity_snapshot_minimal` | `hfv.public.surface_parity_snapshot` | `schemas/PublicSurfaceParitySnapshot.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_surface_parity_snapshot_minimal` |
| `evidence_packet_publication_compliance_minimal` | `hfv.coverage.publication_report`; `hfv.public.notice`; `hfv.publication.contract`; `hfv.publication.trigger_event` | `schemas/PublicNotice.json`; `schemas/PublicationContract.json`; `schemas/PublicationCoverageReport.json`; `schemas/PublicationTriggerEvent.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_publication_compliance_minimal` |
| `evidence_packet_publication_contract` | `hfv.publication.contract`; `hfv.publication.suppression_report` | `schemas/PublicationContract.json`; `schemas/PublicationSuppressionReport.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_publication_contract` |
| `evidence_packet_time_beacon_minimal` | `hfv.time.beacon` | `schemas/TimeBeacon.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_time_beacon_minimal` |
| `evidence_packet_verifier_report_minimal` | `hfv.verifier.report` | `schemas/VerifierReport.json` | — | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_verifier_report_minimal` |
| `evidence_packet_well_known_discovery` | `hfv.public.well_known_discovery` | `schemas/WellKnownElectionStackDiscovery.json` | `gossip_summary`; `transparency_receipt` | `python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_well_known_discovery` |

Notes:
- Bundle packets contain multiple envelopes; single-envelope packets are minimal representatives for one envelope kind.
- Verification checks digests and pointer integrity; signatures in examples are placeholders unless stated otherwise.
