# Public surfaces index

**Track:** Shared

This document is a compact index of the archive’s **public surfaces**: small identifiers and schemas that external implementers may depend on.
If you change any of these in a way that could break consumers, prefer an ADR + a migration story.

| Surface | Canonical source | Digest | Human view | Notes |
|---|---|---|---|---|
| Envelope kinds (kind → schema) | `artifacts/registries/envelope-kinds.csv` | `sha256:87561c8edfeb…` | docs/EVIDENCE_OBJECT_CATALOG.md (generated), docs/178-envelope-kind-registry.md | Treat as a stable API surface; add via ADR when semantics change. (33 entries.) |
| Required attachments per kind | `artifacts/registries/envelope-attachment-requirements.csv` | `sha256:e16195442e03…` | docs/EVIDENCE_OBJECT_CATALOG.md (generated), docs/180-receipts-and-gossip-attachments.md | Anti-selective-disclosure firewall; changes can be breaking. (44 entries.) |
| Receipt profiles | `artifacts/registries/receipt-profiles.csv` | `sha256:315aeba9765f…` | docs/182-receipt-profiles-and-mappings.md, docs/185-receipt-semantics-tiers.md | Profile IDs are public strings; keep small and stable. (7 entries.) |
| Publishable verifier problem codes | `artifacts/registries/verifier-problem-codes.csv` | `sha256:c84eeeafd560…` | docs/VERIFIER_PROBLEM_CODES.md (generated), docs/193-publishable-verifier-reports.md | Designed for cross-verifier comparability; registry is strict + sorted. (170 entries.) |
| Publishable public-surface anomaly codes | `artifacts/registries/surface-anomaly-codes.csv` | `sha256:bde608bba5da…` | docs/SURFACE_ANOMALY_CODES.md (generated), docs/201-public-surface-parity-snapshots.md, docs/210-liveness-beacons-and-missingness-surface.md | Designed for cross-monitor comparability when using notes fields in bounded monitoring payloads; registry is strict + sorted. (18 entries.) |
| Verifier profiles (capability claims) | `artifacts/registries/verifier-profiles.csv` | `sha256:8beec259f650…` | docs/VERIFIER_PROFILES.md (generated), docs/179-evidence-api-surface.md | Small profile IDs for cross-verifier capability comparability; registry is strict + sorted. (6 entries.) |
| Tool maturity + evidence-safety registry | `artifacts/registries/tool-maturity.csv` | `sha256:d23ec903956a…` | docs/212-tooling-maturity-and-evidence-safety.md, tools/README.md | Non-normative intent surface to prevent confusing research/skeleton tools with evidence outputs; keep sorted. (92 entries.) |
| Official communication channel IDs | `artifacts/registries/official-channels.csv` | `sha256:11c4652f40bc…` | docs/186-incident-communications-as-evidence.md, artifacts/checklists/official-communications-channels-hardening-checklist.md | Channel IDs appear in PublicNotice payloads; changes require migrations. (9 entries.) |
| Publication trigger vocabulary | `artifacts/registries/publication-triggers.csv` | `sha256:89e8d592492c…` | docs/184-publication-trigger-vocabulary.md | Used for incident comms + compliance coverage; keep IDs stable. (8 entries.) |
| EvidenceEnvelope schema | `schemas/EvidenceEnvelope.json` | `sha256:984b5c2d9323…` | docs/173-canonical-evidence-envelopes-and-packets.md, docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md | Envelope header semantics; versioned by envelope_version. |
| PacketVerificationReport schema | `schemas/PacketVerificationReport.json` | `sha256:59f692e9e2d8…` | docs/193-publishable-verifier-reports.md | Packet-scoped publishable verifier output. |
| VerifierReport schema | `schemas/VerifierReport.json` | `sha256:6d255cd77de9…` | docs/193-publishable-verifier-reports.md | Implementation-scoped verifier identity + conformance claims. |
| EvidenceBundleManifest schema | `schemas/EvidenceBundleManifest.json` | `sha256:c43cfac111db…` | docs/173-canonical-evidence-envelopes-and-packets.md, docs/179-evidence-api-surface.md | Bundle manifest contract; used by offline verifiers. |
| PublicNotice schema | `schemas/PublicNotice.json` | `sha256:be40ce5e2726…` | docs/186-incident-communications-as-evidence.md | Canonical official communication payload. |
| PublicNoticeFeed schema | `schemas/PublicNoticeFeed.json` | `sha256:e036ed462a0e…` | docs/200-publicnotice-feeds-and-mirror-index.md | Bounded notice discovery surface (rollback-detectable). |
| PublicNoticeSigningKeyset schema | `schemas/PublicNoticeSigningKeyset.json` | `sha256:bae6013e712a…` | docs/208-publicnotice-signing-keys-and-channel-identity.md | Allow-list of keys authorized to sign PublicNotices for a scope. |
| OfficialChannelDirectory schema | `schemas/OfficialChannelDirectory.json` | `sha256:4c46af099d78…` | docs/203-official-channel-directory-as-evidence.md | Declared official channel directory (discovery anchor). |
| WellKnownElectionStackDiscovery schema | `schemas/WellKnownElectionStackDiscovery.json` | `sha256:b3c5cbe902d7…` | docs/204-well-known-election-stack-discovery.md | Domain-first bootstrap pointer object for comms discovery. |
| PublicSurfaceParitySnapshot schema | `schemas/PublicSurfaceParitySnapshot.json` | `sha256:3e31c89f54fe…` | docs/201-public-surface-parity-snapshots.md | Portable split-view/parity evidence across official channels. |
| OfficialSurfaceSecuritySnapshot schema | `schemas/OfficialSurfaceSecuritySnapshot.json` | `sha256:4f81c13a0545…` | docs/199-official-surface-security-snapshots.md | Auditable snapshot of official-surface hardening posture. |
| LivenessBeacon schema | `schemas/LivenessBeacon.json` | `sha256:b2ee913218c2…` | docs/210-liveness-beacons-and-missingness-surface.md | Independent watcher heartbeat for reachability + observed pointer digests. |
| External source lockfile IDs | `evidence/lock/external-sources.toml` | `sha256:1a79ff31c63e…` | docs/191-external-source-lockfile-playbook.md | Cite, don’t bloat; pinned sources are treated as normative references. |

## Full digests

Full sha256 digests for canonical sources listed above (computed from file bytes at generation time; also present in `MANIFEST.sha256`).

- `artifacts/registries/envelope-kinds.csv` — `sha256:87561c8edfeb41af7796f73f3c6c8c1244d80c5034dcc8677840b30272365d77`
- `artifacts/registries/envelope-attachment-requirements.csv` — `sha256:e16195442e0308a8af57450fd0f2db2b17e0d652ec961e38d0e1d3d15fea7108`
- `artifacts/registries/receipt-profiles.csv` — `sha256:315aeba9765fc35492afaea3068569cb8a62d4482d3e000d57748b17cc7536e4`
- `artifacts/registries/verifier-problem-codes.csv` — `sha256:c84eeeafd560b38474fc0fc77817f90cc57be4a951d7073b450bfe2e32c9b1ac`
- `artifacts/registries/surface-anomaly-codes.csv` — `sha256:bde608bba5dae362a2c9669f6b0a1c0f3902b4e6bbe471846188a1f8c71a7751`
- `artifacts/registries/verifier-profiles.csv` — `sha256:8beec259f650c600db1363a16446c61bf75f4d9fef7b042b48b7844f37087b6c`
- `artifacts/registries/tool-maturity.csv` — `sha256:d23ec903956a29cae75a5ae0fd89811450156f244e96d951810e5227f23282ba`
- `artifacts/registries/official-channels.csv` — `sha256:11c4652f40bc0ffbe1d865a59e57f140b41cd82903ea9187d86b46c240c5da61`
- `artifacts/registries/publication-triggers.csv` — `sha256:89e8d592492c9512477d5916323907a4cdd6c76781623aed7929fa7e205b14e7`
- `schemas/EvidenceEnvelope.json` — `sha256:984b5c2d932371f97bd65a8ca75dbfcf726c9bbd0ebe4d6f8b8989be0feffe0a`
- `schemas/PacketVerificationReport.json` — `sha256:59f692e9e2d8b74d3bcfe27beb6e1d84b1b0c0b1743bad123858a1ead8d9dfad`
- `schemas/VerifierReport.json` — `sha256:6d255cd77de9dab163f5362ffe8bbfae0f205b9c58ccf70f8ad4f8183de6b046`
- `schemas/EvidenceBundleManifest.json` — `sha256:c43cfac111db66bc72e475952b7aaea902304083ed3ec27bb7f630ec485a75d4`
- `schemas/PublicNotice.json` — `sha256:be40ce5e2726ccd1124046b87f4ed054f9d4914af34a26e6f58f2ee7937f2b21`
- `schemas/PublicNoticeFeed.json` — `sha256:e036ed462a0e7cd3ec44d7f270a94cf58b6154241650a97333085169c5eabd87`
- `schemas/PublicNoticeSigningKeyset.json` — `sha256:bae6013e712ab7fab609f21578f431a70a7c27b2a50854c197f6adcce952af2f`
- `schemas/OfficialChannelDirectory.json` — `sha256:4c46af099d783c6c91e069d47f18769b32197616da178379d48882017b8b17bc`
- `schemas/WellKnownElectionStackDiscovery.json` — `sha256:b3c5cbe902d7306485a36031eb1d83517698e738045ca0f78987cc7b56434a1c`
- `schemas/PublicSurfaceParitySnapshot.json` — `sha256:3e31c89f54fe328a5f32017abf032781ebebe1d36dea19181af9362e78761bc9`
- `schemas/OfficialSurfaceSecuritySnapshot.json` — `sha256:4f81c13a0545317688f2729e08c0a24df909cc7a856feb24cea852f9e5193101`
- `schemas/LivenessBeacon.json` — `sha256:b2ee913218c25251f725b5bafd4bd5b099dd87512dc53c1bbb99dba00f9612a8`
- `evidence/lock/external-sources.toml` — `sha256:1a79ff31c63e0e889d05f6a8998f2196c60bd1c201bcc7bec0401365fa52fb05`
