---
id: ss-0180-recipient-graph-privacy-proofs
revision_promoted: rev0180
title: Recipient-graph privacy proofs become broker trust products
constellation:
- managed-legibility
- anti-legibility
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- diligence-packets
- identity / credentials / delegated authority
bottleneck_type:
- recipient-scope precision
- selective disclosure / minimization
- admissible evidence
enforcement_surface:
- procurement / framework contract
- audit / attestation / assurance
artifact_type:
- recipient graph
- privacy proof
- delivery attestation
lifecycle_stage:
- route
- rely
- dispute
- correct
failure_modes:
- overbroad-disclosure
- nonpropagation
- stale-state
refactor_cluster:
- authority-lifecycle
authority_role: verifier-relying-party and reviewer-auditor
authority_stage:
- present
- verify
- propagate
state_family:
- authority
state_terms:
- scope-limited
- verifier-unregistered
consolidation_status: state-family-member
---
# Recipient-graph privacy proofs become broker trust products

## Core claim

Amendment-recipient registries and appeal-stay labels solve one problem by creating another. If a broker must prove that every proper recipient of an amendment, correction, stay, or non-reliance notice received the right event, it must maintain a reliance graph. But that graph may reveal commercially sensitive relationships: potential buyers, lenders, insurers, reinsurers, auditors, counsel, platform accounts, regulators, acquisition targets, subcontractors, and downstream users.

The speculative claim is: **recipient-graph privacy proofs become broker trust products**. Mature packet systems will not simply expose full reliance graphs. They will provide role-masked, purpose-bound, auditor-visible, selectively disclosed, or escrowed proofs that the correct class of recipients was notified without revealing more than the verifier needs.

The important shift is from legibility as maximum disclosure to legibility as **sufficient proof under constrained disclosure**.

## Why this belongs in the archive

The archive's managed-legibility lane has become powerful enough that it now needs its own counterweight. Amendment-recipient registries say who must receive corrections. Appeal-stay labels say who must receive interim restrictions. Correction-materiality schedules say which classes of recipient deserve which consequence. Non-reliance states will say which prior users may no longer rely. All of that requires a graph.

But a reliance graph is not neutral. In M&A, procurement, insurance renewal, regulatory supervision, litigation, and platform eligibility, the fact that a party relied can reveal strategy. A seller may not need to know every buyer-side insurer. A buyer may not want to reveal its lender. A broker may need to prove delivery to a class without showing the identities to all other recipients.

Modern credential infrastructure gives a plausible technical pattern. W3C Verifiable Credentials 2.0 defines a data model for tamper-evident credentials across issuer-holder-verifier interactions [S1488]. The W3C BBS Data Integrity cryptosuite is explicitly designed to support selective disclosure and unlinkable proofs [S1489]. EU Digital Identity Wallet materials similarly emphasize selective disclosure of attributes and privacy dashboards as part of the wallet's security and privacy model [S1493]. These do not automatically solve recipient graphs, but they show that verifiers can be trained to accept less-than-full disclosure when the proof primitive is standardized and trusted.

Data-protection law supplies the policy pressure. Restriction and rectification duties already require thinking about downstream recipients [S1468], while privacy-risk management frameworks emphasize managing privacy risks rather than merely securing data after overcollection [S1490]. The broker problem is the same in institutional form: prove correct propagation without turning every update into relationship leakage.

That is why the thesis belongs here. The archive should not keep assuming that the solution to every governance problem is a more visible graph. In many domains, the winning intermediary will be the one that can prove the graph was used correctly while hiding the graph itself.

## Speculative consequences worth tracking

### 1. Recipient classes separate from recipient identities

Packets may expose that all required lenders, insurers, platform operators, regulators, or buyer-side delegates were notified without exposing the names. Some verifiers will see only classes; auditors or courts may see identities under seal.

### 2. Delivery proof becomes role-masked

A broker may produce a proof that “all recipients with covenant reliance rights as of version 4.2 received stay label X before deadline Y” without showing the seller which bank, syndicate member, or counsel endpoint was involved.

### 3. Recipient graphs get escrowed

Full recipient rosters may sit with neutral custodians. Ordinary parties receive proof hashes, class counts, or signed delivery attestations; identity-level disclosure occurs only under appeal, litigation, regulatory review, or agreed trigger.

### 4. Appeal standing becomes provable without full exposure

A party may need to prove it has standing to challenge a packet version because it relied on it. Privacy-preserving standing proofs could show valid reliance purpose, version, and time window without revealing the surrounding transaction.

### 5. Privacy proofs become broker differentiators

Brokers that can route corrections while protecting recipient confidentiality may win high-value diligence, insurance, and procurement markets. Weak brokers may choose either overdisclosure or underproof, both of which become liabilities.

### 6. Proof formats become procurement terms

A buyer may specify acceptable privacy-proof profiles: class-only delivery proof, auditor-readable roster, sealed-recipient escrow, zero-knowledge-style attribute proof, or regulator-readable full graph. Procurement will not just ask whether notices are sent; it will ask what can be revealed to whom.

### 7. Nonreceipt disputes become privacy disputes

If a recipient claims nonreceipt, resolving the dispute may require revealing an endpoint, delegation, forwarding path, or role. Privacy-preserving nonreceipt procedures will become as important as the original proof.

### 8. Excessive proof becomes its own failure mode

A broker can comply with notice duties and still create harm by revealing deal structure, insurer appetite, platform dependency, or regulatory interest. Overbroad graph disclosure becomes a litigable or contract-breaching event.

## Likely artifact shape

The mature artifact is a **recipient-graph privacy proof package**. It would include:

- **Reliance version and purpose** — the packet version and reliance category that triggered notice.
- **Recipient class policy** — which classes are entitled to identity-level notice, class-level proof, sealed proof, or no notice.
- **Masked recipient roster** — class counts, role labels, jurisdiction tags, and endpoint status without unnecessary names.
- **Delivery proof** — signed timestamp, channel class, receipt result, nonreceipt reason code, and proof hash.
- **Selective-disclosure credential** — a proof that a recipient belongs to an eligible class without revealing unrelated attributes.
- **Escrow pointer** — neutral custodian, access rule, retention period, and disclosure trigger for full graph review.
- **Standing proof** — a way for a recipient to prove reliance rights without revealing the whole transaction.
- **Forwarding proof** — evidence that a delegated recipient or downstream forwarder propagated the notice to authorized sub-recipients.
- **Privacy-loss log** — what identity or relationship information was revealed, to whom, and under which authority.
- **Challenge path** — how a party disputes nonreceipt, wrong class, overdisclosure, or improper withholding of graph evidence.

## Who pays / who saves / who captures

Buyers, insurers, lenders, and regulated platforms pay because they need notice rights without exposing their strategies. Sellers pay indirectly because privacy-preserving proof lowers the cost of participation in shared broker systems. Brokers capture value by becoming trusted graph custodians. Neutral custodians, auditors, and credential-service providers may become specialized infrastructure.

Small suppliers benefit if privacy proofs prevent large counterparties from demanding broad graph disclosure as a condition of trust. They are harmed if proof profiles become so technical that only large vendors can satisfy them.

## How this gets abused

- A broker hides an incomplete recipient graph behind opaque privacy language.
- A buyer claims privacy to prevent a seller from testing whether notice was actually sent.
- A seller demands full graph disclosure to identify sensitive counterparties.
- A recipient uses standing proofs repeatedly in ways that become linkable.
- An auditor or neutral custodian becomes the de facto relationship-data monopoly.
- Class labels are manipulated so important recipients are counted in a lower-notice category.

## Near misses

An NDA is not the thesis. The thesis requires a reusable proof that a graph was used correctly without exposing the graph.

A redacted spreadsheet is not the thesis. The thesis is role-aware, purpose-bound, and verifiable, not merely blacked-out.

A privacy policy is not the thesis. The thesis becomes real when a counterparty, regulator, court, or procurement system accepts the privacy proof as sufficient evidence of routing, delivery, or standing.

## What could falsify or weaken the thesis

- Transaction markets accept full recipient disclosure as a normal cost of packet governance.
- Recipient graphs remain internal broker logs and rarely become contested evidence.
- Selective-disclosure tooling stays too complex, expensive, or legally unfamiliar for ordinary diligence workflows.
- Courts and counterparties refuse privacy-preserving proofs and demand full rosters whenever disputes arise.
- Recipient graphs do not reveal enough strategic information to justify specialized privacy products.
- Brokers solve the problem with coarse contractual confidentiality rather than technical or procedural proof packages.

## Research queue

- Which recipient classes first require masking: insurers, lenders, regulators, counsel, platform operators, or downstream buyers?
- Do brokers develop neutral escrow models before or after a major overdisclosure dispute?
- Which proof format becomes acceptable: class attestations, sealed rosters, selective-disclosure credentials, or audited delivery reports?
- Can standing be proven without revealing transaction identity?
- Do privacy proofs reduce small-supplier burden or become another compliance moat?
