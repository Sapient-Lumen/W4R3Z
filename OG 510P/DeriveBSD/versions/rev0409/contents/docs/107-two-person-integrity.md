# Two-person integrity (separate approvals)

Goal: reduce the chance that a single compromised key/operator can ship bad artifacts or enable catastrophic authority.

## Concept

Require **separate approvals/signatures** for:
- **plan/policy approval** ("is this allowed and correctly constrained?")
- **artifact publication/execution** ("this exact digest is what we will ship/run")
- optional **witness rebuild** attestations ("I rebuilt and got the same outputs")

This is the smallest useful form of the “four-eyes principle”: no single actor can both *decide* and *ship*.

The product-default boundary is now explicit too: fleet and factory shapes default to digest-bound distinct-principal approvals for shared-trust mutations, while workstation and general-purpose shapes keep user-consent or single-principal local control viable unless a stronger lane is explicitly chosen (see `docs/474-high-risk-approval-posture-by-profile.md`).

## How DeriveBSD represents approvals

DeriveBSD uses the consent objects as generic approval artifacts:
- `consent.request` describes the action, binds to policy/plan/artifact digests, and declares quorum
- `consent.receipt` records who approved (and how), as evidence

See: `docs/256-consent-ux-contract.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`,
`spec/consent.request.schema.json`, `spec/consent.receipt.schema.json`.

## Where it plugs in

- publishing releases and emergency halts: `docs/260-release-authority-policy-and-key-management.md`
- breakglass entry: `docs/236-breakglass-and-recovery-mode.md`
- network exposure grants (egress/listen brokers): `docs/281-network-egress-broker-and-consent.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`

Non-goals (v0): implementing a full enterprise workflow engine.

See RFC-0076.
Last updated: 2026-03-06r203
