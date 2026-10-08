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

JCS reference: RFC 8785.  (https://www.rfc-editor.org/rfc/rfc8785)

## 179.3 Supported envelope kinds (core)

The authoritative list is `artifacts/registries/envelope-kinds.csv`.

A minimal Track A verifier SHOULD implement at least:
- `hfv.election.parameters_bundle`
- `hfv.results.enr_update`
- `hfv.inspection.challenge_schedule`
- `hfv.inspection.suppression_report`
- `hfv.inspection.gossip_message`
- `hfv.coverage.report`
- `hfv.incident.after_action_report`
- `hfv.public.notice` (see `docs/186`)

## 179.4 Optional: receipts and transparency services

Evidence envelopes can be paired with receipts and gossip summaries to prevent selective disclosure (docs/180).
These are carried as attachments (detached objects referenced by `EvidencePointer`) and may be REQUIRED per-kind via `artifacts/registries/envelope-attachment-requirements.csv`.

SCITT architecture draft: https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/

## 179.5 Output expectations

A verifier MUST produce an observer report that is itself an evidence object:
- what was present
- what validated
- what failed (missing objects, digest mismatches, unknown kinds)
- what deadlines / suppression events were provable

This is how we prevent the “verification ecosystem” from being quietly corrupted:
failures are made *publishable*.
