# Supply chain & build integrity (election-grade)

**Track:** A+C (Core + North Star)


Election systems fail through updates, dependencies, and build pipelines.



**Clarification (Track A reality):** These controls primarily apply to the **evidence/verification infrastructure**
(verifiers, packet builders, monitors) that this archive specifies.
Many jurisdictions use proprietary voting system stacks with limited supply-chain transparency.
Track A does not assume those systems meet these controls; it assumes a paper ballot of record and uses audits/recounts as recovery.

**Important:** when the voting system is opaque, the evidence layer is compensating for opacity it cannot eliminate.
The value of the evidence layer increases with the transparency of the system it wraps.

## Track A wrapper transparency recommendations (for opaque vendors)

These are **recommendations**, not hard Track A requirements. They increase how much the evidence layer can settle in a dispute:

- **Declare what ran (minimum):** publish certified configuration IDs + vendor version strings used during the election.
- **Prove what ran (better):** publish signed hashes of installed packages/firmware images + update history (who authorized, when).
- **Make update channels inspectable:** publish change notices as PublicNotice artifacts; pin hashes of update bundles.
- **Align incident evidence:** when a vendor asserts “this was not the system,” require a hash-addressed exhibit or it is just narrative.

When these are absent, Track A still helps (it can prove what the public surfaces said and when, and it supports recovery), but root-cause attribution becomes harder.


Authoritative sources (selected):
- NIST SSDF (SP 800-218) (`xref: nist_sp800_218_final_html`)
- NIST C-SCRM (SP 800-161 Rev.1 Update 1) (`xref: nist_sp800_161r1_upd1_final_html`)
- SLSA spec (`xref: slsa_spec_v1_2`)
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
