# 97 — Supply‑chain attestations for verifier tools

**Track:** A+C (Core + North Star)

Goal: observers must be able to answer:
- “Is this verifier binary the one that was audited/reviewed?”
- “Did it come from the expected source and build process?”


## Minimum requirements
- Publish reproducible build instructions for each verifier.
- Publish a signed provenance statement for each release:
  - source repo + commit
  - build system identity
  - dependencies (SBOM where feasible)
  - output artifact hashes


## Recommended (SLSA / in‑toto patterns)
Treat verifier releases like critical infrastructure:
- hardened CI builds and reviewable build definitions (`source: nist_sp800_204d_pdf`)
- provenance attestations aligned with SLSA concepts (`xref: slsa_spec_v1_2`, `xref: slsa_provenance_v1_2_html`)
- portable claim formats (in‑toto Statement v1) (`source: intoto_statement_v1_md`)
- optional DSSE envelopes as an interchange wrapper (`xref: intoto_envelope_v1_md`)

Note: Track A’s signature boundary is still the archive’s `EvidenceEnvelope` (`173`–`176`).
If you publish DSSE artifacts, treat them as content‑addressed attachments and bind them with an envelope.


## Where attestations are stored
- In the same Evidence Portal used for election bundles.
- Optionally in an external transparency log for independent auditing (`04`, `93`, `96`).

See also: `94-independent-verifier-diversity.md`, `98-evidence-bundle-provenance-and-retention.md`.
