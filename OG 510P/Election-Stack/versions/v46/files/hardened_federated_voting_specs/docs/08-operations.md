# Operations hardening runbook (paranoid)

**Track:** A (Deployable core)


This system’s security is dominated by **operations**: key ceremonies, build pipelines, logging, and incident response.

## 1) Segmentation (non-negotiable)
- Election Management Systems (EMS) MUST be isolated from the Internet (NIST warning).  
  Reference: https://www.nist.gov/itl/voting/security-recommendations
- Internet-facing components MUST be limited to the Public Bulletin Board (PBB) and public verification endpoints.
- Management planes MUST be physically and logically separated; no shared credentials.

## 2) Keys and ceremonies
- Threshold cryptography for any decryption capability (no single key holder).
- Dual control + split knowledge for ceremony steps.
- HSMs for signing keys where feasible; otherwise, hardware-backed and auditable signing.

See also: `05-key-management.md` and `artifacts/checklists/key-ceremony-checklist.md`.

## 3) Supply-chain security (mandatory)
### 3.1 Secure development practices (SSDF)
Adopt NIST SSDF practices across the SDLC.  
Reference: https://csrc.nist.gov/pubs/sp/800/218/final

### 3.2 Cyber supply-chain risk management (C-SCRM)
Integrate supplier and component risk management into governance and procurement.  
Reference: https://csrc.nist.gov/pubs/sp/800/161/r1/final

### 3.3 Provenance, step-by-step integrity, and updates
- Provenance attestations (SLSA): https://slsa.dev/spec/v1.0/
- Pipeline integrity (in-toto): https://www.usenix.org/system/files/sec19-torres-arias.pdf
- Secure update framework (TUF): https://theupdateframework.github.io/specification/latest/

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
