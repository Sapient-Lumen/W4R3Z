# 179 — Evidence API surface (what an offline verifier must implement)

**Track:** Shared

This doc defines the minimal “API surface” for a verifier or observer tool that wants to
consume evidence from this archive **offline**, under adversarial publication conditions
(selective disclosure, mirror games, split views).

It is deliberately small:
- implement `EvidenceEnvelope` + `EvidencePointer`
- support a compact set of registered `kind` values
- verify digests using JSON canonicalization (JCS)

## 179.1 Packet layout (directory form)

A minimal evidence packet MAY be a directory containing:

- `manifest.json` — an `EvidenceBundleManifest`
- `objects/` — detached payload objects, content-addressed by digest
- `envelopes/` — human-named `EvidenceEnvelope` JSON files that point into `objects/`

See: `artifacts/examples/evidence_packet_minimal/`.

## 179.2 Canonicalization and digests

All envelope hashing/signing uses JSON Canonicalization Scheme (JCS) (RFC 8785).
See: `176-canonicalization-and-signing-rules-for-evidence-envelopes.md`.

A verifier MUST:
- recompute `payload_digest` from the canonicalized payload JSON
- recompute `tbs_digest` from the canonicalized “to‑be‑signed” envelope object
- report missing detached objects as **verification failures** (not “unknown”)

JCS reference: RFC 8785 (`source: rfc8785_txt`).

## 179.3 Supported envelope kinds (profiles, not a monolith)

Human summary: `docs/EVIDENCE_OBJECT_CATALOG.md` (generated).

The authoritative list is `artifacts/registries/envelope-kinds.csv`.

Verifier support profiles are registered in `artifacts/registries/verifier-profiles.csv` (human index: `docs/VERIFIER_PROFILES.md`, generated).
A verifier SHOULD claim profile IDs in `hfv.verifier.report.supported_profiles` (see `docs/193`) so different implementations can be compared without inflating the minimum.

### 179.3.1 Track A base integrity ingest profile (`tes.verifier.profile.track_a_base_integrity_ingest.v1`)

A Track A verifier that wants to answer “did these bytes match the manifest, and were they signed/cosigned under the stated policy?”
SHOULD implement at least:

- `hfv.election.parameters_bundle`
- `hfv.results.enr_update`
- `hfv.inspection.challenge_schedule`
- `hfv.inspection.suppression_report`
- `hfv.inspection.gossip_message`
- `hfv.coverage.report`
- `hfv.incident.after_action_report`

If the verifier publishes its own results, it SHOULD also implement the publishable report kinds (profile: `tes.verifier.profile.publishable_reports.v1`):
- `hfv.verifier.packet_verification_report` (schema: `schemas/PacketVerificationReport.json`)
- `hfv.verifier.report` (schema: `schemas/VerifierReport.json`) for implementation identity + conformance claims

### 179.3.2 Public communications & discovery profile (`tes.verifier.profile.public_comms_discovery.v1`)

If the verifier is used to assess **official communications** (rumor-control/status boards, “where to look” directories, and bounded notice discovery),
it SHOULD also implement:

- `hfv.public.notice`
- `hfv.public.notice_feed` (bounded notice discovery; see `docs/200`)
- `hfv.public.notice_signing_keyset` (authorized PublicNotice signing keys; see `docs/208`)
- `hfv.public.official_channel_directory` (declared official channels; see `docs/203`)
- `hfv.public.well_known_discovery` (domain-first bootstrap; see `docs/204`)
- `hfv.public.surface_parity_snapshot` (split-view proof across channels; see `docs/201`)
- `hfv.coverage.liveness_beacon` (missingness surface; see `docs/210`)

### 179.3.3 Witness governance profile (`tes.verifier.profile.witness_governance.v1`)

If the verifier makes claims about **which witnesses were expected** (quorum, witness policy, or capture-resistance posture),
it SHOULD also implement:

- `hfv.witness.set`
- `hfv.witness.set_change`

### 179.3.4 Optional: closeout omission detection (`tes.verifier.profile.closeout_index.v1`)

If supporting precinct closeout omission detection (see `docs/198`), also implement:
- `hfv.results.closeout_index`

## 179.4 Optional: receipts and transparency services

Evidence envelopes can be paired with receipts and gossip summaries to prevent selective disclosure (docs/180).
These are carried as attachments (detached objects referenced by `EvidencePointer`) and may be REQUIRED per-kind via `artifacts/registries/envelope-attachment-requirements.csv`.

SCITT architecture (work in progress) (`source: draft_scitt_architecture_22_txt`).

## 179.5 Output expectations

A verifier MUST produce an observer report that is itself an evidence object:
- what was present
- what validated
- what failed (missing objects, digest mismatches, unknown kinds)
- what deadlines / suppression events were provable

This is how we prevent the “verification ecosystem” from being quietly corrupted:
failures are made *publishable*.

Reference helper: `tools/observer_verify_packet.py` now enforces the **kind registry** + **required attachments**
in addition to digest integrity; use `--json` to emit a `PacketVerificationReport` payload.

## 179.6 Recommended problem code taxonomy (tight + publishable)

Verifier outputs SHOULD use short, stable codes so different implementations can be compared.

Authoritative list (generated): `docs/VERIFIER_PROBLEM_CODES.md`.

Reference tool: `tools/observer_verify_packet.py --public` emits codes-only outputs suitable for publication.

