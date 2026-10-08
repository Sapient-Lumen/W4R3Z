# 80 — Identity proofing and equity constraints

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

This section defines how the system interprets “citizen keys” in a way that is **auditable, equitable, and recoverable**.

## Franchise scope note

This identity-proofing surface is written for **human** enfranchisement rules in adopting jurisdictions.
Non-human franchise / AI standing is explicitly **not claimed** (see `docs/167` N‑7) and treated as research (`docs/172.6`).


## Anchor: NIST Digital Identity Guidelines
Use NIST SP 800-63-4 volumes as the baseline vocabulary and requirements for:
- **Identity Assurance Level (IAL)** — identity proofing strength
- **Authenticator Assurance Level (AAL)** — authentication strength
- **Federation Assurance Level (FAL)** — federation/assertion strength

Elections are high-stakes; however, *equity and availability are also high-stakes*. Do not set proofing requirements that produce predictable disenfranchisement.

## Recommended enrollment profiles
### Profile P1 (default): In-person proofing + hardware-backed authenticator
- Primary path for initial issuance and high-risk recovery.
- Targets strong IAL/AAL without placing undue burden on remote users.

### Profile P2 (accessibility): Assisted enrollment
- In-person or supervised enrollment with assistive technology support.
- Explicit rules: assistance MUST NOT obtain transferable proof of vote or token minting.

### Profile P3 (optional, higher risk): Remote proofing
Remote proofing is allowed only if:
- it meets a published assurance level target,
- it is backed by independent audits and fraud monitoring,
- it has an appeal path that is not purely digital.

## Equity constraints (normative)
- MUST publish an **Equity Impact Assessment** for enrollment/recovery requirements.
- MUST provide at least one **non-smartphone** path.
- MUST provide language access and accessibility (WCAG-style expectations) for all critical flows.
- MUST provide a same-day “election-week” recovery SLA via in-person channels.

## Remote proofing cautions
Remote proofing is vulnerable to:
- synthetic identity and document forgery,
- deepfake/liveness bypass,
- coercive environments.

If remote proofing is enabled, it MUST be treated as a *separate subsystem* with its own risk register items and “kill switch” procedures.

## Privacy
Proofing records contain sensitive PII. The system MUST:
- minimize retention,
- separate proofing systems from voting systems,
- support independent oversight and redress.

See also `73-vrdb-integrity-and-availability.md` for VRDB handling and `79-credential-lifecycle-and-recovery.md`.