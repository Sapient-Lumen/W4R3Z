# Public surfaces index

**Track:** Shared

This document is a compact index of the archive’s **public surfaces**: small identifiers and schemas that external implementers may depend on.
If you change any of these in a way that could break consumers, prefer an ADR + a migration story.

| Surface | Canonical source | Digest | Human view | Notes |
|---|---|---|---|---|
| Envelope kinds (kind → schema) | `artifacts/registries/envelope-kinds.csv` | `sha256:87561c8edfeb…` | docs/EVIDENCE_OBJECT_CATALOG.md (generated), docs/178-envelope-kind-registry.md | Treat as a stable API surface; add via ADR when semantics change. (33 entries.) |
| Required attachments per kind | `artifacts/registries/envelope-attachment-requirements.csv` | `sha256:e16195442e03…` | docs/EVIDENCE_OBJECT_CATALOG.md (generated), docs/180-receipts-and-gossip-attachments.md | Anti-selective-disclosure firewall; changes can be breaking. (44 entries.) |
| Receipt profiles | `artifacts/registries/receipt-profiles.csv` | `sha256:315aeba9765f…` | docs/182-receipt-profiles-and-mappings.md, docs/185-receipt-semantics-tiers.md | Profile IDs are public strings; keep small and stable. (7 entries.) |
| Publishable verifier problem codes | `artifacts/registries/verifier-problem-codes.csv` | `sha256:c7cfb3300b89…` | docs/VERIFIER_PROBLEM_CODES.md (generated), docs/193-publishable-verifier-reports.md | Designed for cross-verifier comparability; registry is strict + sorted. (50 entries.) |
| Publishable public-surface anomaly codes | `artifacts/registries/surface-anomaly-codes.csv` | `sha256:bde608bba5da…` | docs/SURFACE_ANOMALY_CODES.md (generated), docs/201-public-surface-parity-snapshots.md, docs/210-liveness-beacons-and-missingness-surface.md | Designed for cross-monitor comparability when using notes fields in bounded monitoring payloads; registry is strict + sorted. (18 entries.) |
| Verifier profiles (capability claims) | `artifacts/registries/verifier-profiles.csv` | `sha256:8beec259f650…` | docs/VERIFIER_PROFILES.md (generated), docs/179-evidence-api-surface.md | Small profile IDs for cross-verifier capability comparability; registry is strict + sorted. (6 entries.) |
| Tool maturity + evidence-safety registry | `artifacts/registries/tool-maturity.csv` | `sha256:70e69414cc32…` | docs/212-tooling-maturity-and-evidence-safety.md, tools/README.md | Non-normative intent surface to prevent confusing research/skeleton tools with evidence outputs; keep sorted. (60 entries.) |
| Official communication channel IDs | `artifacts/registries/official-channels.csv` | `sha256:11c4652f40bc…` | docs/186-incident-communications-as-evidence.md, artifacts/checklists/official-communications-channels-hardening-checklist.md | Channel IDs appear in PublicNotice payloads; changes require migrations. (9 entries.) |
| Publication trigger vocabulary | `artifacts/registries/publication-triggers.csv` | `sha256:89e8d592492c…` | docs/184-publication-trigger-vocabulary.md | Used for incident comms + compliance coverage; keep IDs stable. (8 entries.) |
| EvidenceEnvelope schema | `schemas/EvidenceEnvelope.json` | `sha256:0fd31edb64d3…` | docs/173-canonical-evidence-envelopes-and-packets.md, docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md | Envelope header semantics; versioned by envelope_version. |
| PacketVerificationReport schema | `schemas/PacketVerificationReport.json` | `sha256:2520594e4d28…` | docs/193-publishable-verifier-reports.md | Packet-scoped publishable verifier output. |
| VerifierReport schema | `schemas/VerifierReport.json` | `sha256:bc21c3481c7d…` | docs/193-publishable-verifier-reports.md | Implementation-scoped verifier identity + conformance claims. |
| EvidenceBundleManifest schema | `schemas/EvidenceBundleManifest.json` | `sha256:40eacd3764db…` | docs/173-canonical-evidence-envelopes-and-packets.md, docs/179-evidence-api-surface.md | Bundle manifest contract; used by offline verifiers. |
| PublicNotice schema | `schemas/PublicNotice.json` | `sha256:50d3493ab328…` | docs/186-incident-communications-as-evidence.md | Canonical official communication payload. |
| PublicNoticeFeed schema | `schemas/PublicNoticeFeed.json` | `sha256:87e9e06e258c…` | docs/200-publicnotice-feeds-and-mirror-index.md | Bounded notice discovery surface (rollback-detectable). |
| PublicNoticeSigningKeyset schema | `schemas/PublicNoticeSigningKeyset.json` | `sha256:46210a0b1b10…` | docs/208-publicnotice-signing-keys-and-channel-identity.md | Allow-list of keys authorized to sign PublicNotices for a scope. |
| OfficialChannelDirectory schema | `schemas/OfficialChannelDirectory.json` | `sha256:99bb9a6f4970…` | docs/203-official-channel-directory-as-evidence.md | Declared official channel directory (discovery anchor). |
| WellKnownElectionStackDiscovery schema | `schemas/WellKnownElectionStackDiscovery.json` | `sha256:ad293e9e824d…` | docs/204-well-known-election-stack-discovery.md | Domain-first bootstrap pointer object for comms discovery. |
| PublicSurfaceParitySnapshot schema | `schemas/PublicSurfaceParitySnapshot.json` | `sha256:4e1d9c56ec69…` | docs/201-public-surface-parity-snapshots.md | Portable split-view/parity evidence across official channels. |
| OfficialSurfaceSecuritySnapshot schema | `schemas/OfficialSurfaceSecuritySnapshot.json` | `sha256:4a2fb2a096e3…` | docs/199-official-surface-security-snapshots.md | Auditable snapshot of official-surface hardening posture. |
| LivenessBeacon schema | `schemas/LivenessBeacon.json` | `sha256:1c800e2d6ae4…` | docs/210-liveness-beacons-and-missingness-surface.md | Independent watcher heartbeat for reachability + observed pointer digests. |
| External source lockfile IDs | `evidence/lock/external-sources.toml` | `sha256:d1706589b74f…` | docs/191-external-source-lockfile-playbook.md | Cite, don’t bloat; pinned sources are treated as normative references. |

## Full digests

Full sha256 digests for canonical sources listed above (computed from file bytes at generation time; also present in `MANIFEST.sha256`).

- `artifacts/registries/envelope-kinds.csv` — `sha256:87561c8edfeb41af7796f73f3c6c8c1244d80c5034dcc8677840b30272365d77`
- `artifacts/registries/envelope-attachment-requirements.csv` — `sha256:e16195442e0308a8af57450fd0f2db2b17e0d652ec961e38d0e1d3d15fea7108`
- `artifacts/registries/receipt-profiles.csv` — `sha256:315aeba9765fc35492afaea3068569cb8a62d4482d3e000d57748b17cc7536e4`
- `artifacts/registries/verifier-problem-codes.csv` — `sha256:c7cfb3300b89ab1ee2276aa0db779ae13865b7be78c4a60370db250799928473`
- `artifacts/registries/surface-anomaly-codes.csv` — `sha256:bde608bba5dae362a2c9669f6b0a1c0f3902b4e6bbe471846188a1f8c71a7751`
- `artifacts/registries/verifier-profiles.csv` — `sha256:8beec259f650c600db1363a16446c61bf75f4d9fef7b042b48b7844f37087b6c`
- `artifacts/registries/tool-maturity.csv` — `sha256:70e69414cc32b2dd1fc3320871654cd519dbd50f058592f4b8ac1c8db430ebd7`
- `artifacts/registries/official-channels.csv` — `sha256:11c4652f40bc0ffbe1d865a59e57f140b41cd82903ea9187d86b46c240c5da61`
- `artifacts/registries/publication-triggers.csv` — `sha256:89e8d592492c9512477d5916323907a4cdd6c76781623aed7929fa7e205b14e7`
- `schemas/EvidenceEnvelope.json` — `sha256:0fd31edb64d30f8ca5691c820cabcaf4fe0e105b69559daa41399856a44d0f4c`
- `schemas/PacketVerificationReport.json` — `sha256:2520594e4d28675d99cc8ac01e7d7b46fa341c5cf7ba1fb88a59f3d310449ed2`
- `schemas/VerifierReport.json` — `sha256:bc21c3481c7d9c2193beb38d560860d70e9039065ad65593a7bdd9e752117ce1`
- `schemas/EvidenceBundleManifest.json` — `sha256:40eacd3764db1834cfbd949ace6d7af57c2a033736c6f94b8101a0d9a3b2e37f`
- `schemas/PublicNotice.json` — `sha256:50d3493ab32869dc9d98605947375be563839251bc7530eb3294940d02651c20`
- `schemas/PublicNoticeFeed.json` — `sha256:87e9e06e258c43eac860e44fed64cfc845dbfc13095fff7e09fa4dee36ed2522`
- `schemas/PublicNoticeSigningKeyset.json` — `sha256:46210a0b1b10745773a743456d703dedcaf38f481a070f5d75b4f63ca465bf3d`
- `schemas/OfficialChannelDirectory.json` — `sha256:99bb9a6f497082a39079c76729dc4971df81145e08aae06613d3fb5242537a1d`
- `schemas/WellKnownElectionStackDiscovery.json` — `sha256:ad293e9e824d8481ce0fdb18d406d9cfc224922776ab7ef0833c1fdcdeea0107`
- `schemas/PublicSurfaceParitySnapshot.json` — `sha256:4e1d9c56ec698e951f4a34ef0f01138ac299a9f1f77ad8b241db76e9fbb8b7d9`
- `schemas/OfficialSurfaceSecuritySnapshot.json` — `sha256:4a2fb2a096e3d3e2eb5afc691ee60eea131885e1cc356036e29f4dd2a7ab0c3c`
- `schemas/LivenessBeacon.json` — `sha256:1c800e2d6ae4a51ed1bf770d329eb1f36422aff9d4f19c1e5cfef405249213bc`
- `evidence/lock/external-sources.toml` — `sha256:d1706589b74fabda5f5c976de1d653e3c1b187a099fedc9a2c7780c82aec7690`
