# Procurement language template (security requirements)

> This is a **template you can adapt** for RFPs / contracts. It is intentionally demanding.

## 1) Transparency and evaluability
Vendor MUST provide:
- complete source for all security-critical components,
- build instructions and reproducible build support,
- cryptographic verifier tooling and public test vectors,
- documented threat model and security claims (and non-claims).

## 2) End-to-end verifiability support
If the system claims E2E verifiability, vendor MUST provide:
- public evidence sufficient to independently verify inclusion and tally correctness,
- documentation mapping protocol claims to VVSG 2.0 requirements where applicable,
- a public artifact publication plan (logs, proofs, parameters).

## 3) Secure software development (SSDF)
Vendor MUST implement NIST SSDF practices (SP 800-218) and provide:
- SDLC security process documentation,
- vulnerability disclosure process and timelines,
- SAST/DAST and dependency management evidence.

## 4) Supply-chain security (C-SCRM + provenance)
Vendor MUST:
- maintain a component inventory (SBOM) for releases,
- provide build provenance attestations (SLSA-style),
- implement end-to-end pipeline integrity controls (in-toto or equivalent),
- secure updates using a TUF-like framework.

## 5) Key management
Vendor MUST support:
- threshold key ceremonies with public documentation,
- HSM integration where applicable,
- dual control / split knowledge for high-impact keys,
- audited revocation and re-issuance mechanisms.

## 6) Operational security
Vendor MUST provide:
- hardening guides and secure defaults,
- logging and monitoring integration that supports independent auditors,
- incident response playbooks and escalation paths.

## 7) Client and coercion risk disclosures
Vendor MUST:
- explicitly document client malware and coercion limitations,
- document mitigations offered (cast-or-spoil, second-device verification, return codes, supervised override),
- ensure receipts cannot be used as proof-of-vote.

