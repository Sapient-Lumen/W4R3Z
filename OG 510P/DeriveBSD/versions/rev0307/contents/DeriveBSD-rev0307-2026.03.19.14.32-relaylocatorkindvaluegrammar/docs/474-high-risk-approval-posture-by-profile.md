# High-risk approval posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability, isolation  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already has strong approval primitives.
What this doc decides is narrower and more important for coherence:
**what is the default posture for high-risk approvals in each product shape?**

This is intentionally **not** a workflow-engine or ticket-system doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0064-high-risk-approval-posture-by-profile.md`
- multiparty approvals: `docs/288-multiparty-approvals-and-separation-of-duties.md`
- release authority: `docs/260-release-authority-policy-and-key-management.md`
- consent substrate: `docs/256-consent-ux-contract.md`
- breakglass lane: `docs/250-breakglass-and-recovery-workflows.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

If the archive does not decide approval posture, real systems drift into one of two bad states:

- fleet/factory shared-trust mutations still rely on social process, requester self-approval, or undocumented ceremonies,
- workstation/general-purpose flows inherit enterprise-style quorum friction for actions that are really just trusted-UI user consent problems,
- “approval” becomes a vague prompt instead of a digest-bound receipt tied to a plan/policy/artifact,
- and offline/regulatory environments quietly depend on live reviewer infrastructure that does not exist when it matters.

DeriveBSD already says authority should be leased, receipted, and explainable.
That only becomes coherent if the archive fixes the **default authority model for high-risk approvals** instead of leaving quorum as folklore.

## Scope of this knob

`high_risk_approvals` is about **shared-trust or boundary-expanding mutations**,
not every click in the system.
Typical examples include:

- release publish / halt / resume authority,
- trust-root and key-rotation ceremonies,
- destructive breakglass, reset, or reprovision authority,
- exposure or export policy expansions with real blast radius,
- similar actions where requester-self-approval or “approve the idea” would be unsafe.

Ordinary human-risk actions on a workstation (for example consenting to a firmware apply, granting an app access via the trusted UI, or confirming a remembered browser/mail role-default change through `intent.role.binding` consent profiles) stay governed by the product-default lanes that already exist elsewhere in the archive.
A stronger `packet.capture.normalized` export is a useful edge case here: it stays on the generic consent lane, but the archive now insists that the approval evidence be explicit, non-auto, and destination-bound so the stronger export cannot disappear into background uploader folklore or get retargeted after approval (`docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`).

## Product-shape defaults

| Profile | `high_risk_approvals` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `digest-bound-role-separated-quorum` | Shared-trust mutations require digest-bound approvals from distinct principals by default; requester self-approval is not the fleet baseline. |
| B (`workstation`) | `trusted-ui-user-consent-first` | Personal-risk actions use trusted-UI user consent by default; org/shared-trust mutations, if enabled, move into an explicit admin lane instead of hijacking ordinary prompts. |
| C (`general_os`) | `single-principal-default-explicit-quorum-lane` | Ordinary local admin/install/update flows stay single-principal viable; quorum remains an explicit optional policy/adapter lane rather than a hidden dependency. |
| D (`appliance_factory`) | `offline-oob-role-separated-quorum` | Production/manufacturing shared-trust mutations require digest-bound, role-separated quorum with offline/OOB-capable approval paths by default. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- high-risk approvals bind to a **specific digest** (plan, policy, or artifact), not a vague intent
- requester self-approval is weaker than distinct-principal approval and should only survive where the product shape explicitly tolerates it
- separation of duties matters more than raw approval count; “decide” and “ship/execute” should not silently collapse into one principal when blast radius is large
- offline carriers and out-of-band review may transport approvals, but they do not replace local digest verification and receipts
- user-consent prompts and organizational quorum prompts are related but not interchangeable surfaces

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `digest-bound-role-separated-quorum`

- Fleet release, trust-root, breakglass, and similarly dangerous shared-trust mutations should not be approved by the requester alone.
- Distinct-principal approval is the normal posture because fleet hosts usually affect many machines at once.
- The system should bias toward auditable receipts and stable role separation rather than “someone in chat said ship it.”

### B) Secure workstation (`workstation`)

Default: `trusted-ui-user-consent-first`

- The ordinary workstation authority model is a real human at a trusted prompt.
- Workstation UX must not turn personal-risk actions into fake enterprise ceremony just because the archive has quorum primitives.
- If the workstation participates in a larger org-controlled release/trust/admin workflow, that lane must stay explicit and distinct from ordinary user prompts. Remembered role/default reconcile now follows that same rule: interactive changes stay on the constrained consent lane, while non-interactive reconcile/import changes should point at `policy.decision` instead of masquerading as a background user-consent story. The apply rule across both lanes is still compare-and-swap against the current binding digest, so stale remembered-role writes must emit `precondition-failed` denial evidence instead of auto-merge or silent rebase.

### C) General-purpose OS (`general_os`)

Default: `single-principal-default-explicit-quorum-lane`

- General-purpose viability requires that a competent local admin can still install, update, recover, and develop without a remote approval service.
- Stronger approval lanes are fine, but they must be consciously enabled.
- Compatibility remains real only if ordinary local control is not gated on reviewers who may not exist.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `offline-oob-role-separated-quorum`

- Production/manufacturing mutations should assume stronger review, distinct principals, and digest-bound receipts.
- Offline or out-of-band approvals must remain possible because air-gapped and regulated environments are part of the target product shape.
- The baseline should resist “same operator decides and ships” folklore for production-significant changes.

## What this does **not** decide yet

This doc does **not** freeze:

- exact threshold counts,
- exact approver groups/roles,
- exact offline approval token or envelope format,
- exact UI/TUI wording,
- or a full workflow engine.

Those remain implementation details or future RFC/ADR material.

## Why this is worth locking now

This decision collapses a recurring ambiguity without inventing a new subsystem:

- A gets real four-eyes posture where blast radius is shared and fleet-wide,
- B keeps trusted-UI user agency instead of inheriting admin ceremony theater,
- C keeps local-admin viability without closing the door on stronger team workflows,
- D gets a realistic offline/regulatory approval story instead of “we will handle that socially.”

That is enough to guide future specs and coding while leaving envelope details open.

## Design cue from current systems

A few ecosystem lessons are stable:

- threshold-signature systems keep proving that distinct keys/roles matter more than a single “blessed pipeline” actor
- deployment systems that expose reviewer gates and self-review prevention are useful, but they are not a substitute for digest-bound receipts or role separation
- multi-party authorization systems work best when the protected request, approvers, and TTL are explicit rather than hidden in social process
- offline/regulatory environments need approval ceremonies that survive disconnected operation

DeriveBSD should steal those lessons while keeping the approval transport replaceable.

Last updated: 2026-03-17r276
