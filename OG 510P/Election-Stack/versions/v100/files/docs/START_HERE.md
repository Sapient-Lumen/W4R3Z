# Start here (read-order + “what this project is about”)

> "Assume humans compromise systems, build evidence that survives it, and maximize the odds of justified eudaimonia for the innocent, future generations of humans and AI, and all agents who might possibly be able to change the course of history appropriately."
>
> *(This is intentionally “squishy.” Do not sanitize it into false precision. Treat uncertainty as a first-class citizen and pursue justice as optimistically as we can.)*

This archive is the working spec pack for **The Election Stack**: a **research + engineering** program for an election **transparency and evidence stack**.

It is deliberately split into **three tracks** so we can pursue an ambitious North Star without confusing
what is deployable today.

- **Track A — Deployable Core:** evidence infrastructure that can wrap paper/BMD/in-person workflows.
- **Track B — Remote Return / Hard-mode Research:** constrained experiments, with explicit non-claims.
- **Track C — North Star:** “fully electronic voting in its best imaginable form” — attestable devices,
  transparent manufacturing/provenance, and a verification ecosystem hardened against capture.


## Role-based reading paths (fast)

- **Maintainer / steward:** `150` (change protocol) → `adr/INDEX.md` (decision register) → `151`/`161` (sources + citation map) → `162` (release gate) → `docs/PUBLIC_SURFACES.md` (stable external surfaces) → `153` (freeze plan) → `183` (stewardship posture).
- **Verifier implementer:** `173` (evidence packets) → `176` (canonicalization + signing) → `179` (evidence API surface) → `docs/EVIDENCE_OBJECT_CATALOG.md` (kinds + schemas + examples) → `188` (MVP path) → `193` (publishable verifier reports) + `schemas/` + `artifacts/examples/`.
- **Election operator / program lead:** `08` (operations) → `04` (transparency log) → `23` (witness gossip) → `63–72` (results + ENR + publication) → `87`/`186–187` (incident comms + publication compliance) + Track A gate (`track-a/MVR_CHECKLIST.md`).
- **Researcher (remote return / North Star):** `172` (open questions) → Track B bundle (`track-b/BUNDLE.md`) and Track C bundle (`track-c/BUNDLE.md`) + `155–157` (attestation/provenance stack).

If you're maintaining or extending this archive, read:
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)


## Recent additions (v40–v100)
- **Archive entrypoint refresh** (role-based reading paths): this document (`docs/START_HERE.md`).
- **Evidence object catalog** (kind → schema → required attachments → examples): `docs/EVIDENCE_OBJECT_CATALOG.md` (generated).
- **Publishable verifier reason-code registry** (small, stable, comparable): `artifacts/registries/verifier-problem-codes.csv` + drift firewall `scripts/check_verifier_problem_codes_registry.py`.
- **Stewardship compression patterns** (prevent bloat while evolving): `docs/183-archive-stewardship-and-long-horizon-plan.md`.
- **AI-era forged artifacts / synthetic media backlog**: `docs/172-open-research-questions-and-experiment-backlog.md`.
- **ADR decision registry** (single decision index): `adr/INDEX.md`.
- **ADR 0002 (comms as evidence)**: PublicNotice as the canonical comms artifact + official channel IDs (`adr/0002-public-communications-as-evidence-via-publicnotice.md`).
- **ADR drift firewall** (prevents silent decision drift): `scripts/check_adr_index.py`.
- **Incident comms as evidence** (PublicNotice + rumor-control packet): `docs/186-incident-communications-as-evidence.md`.
- **Drill scenario registry + drift firewall** (keep drills aligned with triggers/kinds/comms artifacts): `artifacts/registries/drill-scenarios.csv` + `scripts/check_drill_scenarios.py`.
- **New rumor-control drills** (channel takeover + deepfakes): added scenarios in `artifacts/registries/drill-scenarios.csv` (v69).
- **Ops-reality drill scenarios** (availability, ballot definition, VRDB, ENR, credential recovery): added to the canonical drill registry (v70) and indexed from `docs/90`.
- **Known issues registry format** (patch/mitigation transparency): `artifacts/registries/known-issues.csv` + drift firewall `scripts/check_known_issues_registry.py` (v70).
- **PublicNotice operator starter kit**: schema-valid payload template + digest-card helper for comms surfaces (`artifacts/templates/public-notice-payload.json`, `tools/public_notice_card.py`) (v71).
- **PublicNotice structured update commitment**: optional `next_update_at` field + follow-up status-update template (`supersedes_notice_id`) + digest-card display + validation checks (v80).
- **PublicNotice rumor-control payload template**: schema-valid drafting template for myth-to-fact notices (`artifacts/templates/public-notice-rumor-control-payload.json`) (v79).
- **Tools status index** (operator-ready vs prototype vs skeleton): `tools/README.md` (v79).
- **Public surfaces index** (registries + schemas external parties depend on): `docs/PUBLIC_SURFACES.md` (generated; includes per-surface digests) (v97).
- **Schema meta-validation + example validation** (drift firewall; format checking): `scripts/validate_schemas.py` (v72).
- **Official comms channels registry** (canonical IDs for PublicNotice.channels + parity monitoring) + drift firewall: `artifacts/registries/official-channels.csv`, `scripts/check_official_channels_registry.py` (v73).
- **Official comms channel hardening checklist** (secure channels + publish digest parity): `artifacts/checklists/official-communications-channels-hardening-checklist.md` (v76).
- **CAA + Certificate Transparency hardening notes** (constrain issuance + monitor mis-issuance): `docs/37` + `artifacts/checklists/official-communications-channels-hardening-checklist.md` (v77).
- **DNSSEC baseline hardening note** (optional domain integrity control for official comms surfaces): `docs/37` (v79).
- **Envelope digest vectors can reference existing payload files** (avoid duplicated bytes via `payload_path`) + new PublicNotice template vector: `artifacts/test-vectors/envelope_vectors.json` + `scripts/check_envelope_vectors.py` (v77).
- **PublicNotice correction linkage cleanup**: prefer `correction_of_notice_id` (legacy alias `correction_of` accepted).
- **Evidence envelopes + packets** (anti‑drift packaging): `docs/173-canonical-evidence-envelopes-and-packets.md`
- **Deterministic canonicalization + signing rules** (JCS): `docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`
- **Envelope digest interop vectors** (drift tripwire): `docs/190-envelope-interop-vectors-and-drift-tripwires.md`
- **Time attestation + timestamping as evidence**: `docs/192-time-attestation-and-timestamping-as-evidence.md`
- **Observer kit walkthrough** (offline verification): `docs/177-observer-kit-offline-verification-walkthrough.md`
- **Envelope kind registry** (small, stable API surface): `docs/178-envelope-kind-registry.md`
- **Doc envelope-kind reference drift firewall** (prevents stale/typoed kinds in docs): `scripts/check_doc_envelope_kind_references.py` (v88).
- **Evidence API surface** (what verifiers must implement): `docs/179-evidence-api-surface.md`
- **Packet-scoped verifier reports** (publishable bundle integrity results): `schemas/PacketVerificationReport.json` + kind `hfv.verifier.packet_verification_report` (v82).
- **Verifier implementation report envelope kind** + ship template: kind `hfv.verifier.report` + `artifacts/templates/verifier-report-payload.json` (v88).
- **VerifierReport minimal example packet** (publish a verifier identity report as evidence): `artifacts/examples/evidence_packet_verifier_report_minimal/` (v90).
- **Verifier identity linkage for packet reports**: `PacketVerificationReport.verifier_report_tbs_digest` + `tools/observer_verify_packet.py --verifier-report-envelope/--verifier-report-tbs-digest` (v89).
- **VerifierReport digest card**: stdlib-only `tools/verifier_report_card.py` prints a copy/pasteable verifier identity summary and recomputed digests (v91).
- **PacketVerificationReport digest card**: stdlib-only `tools/packet_verification_report_card.py` prints a bounded, copy/pasteable packet report summary and recomputed digests (v92).
- **PacketVerificationReport comparability pins**: optional `verifier_problem_codes_sha256` + `envelope_kinds_sha256` fields let published reports cite the exact registry bytes used (v98).
- **VerifierReport comparability pins**: implementation-scoped verifier identity reports can now include the same optional registry sha256 pins for byte-level comparability (v99).
- **Public-surface pin helper + drift firewall**: `tools/public_surface_pins.py` prints canonical sha256 pins for stable registry bytes; `scripts/check_example_report_pins.py` enforces that verifier-report example pins + tool versions match the current archive (v100).
- **One-command evidence card renderer**: `tools/evidence_object_card.py` auto-detects kind and dispatches to the right card tool (or prints a small generic card) (v93).
- **Shared packet-reading helpers**: `tools/packet_common.py` centralizes detached-payload lookup + payload_digest recomputation to reduce operator-tool drift (v93).
- **Path traversal hardening for operator tooling**: `tools/packet_common.py` now refuses unsafe `payload_pointer.uri` values (enforces `docs/176` safe-path rule; guarded by a release-gate smoke test) (v94).
- **Encoded-traversal hardening**: safe-path validation now rejects percent-encoded traversal + control/whitespace tricks (shared by tools + example-path scanner; guarded by an expanded smoke test) (v95).
- **Symlink-escape hardening**: detached payload/attachment reads are anchored to the packet root; release-gate forbids symlinks (v96).
- **Drift firewall for linkage emission**: `scripts/check_packet_verification_report_linkage.py` (v90).
- **Public-safe verifier output hardening**: public mode collapses unknown problem codes to `unknown_problem_code` (v84).
- **Verifier problem-code registry**: stable publishable reason codes moved to `artifacts/registries/verifier-problem-codes.csv` (v85).
- **One-command publishable report packet emission**: `tools/observer_verify_packet.py --emit-evidence-object` (v85).
- **Packet layout doc sync**: `docs/173` layout now matches the reference tools (`envelopes/` directory) (v84).
- **External source lockfile playbook** (cite, don’t bloat): `docs/191-external-source-lockfile-playbook.md`
- **Verifier MVP path** (packet → policy → report): `docs/188-verifier-minimum-viable-path.md`
- **Receipts + gossip attachments** (anti-selective disclosure): `docs/180-receipts-and-gossip-attachments.md`

- **Publication contract + deadline breach proofs**: `docs/181-publication-contract-and-deadline-breach-proofs.md`
- **Receipt profiles + semantics tiers**: `docs/182-receipt-profiles-and-mappings.md` + `docs/185-receipt-semantics-tiers.md`
- **Publication trigger vocabulary + comms-as-evidence**: `docs/184-publication-trigger-vocabulary.md` + `docs/186-incident-communications-as-evidence.md`
- **Publication compliance coverage** (coverage proofs for notices/triggers): `docs/187-publication-compliance-and-coverage.md`

Earlier high‑leverage additions:
- Public randomness kernel for seeded sampling: `docs/168-public-randomness-beacons-and-seeded-sampling.md`
- Endorsement/reference-value transparency (North Star anti‑capture): `docs/169-endorsement-and-reference-value-transparency.md`
- Supply‑chain provenance profile (SLSA + in‑toto): `docs/170-slsa-and-intoto-provenance-profile.md`

If you ever worry “are we backing away from the full stack?”, the answer is **no**:
the archive is organizing the full stack into *tracks* so claims remain honest and auditable.

## Archive scope without archive bloat

This archive is **full‑stack in design scope**, but **size‑disciplined**:

- Do **not** embed third‑party PDFs or external works wholesale.
- Prefer citations + short excerpts (only when necessary) + pinned sources (`evidence/lock/`).
- Never include secrets (especially private keys): see `docs/189-sensitive-material-and-secrets.md`.
- Prefer original synthesis as **schemas, checklists, drills, and proof obligations**.

The primary reader is an **LLM maintainer**. Start with the claims contract:
- `166-scope-and-claims-contract.md`
- `167-non-claims-and-boundaries.md`

## Entry points (by track)
- **Track A:** `track-a/README.md`
  - Quick: `track-a/BUNDLE.md`
  - Release gate: `track-a/MVR_CHECKLIST.md`
- **Track B:** `track-b/README.md`
  - Quick: `track-b/BUNDLE.md`
- **Track C:** `track-c/README.md`
  - Quick: `track-c/BUNDLE.md`

## Global read order (15–30 minutes)
1. `154-project-scope-and-track-map.md`
2. `166-scope-and-claims-contract.md` + `167-non-claims-and-boundaries.md`
3. `00-design-goals.md`
4. `01-threat-model.md`
5. `04-transparency-log.md` + `23-witness-gossip-and-cross-checkpointing.md`
6. `159-proof-obligations-ledger.md` + `164-proof-obligations-registry.md`
7. `160-generated-canonical-spec-contract.md`
8. Pick a track readme and follow the suggested deep dives.

## If you are maintaining this archive
Start with `150-maintainer-bootstrap-and-change-protocol.md`.

## Canonical evidence packaging (new)
- Evidence envelopes + packet layout: `docs/173-canonical-evidence-envelopes-and-packets.md`
- Coverage accounting deliverable: `docs/174-coverage-accounting-and-representativeness.md`
- Publication compliance coverage: `docs/187-publication-compliance-and-coverage.md`

## Offline verification starting point
If you're an independent observer, start with:
- `docs/188-verifier-minimum-viable-path.md`
- `docs/177-observer-kit-offline-verification-walkthrough.md`
- example packets:
  - `artifacts/examples/evidence_packet_minimal/` (suppression report + required attachments)
  - `artifacts/examples/evidence_packet_enr_receipted/` (ENR update + required attachments)
  - `artifacts/examples/evidence_packet_publication_compliance_minimal/` (TriggerEvents + PublicNotice + publication coverage)
  - `artifacts/examples/evidence_packet_packet_verification_report_minimal/` (publishable packet verification report as evidence)
- reference checker: `tools/observer_verify_packet.py`
- release-gate: `scripts/check_example_packets.py` (keeps examples from silently rotting)
