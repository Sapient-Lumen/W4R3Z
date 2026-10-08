# 246. Assurance-case skeleton and evidence minimization

**Track:** Shared

This doc is a **maintainer-facing pattern**: how to express *why the stack should be trusted* without ballooning the archive, and how to keep “assurance” grounded in **checkable evidence** rather than narrative.

It is intentionally **not** a compliance checklist. External standards and guidance are treated as *anchors* to help reviewers orient, not as the source of truth for the stack. See `docs/245-external-standards-and-alignment-map.md`.


## 1) The shortest useful assurance case

A deployer should be able to answer three questions, each with **concrete evidence pointers**:

1. **What is the system boundary?** (what is in-scope / out-of-scope)
2. **What failure modes are we defending against?** (threat model)
3. **How do observers verify outcomes anyway?** (verification + audit path)

In this archive those entrypoints are:
- Boundary + scope: `docs/154-project-scope-and-track-map.md`
- Threat model: `docs/01-threat-model.md` and `docs/243-archive-self-threat-model-and-spec-correctness.md`
- Verification path: `docs/02-architecture.md`, `docs/04-transparency-log.md`, `docs/09-audit-recovery.md`, `docs/10-assurance-plan.md`


## 2) A claim tree you can actually maintain

Use a shallow “goal / subgoal / evidence” structure (GSN-like, without the ceremony):

### Top claim (C0)
**C0:** *Given the declared threat model and scope, the reported outcome is verifiable and resilient to undetected manipulation.*

Break C0 into a small fixed set of subclaims (keep this stable over time):

- **C1 — Outcome integrity:** tallies match eligible cast ballots and the tallying procedure.
- **C2 — End-to-end verifiability:** independent observers can detect (with high probability) outcome-changing manipulation.
- **C3 — Availability + recoverability:** service interruptions do not silently alter outcomes; recovery preserves auditability.
- **C4 — Privacy + coercion posture:** ballot secrecy is preserved to the stated level; coercion risks are bounded and explicit.
- **C5 — Operational integrity:** key custody, deployment discipline, and monitoring reduce non-cryptographic failure modes.

Each subclaim must point to **two kinds of evidence**:
- **Design evidence:** invariants, protocol and artifact specs (the “what”).
- **Empirical evidence:** tests, reproducible simulations, independent re-implementations, and monitoring results (the “did it actually behave”).

If a subclaim can’t be backed with *both* kinds, mark it as **research posture** and keep it out of Track A.


## 3) Evidence minimization rules (how to avoid archive bloat)

1. **Prefer pointers over prose.** Replace paragraphs with a small set of canonical links:
   - `docs/*` for specs,
   - `artifacts/*` for operational templates and claims,
   - `schemas/*` for data formats,
   - `tools/*` for verifiers / monitors,
   - `evidence/*` for third-party reviews and reproducible results.

2. **Prefer hashes over screenshots.** If you need to reference a build, artifact bundle, or public log snapshot:
   - store a hash + a retrieval recipe,
   - avoid storing bulky binaries or duplicated data.

3. **One metric, one question.** Each measurement must answer a single verifier question (e.g., “split-view detected within X minutes under Y adversary model”), and link to:
   - the script that produced it, and
   - the raw input boundaries (what was sampled, when, and why).

4. **Normalize evidence vocabulary.** Use a small fixed vocabulary for evidence types:
   - `SPEC`, `FORMAL`, `TEST`, `REDTEAM`, `INDEP_IMPL`, `MONITOR`, `AUDIT`, `OPS`.
   This prevents “new document per adjective” syndrome.

5. **External docs are anchors, not annexes.** When referencing standards/guidance, cite them once, then link back to the relevant internal surfaces (avoid pasting text). Useful anchors include EAC VVSG 2.0, NIST’s election infrastructure cybersecurity profile, and CISA election security guidance. (See citations below.)


## 4) A tiny crosswalk (anchors → stack evidence surfaces)

This is a **starter** crosswalk. Keep it short; expand only when it prevents repeated review confusion.

| Anchor theme | Why reviewers care | Stack surfaces to cite (examples) |
|---|---|---|
| Baseline voting-system security + accessibility requirements | “Does this resemble real-world expectations?” | `docs/245-*`, `docs/06-client-security.md`, `docs/05-key-management.md`, `docs/108-language-device-parity-and-ui-integrity.md` |
| Cyber risk management lifecycle (Identify/Protect/Detect/Respond/Recover) | “What do you do when things go wrong?” | `docs/08-operations.md`, `docs/09-audit-recovery.md`, `docs/10-assurance-plan.md`, `artifacts/playbooks/*` |
| Electronic ballot delivery/marking/return risk posture | “Are you honest about remote-return limits?” | Track B docs + explicit risk acceptance surfaces (see `docs/154-*`) |
| Verification + audits | “Can independent observers verify?” | `docs/04-transparency-log.md`, `observer-kit/*`, `tools/*`, `docs/09-audit-recovery.md` |


## 5) “Stop conditions” for risky expansions (especially remote return)

If a Track B proposal increases coercion, malware exposure, or unverifiable paths, it must ship with:
- an explicit **risk posture statement** (who bears what risk, and why it is acceptable),
- a clear **detection story** (what would show we’re wrong),
- a **rollback story** (how to revert without losing auditability).

For electronic ballot return specifically, treat external guidance as a signal that many mitigations are partial and trade-off heavy; the stack should not imply a solved problem where none exists. Use Track B to explore, and keep Track A conservative. (See cited guidance and analyses below.)


## 6) Citations (anchors)

- EAC: Voluntary Voting System Guidelines (VVSG) 2.0 requirements (Feb 2021): https://www.eac.gov/sites/default/files/TestingCertification/Voluntary_Voting_System_Guidelines_Version_2_0.pdf
- NIST: Cybersecurity Framework Election Infrastructure Profile (NIST VTS 200-1, Jan 2024): https://nvlpubs.nist.gov/nistpubs/vts/NIST.VTS.200-1.pdf
- CISA: Best Practices for Securing Election Systems: https://www.cisa.gov/best-practices-securing-election-systems
- CISA/EAC/FBI/etc: Risk Management for Electronic Ballot Delivery, Marking, and Return (May 2020): https://www.cisa.gov/sites/default/files/2024-02/Final_%20Risk_Management_for_Electronic-Ballot_05082020_508c.pdf
- Bipartisan Policy Center: Balancing Security, Access, and Privacy in Electronic Ballot Transmission (Apr 2022): https://bipartisanpolicy.org/wp-content/uploads/2022/03/BPC_ElectronicBallotTransmission_Revised_411.pdf
