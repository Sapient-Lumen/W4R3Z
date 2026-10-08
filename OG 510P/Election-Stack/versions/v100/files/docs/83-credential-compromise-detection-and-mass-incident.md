# 83 — Credential compromise detection and mass-incident response

**Track:** B (Remote return / hard-mode research)


Assume at least one of the following will occur:
- passkey sync ecosystem compromise,
- CSP administrative compromise,
- insider-driven silent revocations,
- large-scale phishing attempt.

## Detection signals
- Abnormal spikes in token minting attempts.
- Geographic anomalies inconsistent with expected turnout.
- Increased recovery requests correlated with a campaign.
- Divergence between CSP audit logs and ETI mint logs (within privacy constraints).

## Mandatory controls
- **Dual control** for admin actions affecting eligibility.
- Tamper-evident logging for credential events, anchored at least daily.
- Automated “mass-change budget” alarms.

## Mass incident playbook (normative)
1. **Freeze** token minting and/or credential changes for affected cohorts.
2. Publish a signed public statement (anchored) explaining:
   - what is known
   - what is paused
   - what fallbacks are available
3. Rotate relevant keys and refresh trustee/witness checkpoints.
4. Provide emergency in-person issuance at expanded sites.
5. After-action report with evidence bundle.

Template: `artifacts/templates/voter-key-reissuance-notice.md`
Checklist: `artifacts/checklists/mass-compromise-response-checklist.md`