---
id: ss-0176-amendment-recipient-registries
revision_promoted: rev0176
title: Amendment-recipient registries become reliance-graph infrastructure
constellation:
- managed-legibility
status: dossier
maturity: S2-artifact-emerging
confidence: medium-high
time_horizon: near
domain:
- diligence-packets
bottleneck_type:
- recipient-scope precision
- correction-propagation
- state freshness
enforcement_surface:
- procurement / framework contract
- underwriting / insurance renewal
artifact_type:
- recipient graph
- notice
- delivery attestation
lifecycle_stage:
- route
- rely
- correct
failure_modes:
- nonpropagation
- overbroad-disclosure
refactor_cluster:
- provenance-lineage
lineage_role: recipient and registry-steward
lineage_stage:
- transfer
- correct
- archive
state_family:
- provenance
state_terms:
- archive-evidentiary
- provenance-disputed
consolidation_status: state-family-member
---
# Amendment-recipient registries become reliance-graph infrastructure

## Core claim

Once split/merge corrections, duplicate reversals, source remaps, rejected identifiers, superseded packet versions, corrected scores, and historical-view amendments become formal packet events, the hard problem is not only whether the amendment notice exists. The hard problem is **who is entitled to receive it**.

A diligence broker can know that a prior packet changed meaning and still fail the market if it cannot identify which buyer, seller, insurer, lender, auditor, procurement platform, delegated agent, downstream subscriber, escrow custodian, or expired-but-still-entitled party relied on the affected packet version for the affected purpose. A static distribution list is too weak. It does not know whether a party merely viewed a packet, received it as an agent, acquired reliance rights, subscribed to amendment events, transferred rights after closing, lost authority, changed delegate, opted into electronic notice, or only had a right to notice for covenant-impacting corrections.

That is the speculative claim: **amendment-recipient registries become reliance-graph infrastructure**. The next market layer is a durable, queryable registry that binds packet versions, reliance purposes, parties, roles, delegates, endpoints, subscription channels, entitlement periods, notice classes, delivery proofs, and downstream-forwarding obligations into one governed graph. Packet correction stops being a single notice event and becomes a continuing registry obligation.

## Why this belongs in the archive

The archive’s lifecycle-governance lane has moved from state-transition notices through delivery attestations, delegate-freshness proofs, propagation-lag budgets, convergence gates, gate-expiry disputes, waivers, post-waiver certificates, residue inventories, extension-lineage disclosures, renewal-history normalization, normalization-loss warranties, non-comparable-state carve-outs, source-object identity warranties, transform escrow, and split/merge amendment notices. The previous dossier created the amendment event. This dossier adds the missing routing substrate: a correction cannot be legally or economically meaningful unless the broker knows who has an amendment right.

Existing technical standards already show pieces of this substrate. FHIR’s Subscription resource is explicitly a request for proactive event notifications from one system to another, tied to a predefined topic and refined through filters [S1427]. FHIR’s Subscriptions framework separates the topic, the subscription request, the channel, the endpoint, and the notification payload [S1428]. That is a clean analogy for packet amendments: a party should not merely be “on the list.” It should have a registered event topic, a filter scope, a channel, a payload class, and an endpoint.

WebSub makes the registry shape even sharper. It defines a subscription as the unique relation between a Topic URL and a Subscriber Callback URL, allows subscriptions to have lease-like expiration times, and requires renewal when needed [S1429]. A diligence-packet registry will have a similar problem: an entitlement may be tied to a packet topic, a recipient endpoint, a reliance class, and a renewal or expiry rule. If the lease silently lapses, a later nonreceipt dispute becomes partly a registry-maintenance dispute.

OpenID’s Shared Signals Framework shows how formal event streams become managed objects. A receiver creates an event stream, the transmitter returns a stream configuration, and the configuration can include stream IDs, audiences, delivery methods, endpoints, requested events, delivered events, descriptions, and inactivity timeouts [S1430]. That pattern points beyond ordinary mailing lists. Amendment recipients may need stream-level configuration: which amendment classes are in scope, whether the receiver uses push or poll, who the audience is, whether subject scoping is `ALL` or explicit, and what happens when the recipient goes inactive.

Security-event standards add evidentiary discipline. RFC 8417 defines a Security Event Token as a signed or encryptable JSON Web Token containing statements of fact by an issuer about a subject, often delivered asynchronously after the triggering state change [S1431]. RFC 8935 defines push delivery to an intended recipient endpoint with success or failure indicated by the HTTP response [S1432]. RFC 8936 defines poll-based delivery where a recipient can retrieve events and acknowledge received tokens, with delivery assurance depending on recipient needs [S1433]. Those mechanisms matter because packet amendments will also need issuer, subject, intended recipient, delivery mode, acknowledgement, and proof-of-receipt semantics.

CloudEvents’ subscription specification generalizes the role of a subscription manager: an intermediary may determine who receives copies of events from producers, and configured subscriptions can be pull-style or push-style [S1434]. That is close to the broker role here. The broker is not only producing corrected packets; it is deciding who receives a copy of the amendment event and under which channel, filter, and entitlement. If that decision is wrong, the broker’s registry becomes a liability surface.

Permission models show why the registry must be purpose-bound, not merely address-bound. FHIR Consent records who grants rights, who must comply, who manages or enforces consent, what policy basis governs the consent, which actors are controlled, which actions and purposes are covered, and what effective periods apply [S1435]. XACML likewise frames access-control decisions around attributes of subjects, resources, actions, and environment [S1436]. A packet-amendment registry needs analogous dimensions: subject is the recipient or delegate, resource is the packet version or amendment class, action is receive/view/forward/challenge/rely, purpose is procurement, insurance, lending, acquisition, audit, or regulatory use, and environment includes time window, transaction class, and channel.

Legal notice practice supplies the final clue. The Federal Rules of Civil Procedure distinguish who must be served, when service goes to an attorney rather than a party, how electronic service is made, and when service is ineffective after the sender learns it did not reach the recipient [S1437]. The E-SIGN Act preserves underlying rights and obligations, does not force people to accept electronic records, and imposes consent conditions when required information is provided electronically [S1438]. The point is not that packet amendments are court pleadings or consumer disclosures. The point is that serious notice systems track recipient capacity, consent, channel, address, failure knowledge, and underlying rights. A brokered packet ecosystem will rediscover the same grammar.

OSCAL’s assessment-results reference also keeps role-to-party relationships explicit: responsible-party and responsible-role structures create arcs between role identifiers and party UUIDs, with scope determined by the containing object [S1439]. That is the governance model a packet broker will need: not merely a table of emails, but a role-and-party graph that can answer who was entitled to which amendment under which role when the packet was used.

That is why this thesis belongs here. The archive already has correction notices. It now needs the infrastructure that turns those notices into routed, bounded, reviewable, and litigable amendment obligations.

## Speculative consequences worth tracking

### 1. Reliance rights become registry entries

A packet recipient will not merely download an exhibit. It may acquire a named reliance right: buyer diligence reliance, insurer underwriting reliance, lender covenant reliance, auditor review reliance, procurement eligibility reliance, regulator-supervision reliance, seller-defense reliance, or escrow-replay reliance. Each right implies different amendment entitlements.

### 2. Viewer, recipient, subscriber, and relying party split apart

Many people may see a packet. Fewer may receive it through an authorized channel. Fewer still may be allowed to rely on it. Some may only subscribe to correction notices without having economic reliance rights. The registry will need to distinguish these statuses because the notice duty may attach to one and not another.

### 3. Packet versions acquire recipient histories

The same entity may rely on version 4 for closing, version 5 for insurance renewal, and version 6 for covenant monitoring. If version 4 is later amended, the broker cannot simply notify everyone with current access. It must know who had rights in the old version and whether those rights survive after newer packets issue.

### 4. Notice class becomes purpose-bound

A non-material display correction may go to portal subscribers only. A score restatement may go to buyers and insurers. A holdback-impacting correction may go to buyer, seller, escrow agent, and counsel. A procurement-eligibility correction may go to the procurement platform and prime contractor. Notice rights become classed by reliance purpose.

### 5. Delegates become governed notice endpoints

Counsel, brokers, agents, auditors, procurement platforms, insurance intermediaries, managed-security providers, and data rooms may receive notice on someone else’s behalf. The registry must know whether the delegate is still authorized, which notice classes it can receive, and whether notice to the delegate counts as notice to the principal.

### 6. Expired recipients retain residual amendment rights

A buyer may lose portal access after closing but retain a right to amendments affecting that closing. An insurer may stop underwriting the account but retain claim-related amendment rights. A procurement platform may no longer list the supplier but need historical correction records. Expiry of access and expiry of amendment entitlement will diverge.

### 7. Downstream platforms become co-distributors

If a packet flows into a procurement portal, underwriting system, lender dashboard, or auditor workpaper platform, the original broker may notify the platform while the platform must notify its own users. That creates a second-order reliance graph. The broker may not know every downstream user, but contracts may require the platform to maintain sub-recipient registers.

### 8. Delivery proof becomes a graph query

A future dispute will ask not only “was a notice sent?” but: to which legal entity, role, delegated endpoint, channel, subject scope, packet version, notice class, and reliance purpose; when was it delivered, acknowledged, rejected, suppressed, retried, expired, or learned to have failed? Delivery attestation becomes queryable graph evidence.

### 9. Recipient privacy becomes a design constraint

A full registry reveals sensitive transaction structure: who is buying whom, which insurer is underwriting, which lender is nervous, which regulator is watching, which auditor requested a packet, and which downstream platforms are involved. Brokers will need privacy-preserving recipient records, escrowed recipient lists, or role-masked proofs.

### 10. Notification fatigue creates batching and severity rules

If every minor correction is pushed to every historical recipient, amendment notice becomes spam. The registry will need event severity, digest preferences, urgency flags, materiality thresholds, and override rules when a supposedly low-severity correction touches a high-stakes reliance purpose.

### 11. Recipient maintenance becomes a service metric

A broker may be judged on percentage of amendment recipients with verified endpoints, current delegates, fresh consent, non-expired subscriptions, tested channels, and usable escalation paths. The archive already has delegate freshness and escalation-path liveness. Amendment-recipient registries turn them into broker scorecard inputs.

### 12. Reliance transfer becomes a closing issue

If a loan is assigned, an insured risk is reinsured, a buyer sells the asset, or a prime contractor transfers obligations to a subcontracting platform, do amendment rights transfer? The registry may need successor-recipient rules just as packet subjects need successor IDs.

### 13. Incorrect non-notice becomes its own fault class

A broker may produce the right correction and deliver it to the wrong class of recipients. That is not the same fault as producing a bad packet or failing to correct one. Expect fault classes for missed reliance recipient, overbroad disclosure, stale delegate, invalid channel, expired subscription, unregistered downstream user, and non-transfer of amendment rights.

## Likely artifact shape

A mature artifact probably looks like an **amendment-recipient registry** bound to the packet family, correction ledger, delivery-attestation layer, and transform-escrow bundle. It would not be a simple contact list. A minimum useful registry would include:

- **Registry ID** — stable identifier for the recipient graph and its governing version.
- **Packet family and version scope** — packet IDs, versions, exhibits, scorecards, residue inventories, warranty schedules, amendment ledgers, and historical views covered by the registry.
- **Recipient legal identity** — organization, person, platform, trustee, escrow agent, auditor, counsel, insurer, lender, agency, prime contractor, seller, buyer, or delegated service provider.
- **Recipient capacity** — viewer, authorized recipient, relying party, subscriber, agent, delegate, custodian, downstream distributor, archive holder, challenge-right holder, or historical claimant.
- **Reliance grant** — whether reliance is expressly granted, implied by transaction documents, limited to a reliance letter, inherited by assignment, delegated through agency, or excluded.
- **Reliance purpose** — acquisition diligence, procurement eligibility, cyber insurance, lending, surety, regulatory submission, internal audit, remediation holdback, covenant monitoring, seller defense, or supervisory review.
- **Notice classes** — emergency correction, score restatement, holdback-impacting amendment, eligibility-impacting amendment, warranty-boundary change, source-object correction, semantic-loss correction, non-comparable-state reclassification, disclosure-only update, digest-only update, or correction withdrawal.
- **Subject and event filters** — affected subsidiaries, assets, products, controls, vulnerabilities, parcels, obligations, dependencies, canonical subjects, amendment types, severity bands, and materiality thresholds.
- **Channel and endpoint** — portal, API, webhook, email, registered agent, counsel-of-record, escrow custodian, procurement platform, underwriting system, secure mailbox, poll endpoint, or push endpoint.
- **Channel authority evidence** — consent record, reliance letter, data-room invitation, subscription creation, stream configuration, court-like service designation, contract clause, board authority, agent appointment, or system registration.
- **Delegate-of-record data** — current delegate, delegate role, authority period, revocation date, backup delegate, escalation path, and whether notice to delegate binds the principal.
- **Subscription state** — requested, active, paused, disabled, expired, revoked, pending handshake, pending verification, digest-only, poll-only, push-enabled, or historical-entitlement-only.
- **Effective period** — when the recipient acquired rights, when they expire, what residual post-expiry amendment rights remain, and which event classes survive termination.
- **Delivery assurance level** — best-effort alert, signed event token, authenticated webhook, portal posting plus alert, acknowledgement required, manual receipt required, counsel service, or escrow delivery.
- **Acknowledgement and failure log** — sent, delivered, opened, acknowledged, rejected, bounced, suppressed, endpoint dead, unauthorized, failed signature, retry pending, alternative channel used, or sender learned of failure.
- **Downstream distribution duty** — whether the recipient may forward, must forward, must maintain a sub-recipient registry, must certify forwarding, or must not disclose recipient-specific details.
- **Privacy and masking rule** — whether identities are visible to all packet parties, visible only to broker, escrowed, role-masked, aggregated, disclosed on dispute trigger, or withheld under confidentiality restrictions.
- **Transfer and successor rule** — whether amendment rights transfer with asset sale, loan assignment, insurance novation, reinsurance, contractor substitution, platform migration, or successor counsel appointment.
- **Challenge right** — whether the recipient may challenge recipient-scope exclusion, nonreceipt, materiality classification, correction content, delivery sufficiency, or supersession effect.
- **Audit export** — machine-readable registry snapshot, recipient-scope proof, delivery-proof bundle, stale-recipient report, non-notice explanation, and historical graph view as of a transaction date.

This artifact matters because it turns amendment notice from ad hoc outreach into governed infrastructure. It lets sellers know retroactive notice will not leak to every historical viewer. It lets buyers know high-stakes corrections will not vanish into a stale portal. It lets insurers and lenders register purpose-bound amendment rights without receiving irrelevant noise. It lets brokers prove that they notified the legally relevant recipient class without exposing every deal participant. And it lets later reviewers distinguish a packet-production failure from a recipient-graph failure.

## New bottlenecks exposed

### Recipient-scope adjudication

Someone will have to decide whether a party was a true reliance recipient, a mere viewer, a downstream beneficiary, a delegated agent, a terminated subscriber, or an excluded recipient. That classification may decide whether late notice reopens money.

### Stale-recipient repair

The registry will degrade: counsel changes, auditors rotate, insurers exit, procurement platforms migrate, data rooms close, endpoints fail, and counterparties merge. Brokers may need periodic recipient recertification, stale-recipient reason codes, and cure windows.

### Confidentiality-preserving notice proof

A seller may demand proof that required parties were notified while also resisting disclosure of every buyer-side insurer, lender, auditor, or platform user. Neutral proofs, escrowed recipient lists, and role-level attestations may become standard.

### Over-notice liability

Under-notice creates nonreceipt disputes. Over-notice creates confidentiality, privacy, market-signal, and trade-secret problems. The registry must be precise enough to avoid both.

### Successor-recipient mapping

If packet subjects need successor maps, so do packet recipients. After acquisition, assignment, merger, mandate termination, or platform replacement, old amendment rights may need to follow a successor recipient or remain with the original recipient for historical claims.

### Multi-broker synchronization

If several brokers normalize overlapping source universes, one broker’s amendment-recipient registry may not know that another broker’s recipient relied indirectly on the same corrected subject. Cross-broker notice propagation may become a hard problem.

## What could falsify or weaken the thesis

- Packet contracts disclaim all post-issuance amendment obligations, so correction notices remain courtesy updates rather than reliance events.
- Market participants accept a single public or private portal as constructive notice, eliminating the need for fine-grained recipient graphs.
- Buyers, insurers, lenders, and procurement platforms refuse to disclose reliance roles to brokers, making durable registries too sensitive to maintain.
- Privacy, confidentiality, or competition-law concerns prevent brokers from retaining or proving detailed recipient relationships.
- Native source systems become strong enough at subscriber routing that broker-level amendment-recipient infrastructure remains unnecessary.
- Courts, regulators, or market practice treat packet amendments as current-state corrections with prospective effect only, reducing the value of historical recipient notice.
- Insurance or indemnity mechanisms absorb correction risk more cheaply than maintaining precise recipient registries.
- Downstream systems ignore amendments unless they arrive through their own native workflow, making broker registries secondary.

## Research queue

- Which recipient class demands formal amendment rights first: insurers, lenders, buyers, government procurement platforms, auditors, sellers, regulators, or escrow agents?
- Do reliance grants become explicit registry objects, or do they remain buried in transaction agreements and data-room access logs?
- What counts as notice to a platform user when the broker only notified the platform?
- Does amendment entitlement survive portal-access termination, insurance expiry, loan assignment, asset sale, or counsel substitution?
- Which notice class creates the first major dispute: score restatement, holdback impact, eligibility change, warranty-boundary change, or source-object correction?
- How much recipient identity can be hidden while still proving that the right class of recipients received notice?
- Do brokers compete on recipient-graph freshness, stale-endpoint cure rates, acknowledgement rates, or successful downstream-forwarding proofs?
- Do packet recipients prefer push alerts, pull queues, portal digests, signed event tokens, counsel service, or API polling?
- When a correction is withdrawn or reversed, must every recipient of the original correction receive the reversal, or only parties whose reliance purpose was affected?
- Does recipient-graph failure become a separate liability cap from packet-production failure, semantic-loss warranty breach, source-object identity error, or transform-custody failure?
