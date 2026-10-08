# Credential issuance & recovery checklist (citizen keys)

**Track:** Shared (cross-cutting)


- [ ] Issuance is anchored in **in-person identity proofing** (or equivalent high-assurance process).
- [ ] Credential private keys are **hardware-backed and non-exportable**.
- [ ] Credential UX is **phishing-resistant** (origin-bound; no generic signing prompts).
- [ ] Lost credential recovery process:
  - [ ] documented, audited, and time-bounded
  - [ ] produces a signed revocation update within SLA
- [ ] Revocation updates are **public, append-only, and mirrored**.
- [ ] Eligibility for casting uses **unlinkable spend-once tokens** (not long-term credential signatures on ballots).
- [ ] Accessibility accommodations documented (assistive devices, caregivers, etc.) without leaking vote.
- [ ] Red-team exercise for: fraudulent issuance, revocation suppression, and recovery-channel takeover.

