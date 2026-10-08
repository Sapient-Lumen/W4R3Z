# 013 — Authority credentials and the end of emailed delegation

**Status:** canon

## Thesis

As machine-verifiable organisational identity and mandate systems spread, more institutions will stop accepting portal accounts, signature blocks, scanned letters, and ad hoc callbacks as sufficient proof that a person is entitled to act for a firm.
The operative primitive shifts from “this looks like the company’s representative” to “prove who can bind whom.”

## Why it matters

A large share of economic life depends on acting *for* an organisation rather than merely acting as oneself.
Today that layer is often surprisingly loose: shared inboxes, manually managed user lists, PDF authorisations, board-resolution uploads, and custom role checks inside every portal.
That looseness creates fraud risk, delay, duplication, and automation bottlenecks.

If organisational existence, official role, and delegated mandate become machine-readable and legally legible, then procurement, tax filing, banking, customs, compliance, and regulated messaging all change.
The question is no longer just whether a document is authentic.
It is whether the actor is demonstrably authorised to commit the organisation.

## Mechanism sketch

- The revised eIDAS framework already treats natural and legal persons, and natural persons representing legal persons, as first-class subjects of identification and authentication. It explicitly includes electronic attestations for powers and mandates to represent natural or legal persons, and treats those attestations as legally effective trust-service outputs.
- The same framework requires Member States to provide European Digital Identity Wallets for natural and legal persons, making business-facing wallet infrastructure part of the baseline rather than a niche overlay.
- The Once-Only Technical System’s representation work shows that cross-border administrative procedures already need evidence about legal persons and their representatives; representation is being engineered as a repeatable technical problem, not left as a one-off paperwork ritual.
- The Commission’s 2025 European Business Wallet proposal pushes this logic further. It frames business identity and compliance as a wallet problem, gives the wallet core functions for identifying, authenticating, signing or sealing, submitting documents, and sending or receiving notifications, and explicitly calls for technical mandates and administrative mandates for authorised representatives.
- GLEIF’s verifiable LEI work supplies a parallel global path outside any one regional wallet regime. The vLEI is designed to provide automated identity verification of legal entities and of people acting on their behalf.
- ISO 5009’s official organisational role codes give that ecosystem a standardised way to express roles, helping turn “is this person really entitled to sign for the company?” from bespoke judgement into reusable machine-readable data.
- The FSB continues to push broader LEI adoption in cross-border payments because standardised entity identification improves payment data quality, KYC, and sanctions screening. That means organisational identity is not only a registry issue; it is becoming transactional infrastructure.

The deeper pattern is that many institutions increasingly need proof of **agency**, not just proof of personhood.
Once remote workflows, cross-border systems, and agentic software make loose delegation look fragile, organisational authority itself becomes a rising control surface.

This is different from authoritative-source evidence exchange. Even in a once-only system, someone or something still has to prove it is entitled to act for the organisation requesting, receiving, or binding.

## What this speculation predicts

1. More high-value workflows will require machine-verifiable proof that a human or software agent is authorised to act for a legal entity, rather than relying on uploaded authority letters or manually curated portal roles.
2. Organisational wallets, role credentials, e-seals, and mandate registries will increasingly converge with payments, procurement, filing, and compliance systems, turning representation into reusable infrastructure.
3. Fraud controls will move from checking whether a document was signed to checking whether the signer or submitting system had the right role, mandate scope, and current organisational status at the moment of action.
4. Political and legal conflict will concentrate on revocation, insolvency, stale mandates, internal delegation chains, and what happens when machine-readable authority collides with local company law or emergency exceptions.

## Watchpoints

- wallet or credential systems explicitly carrying organisational roles, mandates, powers of attorney, or representation rights
- payment, procurement, customs, or filing systems requiring machine-verifiable legal-entity identifiers or role credentials
- growth of role-code lists, mandate schemas, or interoperable authorisation registries that make organisational authority queryable across systems
- disputes or guidance focused on revoking delegated authority, proving who could bind a firm at a specific time, or handling expired/stale authority data
- evidence that businesses and regulators still prefer bespoke portal permissions, wet-signature uploads, or callback verification because shared authority infrastructure remains too fragmented

## What would weaken this

- organisational-role credentials remaining mostly demonstrational while real workflows continue to depend on bespoke portal access and uploaded paperwork
- company-law diversity, liability fears, or internal-governance complexity preventing shared mandate infrastructure from being trusted across borders
- firms concluding that manual review and closed vendor silos are safer than interoperable authority proofs for high-stakes transactions

## Source anchors

- [SRC-054](../00-meta/bibliography.md#src-054)
- [SRC-055](../00-meta/bibliography.md#src-055)
- [SRC-056](../00-meta/bibliography.md#src-056)
- [SRC-057](../00-meta/bibliography.md#src-057)
- [SRC-058](../00-meta/bibliography.md#src-058)
- [SRC-059](../00-meta/bibliography.md#src-059)
- [SRC-060](../00-meta/bibliography.md#src-060)
