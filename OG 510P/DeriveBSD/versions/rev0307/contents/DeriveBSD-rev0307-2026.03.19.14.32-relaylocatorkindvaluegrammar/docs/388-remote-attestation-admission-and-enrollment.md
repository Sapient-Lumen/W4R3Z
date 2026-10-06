# Remote attestation: admission, enrollment, and “what is gated?” (optional)

DeriveBSD already treats local measurements as evidence (`boot.attestation`, `attestation.receipt`).
The missing “ecosystem completion” step is **remote attestation as an admission primitive**:

- *who* is allowed to join a fleet,
- *when* secrets can be unsealed,
- *when* workload identity is issued,
- *when* updates/rollbacks are permitted.

Keylime is a useful reference because it is operationally minded (agent + registrar + verifier), and it treats event-log analysis as a core activity.

## The stance

- **Optional lane:** remote attestation infrastructure exists, but is not required for single-node systems.
- **Principle:** attestation affects **admission decisions**, not just dashboards.
- **Make it reviewable:** “what is gated by attestation?” must be a typed policy artifact.

## Product-shape default now fixed

The archive now makes the A–D default explicit in `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`:

- **A** treats measured platform posture as receipted evidence that can gate sensitive admissions by default.
- **B** keeps measured posture visible/exportable, while limiting default attestation gates to sensitive operations rather than ordinary local use.
- **C** keeps attestation optional/exportable, with explicit gates available where a deployment chooses them.
- **D** retains measured posture and uses it for production enrollment, maintenance access, or sensitive release gates by default.

This doc still describes the lane mechanics; `docs/469-...` fixes the product default.

## What we steal (Keylime-shaped lessons)

### 1) Registration and identity are separate steps

Bootstrapping is messy.
A dedicated registrar step makes it explicit when a host becomes eligible for verification.

### 2) Verifier results are reusable, expiring receipts

Don’t embed attestation checks into every subsystem.
Emit receipts with a clear freshness bound and let other gates reference them.

The consuming gate still needs its own authority receipt. In v0 that means action receipts such as `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt` should summarize the attestation decision they consumed via `attestation_verification`.

We already have this shape in `spec/attestation.receipt.schema.json`.

### 3) Event-log parsing is a first-class surface

If we rely on TPM event log analysis, it is a **parser surface** and must show up in the parser registry.
See: `docs/376-parser-surface-registry-and-fuzz-gates.md`.

## New missing artifact: `attestation.admission.policy`

We add a small, typed policy surface that answers:

> “Which actions are attestation-gated, and by which requirement?”

This prevents “attestation theater”, where receipts exist but nothing depends on them.

### Schema

- `spec/attestation.admission.policy.schema.json`
- Example: `spec/examples/attestation.admission.policy.json`

### Shape

- `rules[]` map:
  - an **action** (issue identity, unseal secrets, join cluster, promote update, allow remote admin session)
  - a **subject selector** (fleet labels / host classes)
  - a referenced **`attestation.requirement`** digest/id

This policy becomes:
- a reviewable diff on change,
- an input to the policy engine,
- visible in the Permission Center (“why is this blocked?”).

## Where this plugs in

- **Workload identity issuance** can require fresh `attestation.receipt`.
  - See: `docs/181-workload-identity-and-secretless-deploys.md`

- **Sealed secrets + unsealing** should be conditional on a passing receipt.
  - See: `docs/272-sealed-secrets-attested-unsealing.md`

- **Fleet admission / orchestration** gates use attestation as a hard predicate.

- **Remote assistance** can be allowed only when the host is in a verified posture.
  - See: `docs/291-remote-assistance-sessions-as-evidence.md`

## Operational ergonomics

- Receipts must be cheap to query.
- Make freshness visible (countdown to expiry).
- Keep failures explainable (reason codes, not mystery).

## Non-goals

- Building a full Keylime clone inside the base system.
- Making remote attestation mandatory for every hobby deployment.

## References

- Red Hat Enterprise Linux 10: Ensuring system integrity with Keylime:
  - https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/security_hardening/ensuring-system-integrity-with-keylime
- Microsoft Device Health Attestation (measured boot report as admission input):
  - https://learn.microsoft.com/en-us/windows-server/security/device-health-attestation
- Azure Trusted Launch for Azure VMs (vTPM / measured boot / attestation overview):
  - https://learn.microsoft.com/en-us/azure/virtual-machines/trusted-launch

Last updated: 2026-03-07r221
