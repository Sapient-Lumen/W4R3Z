# 56 — Proactive Secret Sharing, Share Refresh, and Committee Churn

**Track:** A (Deployable core)


## Why this exists (paranoid assumption)
Over a long enough election lifecycle, **every trustee may eventually be compromised**. If the private key shares remain static, an attacker can accumulate shares over time and later decrypt or forge.

**Proactive Secret Sharing (PSS)** and **Dynamic Committee PSS (DPSS)** reduce this risk by periodically refreshing shares so past compromises do not accumulate indefinitely.

## Applicability
- **Trustees holding tally decryption shares** (critical)
- **Witnesses cosigning checkpoints** (important)
- **Update-signing roles** (if threshold signing is used)

## Threats addressed
- Slow, stealthy compromise of trustees over months/years
- “Harvest now, decrypt later” in multi-election deployments
- Insider churn and committee membership changes

## Normative requirements
1. Systems that reuse trustee infrastructure across elections SHOULD implement a **share refresh schedule**.
2. Refresh ceremonies MUST be publicly logged:
   - participants
   - protocol version
   - transcript commitments
   - success/failure
3. Share refresh MUST NOT change the election public key (unless explicitly rotating keys under a published migration plan).
4. If committee membership changes, the system MUST publish:
   - membership delta
   - new threshold parameters
   - a public justification (policy)

## Minimal practical profile (recommended)
- Use threshold schemes where refresh is operationally feasible.
- Refresh is executed:
  - pre-election (after final trustee roster set)
  - post-election (before archival custody)
  - periodically for long-lived services

## Operational design notes
- Treat refresh as a **key ceremony** with dual control and independent observation.
- Store refresh artifacts in the Evidence Bundle (see `43-evidence-bundles-and-court-proofing.md`).

## Artifact: `ShareRefreshTranscript`
The system records a content-addressed transcript including:
- election_id
- committee roster and threshold
- protocol id
- commitments to messages (hashes)
- signatures of participants

The transcript is published as a PBB entry and optionally anchored externally.

## Caution
PSS/DPSS increases complexity. If the implementation is not mature, prefer:
- shorter-lived election keys
- stronger trustee diversity
- strict physical custody

## References (see `references.md`)
- NIST threshold cryptography discussion and proactive secret sharing examples.