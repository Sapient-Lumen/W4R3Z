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

## What we steal (Keylime-shaped lessons)

### 1) Registration and identity are separate steps

Bootstrapping is messy.
A dedicated registrar step makes it explicit when a host becomes eligible for verification.

### 2) Verifier results are reusable, expiring receipts

Don’t embed attestation checks into every subsystem.
Emit receipts with a clear freshness bound and let other gates reference them.

We already have this shape in `spec/attestation.receipt.schema.json`.

### 3) Event-log parsing is a first-class surface

If we rely on TPM event log analysis, it is a **parser surface** and must show up in the parser registry.
See: `docs/376-parser-surface-registry-and-fuzz-gates.md`.

## New missing artifact: attestation admission policy

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
  - a referenced **attestation.requirement** digest/id

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

- Keylime blog: “A Hitchhiker’s Guide to Remote Attestation” (architecture overview):
  - https://keylime.dev/blog/2024/02/07/remote-attestation-blog-part1.html
- Keylime docs: Attestation security (design notes):
  - https://keylime.readthedocs.io/en/latest/design/security.html

Last updated: 2026-02-27r110
