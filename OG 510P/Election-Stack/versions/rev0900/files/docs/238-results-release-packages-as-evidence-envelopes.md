# 238 — Results release packages as evidence envelopes (signature layering)

**Track:** A (Deployable core)

Problem: results objects already have strong hashing rules (`235`) and a strict ordering oracle (PBB + witness checkpoints; `236`).
But deployments can still drift into *signature layering ambiguity*:
- a `ResultsReleasePackage` (RRP) is “signed” in two different ways (inner signature vs envelope signature),
- different mirrors disagree on which bytes are the canonical signed artifact, or
- a PBB `RESULTS` leaf commits to a digest that does not match the published signed object.

This doc makes the RRP publication shape *single‑path* and verifiable.

See also: `173`–`176` (EvidenceEnvelope), `234`–`236` (corrections + hashing + anchoring).


## 238.1 Normative profile

### A) RRPs MUST be published as EvidenceEnvelope payloads
A Track A results interval publication MUST be an `EvidenceEnvelope` with:
- `kind: hfv.results.release_package`
- `payload_schema: schemas/ResultsReleasePackage.json`
- `payload_digest` computed over RFC8785‑JCS canonical JSON of the RRP payload (`source: rfc8785_txt`).
- the envelope MUST include the required publication attachments (receipt + gossip summary) per `artifacts/registries/envelope-attachment-requirements.csv` (anti selective disclosure; `185`, `220`).

This makes the envelope the *one* signature boundary.

### B) Inner signatures in ResultsReleasePackage are deprecated
`ResultsReleasePackage.package_signature` is tolerated for legacy pipelines, but:
- when an RRP is carried as an `EvidenceEnvelope` payload, publishers SHOULD omit `package_signature`, and
- verifiers MUST NOT treat an inner signature as sufficient without a valid envelope signature.

Rationale: envelope signatures are already governed by the archive’s canonical signing rules (`176`) and key registry surfaces.

### C) PBB RESULTS leaves MUST commit to the envelope payload digest
When anchoring a release interval into the PBB (`236`):
- `LogEntry.entry_type = RESULTS`
- `payload_hash_b64` MUST be base64(raw SHA‑256 bytes of RFC8785‑JCS(RRP_payload))

Interoperability rule: the digest committed by the PBB leaf MUST match the envelope’s `payload_digest` (format translation only).



Example packet (minimal): `artifacts/examples/evidence_packet_results_release_package_minimal` (includes required attachments).

## 238.2 Optional adapter: DSSE/in-toto attestations (informative)
Some ecosystems publish provenance/attestations as **in‑toto Statements** wrapped in a **DSSE envelope**.
This archive does not require that format, but it can be carried without schema churn:
- treat the DSSE JSON as a content‑addressed attachment,
- reference it from `hfv.provenance.build_provenance` (`97`) or other evidence payloads,
- keep the *archive’s* signature boundary at `EvidenceEnvelope`.

Reference formats:
- in‑toto Statement v1 (`source: intoto_statement_v1_md`)
- DSSE envelope layer spec (`xref: intoto_envelope_v1_md`)
