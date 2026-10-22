# RFC-0039: Volition tokens and a trusted UI path (D-VOLITION)

Status: Draft  
Updated: 2026-02-24  
Decision node(s): D-VOLITION, D-POWERBOX

## Summary
Add an optional **trusted UI path** seam for capability UX: a user-space “UI root” emits a signed **CH-VOL v0** token that binds a concrete user gesture to the canonical consent summary for a specific action digest. IF-CONSENT uses CH-VOL to mint CH-AUTHZ for high-risk actions, reducing “UI spoofing / clickjacking” confused-deputy failures.

## Motivation
Capability systems are good at “who holds authority,” but weak at “did a human *really* authorize this action?” because the user’s UI is typically untrusted and can be spoofed. EROS highlighted that you need traceability of **user volition**: a trusted path that ties user gestures to effects.

We already bind approvals to action digests (I-AUTHZ-1, I-CONSENT-1), but we lack an explicit *gesture evidence* seam to prevent:
- an untrusted app presenting a misleading prompt and then requesting an unrelated high-risk approval;
- clickjacking-style overlays that trick a user into approving something they did not understand.

## Integration seam / kernel impact (keep small)
Keep all UI logic out of the kernel. The only mechanism assumptions are:
- input devices and the display “front buffer” are assigned to a **UI root** component as explicit IO capabilities (D-DRVDOM/I-IORES-1), and
- the UI root’s signing key is pinned by policy (e.g., allowlisted in CH-CFG or endorsed via D-AUTHAGENT).

Optional hardening: **secure attention sequence (SAS)**.
- Some deployments want a non-spoofable way to enter the “secure UI mode” used for login/lock or high-risk consent. A SAS is a key chord or hardware event delivered to the secure UI component in a way normal applications cannot intercept.
- This does not require moving UI into the kernel; it only requires a narrowly-scoped input-routing rule: SAS events are reserved and routed exclusively to the UI root (or a designated secure-mode component).
- This mirrors the classic Ctrl+Alt+Del pattern used to ensure the credential UI is genuine.

No new IF-* surface is required: this extends IF-CONSENT’s input validation (it already mints CH-AUTHZ in user space).

## Design
### A) Volition token (CH-VOL v0)
CH-VOL is an evidence token that binds:
- `action_digest` + `action_schema`, and
- `summary_digest` (digest of a canonical-rendered consent summary),
to:
- a specific user gesture kind and nonce,
- a validity window, and
- an issuer identity (the UI root).

See: `docs/30-architecture/volition-token-schema-v0.md`.

### B) Canonical consent summary
The consent UI must render a canonical summary derived from action bytes/digest (I-CONSENT-1). The summary profile is policy-selected (e.g., “hi_risk” includes extra context like target identities and irreversible effects). The UI root produces `summary_digest = H(canonical_summary_bytes)` and includes it in CH-VOL.

### C) Consent issuance rule (tight)
For action classes marked “requires volition” (policy):
1) UI root renders the canonical summary for the action (or receives it from the validator, then re-derives and checks).
2) user performs a gesture (e.g., hold-to-approve).
3) UI root emits CH-VOL.
4) IF-CONSENT validates CH-VOL (signature + freshness + summary digest match) and then issues CH-AUTHZ bound to the same action digest.

Transcript linkage:
- IF-CONSENT logs `vol_ref = digest(CH-VOL)` alongside `authz_ref = digest(CH-AUTHZ)` in CH-LOG (optional but recommended).

### D) Headless / remote workflows
If no UI is present, profiles can:
- disable D-VOLITION entirely; or
- require non-human approvals (quorum, hardware attestation, policy) under CH-AUTHZ issuer kinds.
CH-VOL never substitutes for CH-AUTHZ; it is only additional evidence used by IF-CONSENT.

## Registries impacted
- Decision map: add D-VOLITION (done).
- CH registry: add CH-VOL v0 (done).
- I registry: add I-VOLITION-1 (this RFC).
- PO registry: add PO-VOL-VALIDATE, PO-VOL-NOREPLAY (this RFC).
- IF registry: augment IF-CONSENT controls to include I-VOLITION-1/PO-VOL-VALIDATE when D-VOLITION is enabled.

## Threat-model impact
Reduces confused-deputy risks from untrusted UI, but introduces a new trusted component: the UI root.
Assumptions:
- UI root has exclusive access to the trusted input and trusted presentation surface (profile-defined).
- UI root signing keys are pinned/allowlisted; compromise of UI root is a high-impact event.

Out of scope:
- defending against a fully compromised UI root;
- side channels (timing/power) through user input devices.

## Assurance/verification impact
New invariant:
- **I-VOLITION-1 (Volition binding, optional):** when D-VOLITION is enabled, any CH-AUTHZ minted for an action class requiring volition must be traceable to a fresh, valid CH-VOL whose `action_digest` matches, and whose `summary_digest` matches the canonical summary actually rendered by the trusted UI path.

New proof obligations:
- **PO-VOL-VALIDATE:** consent service validation of CH-VOL is total and fail-closed; proof verifies under policy; summary digest match is enforced.
- **PO-VOL-NOREPLAY:** CH-VOL nonces are one-shot within the replay window; replays reject deterministically.

## Observability / operations impact
- IF-OBS can export redacted counts of “volition-required approvals” vs “other approvals.”
- Logs should record only digests (vol_ref/authz_ref), not raw proofs, by default (align with I-OBS-1).

## Alternatives
- “Just display the digest”: improves auditability but does not address UI spoofing.
- Push UI into the kernel: rejected; would explode trusted computing base and proof surface.
- Rely only on hardware UI attestation: viable for some devices, but too restrictive for general profiles; CH-VOL is compatible with both software and hardware attest modes.

## Evidence plan
Phase 1:
- Prototype UI root + consent overlay in user space; wire to IF-ACP with a small allowlist of high-risk actions.
- Property tests: CH-VOL replay rejected; CH-VOL bound to wrong action digest rejects; summary digest mismatch rejects.

Phase 2:
- Threat-driven UI tests: spoofed app windows cannot produce CH-VOL; clickjacking overlay attempts do not mint CH-VOL.
- Optional: model-check a tiny state machine for the “render→gesture→token→authz” path.

## References
REF-EROS-EWS-SEC04, REF-CAPMYTHS, REF-OPENBSD-PLEDGE, REF-MS-WINLOGON-SAS.
