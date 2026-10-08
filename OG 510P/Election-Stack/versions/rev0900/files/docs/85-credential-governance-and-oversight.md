# 85 — Credential governance and oversight

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

Credential systems fail as much from governance weaknesses as from cryptography.

## Separation of duties
- CSP operations MUST be separate from vote casting infrastructure operations.
- ETI keys and policies MUST be governed by a multi-stakeholder oversight process.

## Required public artifacts
- Credential policy (enrollment, recovery, revocation, appeal).
- Equity Impact Assessment (what IDs are required; how exceptions are handled).
- Transparency metrics (aggregate counts, outage metrics, incident summaries).

## Independent oversight
- Annual third-party security assessment.
- Public vulnerability disclosure program.
- Election-specific red team exercises focusing on enrollment and recovery.

## Appeals and redress
- Must provide an appeal process usable without smartphones.
- Must publish timelines and escalation points.

## Alignment
- Follow NIST digital identity assurance concepts and management process expectations.
- For WebAuthn use, require origin-bound credential policies to reduce phishing.