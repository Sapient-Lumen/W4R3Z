# Operations hardening runbook (paranoid)

**Track:** A (Deployable core)

> **Read-first:** before treating anything here as deployment guidance, read `166-scope-and-claims-contract.md` and `167-non-claims-and-boundaries.md` (they are binding on interpretation).



This system’s security is dominated by **operations**: key ceremonies, build pipelines, logging, and incident response.

If you want a compact “what exists when” view across the real-world election timeline,
see `215-election-lifecycle-evidence-map.md`.

If you are triaging an incident and need a symptom→packet map, see `216-incident-triage-and-evidence-quickmap.md`.

If you are publishing public updates during an incident or dispute, see `219-uncertainty-safe-public-updates.md` (tags + update commitments).

If you are monitoring PublicNotice feeds and need a bounded parity-failure handoff bundle, see `221-publicnotice-monitoring-and-convergence.md` and `222-publicnotice-divergence-dispute-bundle-minspec.md`.

## 1) Segmentation (non-negotiable)
- Election Management Systems (EMS) MUST be isolated from the Internet (NIST warning).  
  Reference: `xref: nist_voting_security_recommendations_page`
- Internet-facing components MUST be limited to the Public Bulletin Board (PBB) and public verification endpoints.
- Management planes MUST be physically and logically separated; no shared credentials.

## 2) Keys and ceremonies
- Threshold cryptography for any decryption capability (no single key holder).
- Dual control + split knowledge for ceremony steps.
- HSMs for signing keys where feasible; otherwise, hardware-backed and auditable signing.

See also: `05-key-management.md` and `artifacts/checklists/key-ceremony-checklist.md`.

## 3) Supply-chain security (mandatory)

### 3.1 Secure development practices (SSDF)
Adopt NIST SSDF practices across the SDLC (`xref: nist_sp800_218_final_html`).

Track emerging SSDF revisions as they progress (e.g., SP 800-218r1 IPD) (`xref: nist_sp800_218_r1_ipd_html`).

### 3.2 Cyber supply-chain risk management (C-SCRM)
Integrate supplier and component risk management into governance and procurement (`xref: nist_sp800_161r1_upd1_final_html`).

### 3.3 Provenance, step-by-step integrity, and updates
- Provenance attestations (SLSA) (`xref: slsa_spec_v1_2`).
- Pipeline integrity (in-toto) (`xref: usenix_intoto_pipeline_integrity_pdf`).
- Secure update framework (TUF) (`xref: tuf_spec_latest_html`).

**Rule:** You cannot “patch your way” out of a compromised updater.

## 4) Deployment model
- Immutable infrastructure (signed images; verify at boot).
- No SSH into production. Break-glass access requires dual authorization + full recording.
- Strict time-bound credentials; no long-lived tokens in CI/CD or ops.

## 5) Monitoring & independent verification
Independent monitors MUST continuously:
- mirror the log,
- verify inclusion/consistency proofs,
- detect split views (equivocation),
- detect anomalous submission patterns and regional drops.

Monitors SHOULD be run by organizations not involved in operating core servers.

## 6) DDoS and partition posture
- Assume the internet will be unstable on election day.
- Provide multiple anycast entrypoints + multiple domain names + mirror endpoints.
- Never “finalize” conflicting histories without witness quorum.

## 7) Incident response (pre-written)
Define before launch:
- anomaly thresholds and who can pause remote return,
- safe fallback communications to voters,
- forensic evidence retention (write-once logs),
- public transparency commitments.

## 8) Public transparency commitments
To earn trust:
- publish source, reproducible builds, hashes,
- publish verifiers and test vectors,
- publish a public postmortem process for incidents.
