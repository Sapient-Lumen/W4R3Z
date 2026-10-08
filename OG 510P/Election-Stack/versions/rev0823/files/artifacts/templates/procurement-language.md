# Procurement language template (security requirements)

**Track:** Shared (cross-cutting)


> This is a **template you can adapt** for RFPs / contracts. It is intentionally demanding.

**Scope note:** Many jurisdictions will adopt Track A as an **evidence wrapper** around an existing (often proprietary) voting system.
If you are procuring the **evidence/verification infrastructure** (packet builders, verifiers, monitoring, mirrors), the “open + reproducible” requirements below apply directly.
If you are procuring a conventional proprietary voting system you cannot force open, use §9 (wrapper transparency) and keep the **publication/MAPT** requirements.

## 1) Transparency and evaluability
Vendor MUST provide:
- complete source for all security-critical components **in the procured evidence/verification path** (and for any voting system that claims E2E verifiability),
- build instructions and reproducible build support,
- cryptographic verifier tooling and public test vectors,
- documented threat model and security claims (and non-claims).

## 2) End-to-end verifiability support
If the system claims E2E verifiability, vendor MUST provide:
- public evidence sufficient to independently verify inclusion and tally correctness,
- documentation mapping protocol claims to VVSG 2.0 requirements where applicable,
- a public artifact publication plan (logs, proofs, parameters).
- publication outputs MUST pass MAPT (minimal adversarial publication test; `docs/187`) — stable URLs, indexed bundles/manifests, machine-readable formats, and digest-first verification (no “PDF scan compliance”).
- public status/incident updates MUST support epistemic tagging + correction-chain semantics (`docs/218–220`) so uncertainty is explicit and updates are auditable (avoid hedging language as a substitute for evidence).

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

## 8) Anti-capture / interoperability (no verification chokepoint)

Vendor MUST NOT make verification practically dependent on the vendor’s platform.

Vendor MUST provide and contractually commit that:
- **Core evidence schemas** remain public, versioned, and implementable without license or proprietary SDKs.
- Any schema extensions are published as open JSON Schema (or equivalent) and remain backward compatible or explicitly versioned.
- The **offline verifier** can run without vendor credentials and can verify packets produced by *any* conforming implementation.
- Public evidence (feeds, packets, digests) is accessible without paywalls, “account required” gates, or rate limits that prevent independent monitoring.
- The witness/monitor ecosystem is not operated solely by the vendor; governance and key custody remain independently auditable.

## 9) Track A wrapper transparency for proprietary voting systems (when you can’t demand open source)

If the jurisdiction uses a proprietary voting system, the evidence layer can wrap it but cannot remove its opacity.
Require at minimum:
- certified configuration IDs + vendor version strings used during the election,
- a signed update/change history (who authorized, when, and what changed),
- if feasible, signed hashes of installed packages/firmware images,
- all changes and advisories published as PublicNotice artifacts.

Recommended contract clauses:
- “no proprietary extensions that change meaning of core evidence objects,”
- “data escrow / portability,”
- “termination does not revoke the public’s ability to verify prior elections.”


## 10) Promotion guardrails (anti-capture)

If any experimental surface is promoted into a deployable election-critical role, vendor and jurisdiction MUST follow `docs/229-experiment-to-spec-promotion-protocol.md` (independent security review, adversarial non-claims review, and a published rollback plan).

If the promoted surface includes **remote ballot return**, these clauses are **non‑waivable** (including under “emergency” or equity justifications).
