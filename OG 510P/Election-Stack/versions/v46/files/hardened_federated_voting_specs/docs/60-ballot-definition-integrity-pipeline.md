# 60 — Ballot definition integrity pipeline (BDI)

**Track:** A (Deployable core)


Ballot definitions are **executable election law**. A single-bit change can:
- remove a contest or candidate for a subset of voters,
- swap candidate order/labels,
- mis-map selections to tabulation identifiers,
- mis-assign a voter to the wrong ballot style.

Because this pack treats the network as hostile, we treat ballot definition production/distribution as a *Tier‑0 security boundary*.

## Goals
- Ensure every voter is presented the **correct ballot style**.
- Ensure ballot definitions are **tamper-evident**, **publicly verifiable**, and **reproducible**.
- Ensure *targeted* manipulation (serving different ballot definitions to different voters) becomes **detectable and provable**.
- Ensure ballot definitions integrate cleanly with audits and reporting.

## Recommended data model
Use the NIST **Ballot Definition Common Data Format** (BD CDF) as the authoritative machine-readable representation for ballot style and contest structure.
- NIST SP 1500‑20 (BD CDF) describes JSON/XML schemas and expected use cases.

Also use NIST implementation guidance for CDF integration across BD/CVR/VRI/ERR.

## Canonicalization and hashing
To make BD files safely signable and hashable:
- Canonicalize JSON using **RFC 8785 (JCS)**.
- Hash the canonical bytes (e.g., SHA‑256) to get `bd_hash`.
- Treat `bd_hash` as the unique identifier for the ballot definition.

**MUST:** all signers/verifiers compute `bd_hash` the same way.

## End-to-end pipeline (normative)
### Phase A — Authoring and compilation
1. Start with a signed **legal source bundle** (ordinance/ballot measure text + candidate filings + districting definitions).
2. Produce BD CDF (`bd.json`) using deterministic tooling.
3. Produce a **human review artifact** (PDF render) from the same inputs.

**MUST:** the PDF render is generated from the exact `bd.json` that will be published.

### Phase B — Independent reproduction
At least two independent teams MUST reproduce the BD from the legal source bundle.
- If the two independent `bd_hash` values differ, the election MUST halt until resolved.

### Phase C — Parameter ceremony (binding)
Bind the ballot definition into an **ElectionParameterBundle (EPB)**:
- `election_id`, `ballot_definition_hash`, `election_public_key`, trustee/witness policy, disclosure policy, crypto policy.

Then:
1. Multi-party sign the EPB.
2. Submit EPB to the **Parameter/Key Transparency log** (PKT) and obtain inclusion+consistency proofs.
3. Require a witness quorum checkpoint for EPB finalization.

**MUST:** client software refuses to CAST if it cannot verify a quorum-final EPB.

### Phase D — Distribution
Distribute BD via multiple independent channels:
- official site
- multiple mirrors (NGO/party/university)
- transparency-log fetch by hash

**MUST:** every distribution endpoint is content-addressed (hash pinned) and provides integrity proofs.

### Phase E — Continuous monitoring
- Run canary retrieval from diverse networks.
- Publicly log any retrieval variance.

## Failure modes and responses
- **BD mismatch discovered pre-election:** halt; republish EPB; invalidate prior EPB.
- **Targeted BD served (split-view):** publish evidence; freeze affected precincts; switch to paper-of-record adjudication; trigger incident process.
- **Late change pressure:** only via new EPB version with explicit delta documentation.

## Artifacts in this pack
- `artifacts/checklists/ballot-definition-pipeline-checklist.md`
- `artifacts/test-vectors/jcs_canonicalization_vectors.json`
- `artifacts/test-vectors/ballot_definition_release_example.json`

## References
- NIST SP 1500‑20 Ballot Definition CDF.
- NIST GCR 24‑058 Implementation Guidance for Common Data Formats.
- RFC 8785 JSON Canonicalization Scheme (JCS).