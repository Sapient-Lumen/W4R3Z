# Rejected attestation does not silently mint ordinary authority; breakglass stays explicit

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt

The archive already fixed two major attestation questions:

- decisive consuming receipts pin the exact requirement/receipt/policy tuple, and
- degraded admission must already be in the reviewed requirement.

What still needed one more hard cut was the meaning of **`rejected`** when an authority lane is still tempted to “help” the operator.

If DeriveBSD leaves that fuzzy, secret brokers and identity agents will quietly do the dangerous thing:
record a rejected attestation decision, but still succeed in the ordinary lane.
That would make notes, dashboards, or sticky verifier state the real override mechanism.

Related:
- ADR: `adrs/ADR-0237-rejected-attestation-does-not-silently-mint-ordinary-authority-breakglass-stays-explicit.md`
- action-side exact tuple boundary: `docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md`
- degraded-admission boundary: `docs/646-attestation-degraded-admission-stays-requirement-shaped-and-no-hidden-waivers.md`
- workload identity lane: `docs/181-workload-identity-and-secretless-deploys.md`
- secret lane: `docs/223-secrets-and-key-management-as-evidence.md`
- recovery lane: `docs/236-breakglass-and-recovery-mode.md`

## The boundary

In v0, ordinary issue/delivery lanes are **fail-closed on rejected attestation**.

That means:

- `workload-identity-issue-receipt` never uses `attestation_verification.decision = rejected`.
- `secret-receipt` delivery actions (`materialize`, `fetch`, `unseal`) must not report successful ordinary delivery when `attestation_verification.decision = rejected`.
- if operators must proceed despite rejected posture, the action must move into an already-authoritative emergency lane such as breakglass.
- breakglass may explicitly record `attestation_verification.decision = rejected` because breakglass itself is the emergency authority object.
- any later ordinary attestation-gated lanes still need fresh post-breakglass attestation instead of inheriting emergency-state authority.

## Why this matters

### 1) It keeps ordinary authority receipts semantically honest

A successful workload-identity issue receipt means a credential was actually issued.
A successful ordinary secret-delivery receipt means the secret was actually delivered.
Those receipts should not double as hidden override records for a rejected attestation gate.

### 2) It keeps breakglass meaningfully distinct

The archive already had an explicit emergency lane.
Letting normal issue/delivery flows silently succeed on `rejected` would erase the practical difference between ordinary authority and emergency authority.

### 3) It keeps A/B/C/D coherent

- **A / fleet host:** secret release and workload identity fail closed on rejected posture; emergency recovery stays on the explicit breakglass lane.
- **B / workstation:** trusted UI can explain that ordinary issuance was denied while recovery used a visibly different authority path.
- **C / general-purpose OS:** optional attestation remains explicit when used, instead of turning into invisible override folklore.
- **D / appliance factory / regulatory:** audit review can prove that ordinary authority did not silently succeed after rejected posture, while emergency recovery still remained receipted.

## Schema/example consequence

The canonical ordinary authority schemas now teach this explicitly:

- `spec/workload.identity.issue.receipt.schema.json` forbids `attestation_verification.decision = rejected`.
- `spec/secret.receipt.schema.json` forbids successful `materialize` / `fetch` / `unseal` when `attestation_verification.decision = rejected`.
- `spec/breakglass.receipt.schema.json` teaches the complementary rule: breakglass may explicitly record `rejected` because it is the emergency lane.

The archive also carries concrete examples:

- `spec/examples/secret.receipt.rejected.json`
- `spec/examples/breakglass.receipt.rejected.json`

That keeps the boundary checkable instead of aspirational. In plain terms: ordinary issue/delivery lanes are fail-closed on rejected attestation, and the archive rejects silent success in those normal authority lanes.

## Guardrail

`tools/check_attestation_rejected_override_contract.py`

This guardrail checks that:

- ordinary secret delivery cannot silently succeed on `rejected`,
- workload identity issue receipts cannot encode `rejected`,
- breakglass remains the explicit lane allowed to carry a successful rejected-posture crossing,
- and the canonical examples teach both the fail-closed ordinary path and the explicit breakglass recovery path.

## What stays open

This cut does **not** settle:

- the full future denied-receipt/event vocabulary for every attestation-gated lane,
- every product-profile default sensitive-action set,
- or whether additional explicit emergency lanes are worth designing later.

It only makes one narrow decision now:
**ordinary authority does not silently succeed on rejected posture; explicit recovery must move into breakglass instead.**

Last updated: 2026-03-21r379
