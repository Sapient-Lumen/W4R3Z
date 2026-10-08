# Supply chain & build integrity (election-grade)

**Track:** A+C (Core + North Star)


Election systems fail through updates, dependencies, and build pipelines.

Authoritative sources (selected):
- NIST SSDF (SP 800-218) (`xref: nist_sp800_218_final_html`)
- NIST C-SCRM (SP 800-161r1) (`xref: nist_sp800_161r1_final_html`)
- SLSA spec (`xref: slsa_spec_v1_1_html`)
- in-toto pipeline integrity (paper) (`xref: usenix_intoto_pipeline_integrity_pdf`)
- TUF specification (`xref: tuf_spec_latest_html`)

## Baseline controls (MUST)
- reproducible builds for critical components,
- build provenance / attestations,
- dependency pinning + SBOMs,
- offline signing keys in HSMs with dual control,
- controlled release channels with staged rollouts and rollback.

## Framework alignment (SHOULD)
- NIST SSDF practices mapped into the SDLC.
- C‑SCRM practices for vendors and critical dependencies.
- Harden update distribution using a framework designed for key compromise.

## Practical targets (recommended)
- Achieve SLSA build track targets (>= L2; aspire to L3 for critical components).
- Use TUF-style repository roles to keep updates secure even if some keys are compromised.
- Require independent reproducibility verification by third parties.

## Independent “known-good” verifiers
Publish:
- a minimal verifier (log + proofs + tally) in >=2 independent implementations,
- signed hashes of verifier builds,
- test vectors that auditors can run offline.
