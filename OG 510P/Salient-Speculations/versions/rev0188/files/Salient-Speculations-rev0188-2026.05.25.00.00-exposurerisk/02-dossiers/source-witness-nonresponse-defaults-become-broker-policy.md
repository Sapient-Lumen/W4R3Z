---
id: ss-0180-source-witness-nonresponse-defaults
revision_promoted: rev0180
title: Source-witness nonresponse defaults become broker policy
constellation:
- managed-legibility
- administrative-repair
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- diligence-packets
- cyber / software supply chain / vulnerability governance
- organizational identity / entity resolution
bottleneck_type:
- appealability / redress
- source-of-truth precedence
- interim reliance authority
- correction throughput
enforcement_surface:
- procurement / framework contract
- underwriting / insurance renewal
- court / tribunal / administrative appeal
artifact_type:
- appeal record
- state label
- notice
- reason code
lifecycle_stage:
- dispute
- stay
- investigate
- correct
- decide
failure_modes:
- nonresponse
- stale-state
- strategic-delay
- unverifiable-source
- procedural-debt
refactor_cluster:
- remedy-lifecycle
- provenance-lineage
remedy_role: source-witness nonresponse default
remedy_stage:
- evidence-request
- nonresponse
- decide
consolidation_status: standalone-mechanism
state_family:
- remedy
- provenance
lineage_role: source-issuer and auditor-regulator
lineage_stage:
- dispute
- archive
- correct
state_terms:
- provenance-disputed
- lineage-gap
---
# Source-witness nonresponse defaults become broker policy

## Core claim

Once normalized packets depend on source-object identity warranties, transformation-code escrow, split/merge correction notices, amendment-recipient registries, identity-match appeals, appeal-stay labels, and correction-materiality schedules, the next hard problem is not only whether the broker can adjudicate a dispute. It is what the broker does when the relevant **source witness does not answer**.

A source witness may be the native SaaS vendor, repository host, scanner, ticket-system administrator, cloud tenant owner, data-room custodian, identity issuer, registry operator, parcel authority, product-passport provider, map custodian, or source-system successor. Appeals may require that witness to say whether a native ID was reused, whether an export was complete, whether a record was deleted, whether a join key was stable, whether a status had already changed, whether a historical snapshot exists, or whether an asserted relation was source-declared rather than broker-inferred.

The speculative claim is: **source-witness nonresponse defaults become broker policy**. Packet systems will need machine-readable defaults for silence, late response, impossible verification, refusal, expired retention, wrong-forum response, partial response, conflicting response, and witness unavailability. Those defaults will decide whether a packet remains usable, becomes manual-review-only, is score-excluded, moves to non-reliance pending, triggers a holdback reserve, or is decided against the party that needed the witness.

The key shift is from nonresponse as administrative frustration to nonresponse as a governed evidentiary state.

## Why this belongs in the archive

The archive has reached the point where many dossiers depend on appeal and correction. But an appeal system is only real if it can handle the ordinary case where evidence is incomplete.

Credit-reporting law provides a mature analogy. The FCRA requires reinvestigation of disputed accuracy and creates consequences for information that cannot be verified within the statutory dispute process [S1469]. Regulation V requires furnishers to investigate covered direct disputes, review relevant information, report results, and provide notice for frivolous or irrelevant disputes [S1470]. That regime does not assume every source perfectly cooperates. It creates procedural states for verified, corrected, deleted, disputed, frivolous, and unresolved information.

GDPR restriction and rectification practice points in the same direction. Restriction of processing lets contested information remain stored while use is limited [S1467], and recipient-notification duties matter when corrected or restricted information has already traveled [S1468]. The packet analogue is direct: if the source witness does not answer, the system still has to decide whether prior recipients can keep relying, whether a stay applies, and whether the contested object must travel with a disputed or unverifiable label.

Security data supplies a live pressure signal. NIST announced in April 2026 that CVE submissions had increased 263% between 2020 and 2025 and that NVD enrichment would shift to a risk-based approach because the volume could no longer be handled by uniform enrichment [S1480]. In a world where public enrichment, vendor VEX, scanner status, and customer evidence increasingly conflict, “awaiting source confirmation” becomes a practical state, not an exception.

Operational-resilience regulation adds another pressure. DORA establishes EU-wide oversight of ICT risk and critical third-party providers for financial entities [S1483]. When supervised entities depend on third-party source systems, their ability to prove, correct, and explain source-state uncertainty becomes part of operational resilience rather than mere vendor management.

That is why this thesis belongs here. The archive's reliance-object lifecycle needs a rule for silence. If it does not have one, appeals become either theater or leverage: parties can block corrections by not answering, or force overbroad stays by demanding evidence no one can produce inside the transaction window.

## Speculative consequences worth tracking

### 1. Nonresponse becomes a named appeal outcome

Expect appeal outcomes such as verified, corrected, rejected, insufficient evidence, witness unavailable, source-retention expired, source refused, partial response, conflicting witness, cannot verify, stale source, wrong forum, and deemed admitted / deemed denied. These are not semantic niceties. They determine whether downstream reliance continues.

### 2. Silence affects the burden of proof

Contracts may say that if the source witness is controlled by the seller, seller silence counts differently than third-party vendor silence. If the buyer requested manual review but cannot provide its own source evidence, the appeal may become disclosure-only rather than stay-triggering. If a broker lost the replay bundle, silence may weigh against the broker rather than either party.

### 3. Stay labels will encode source-witness state

A pending appeal may be manual-review-only because the witness has not answered, score-excluded because the witness partially contradicted the join, or no-stay because the witness request was irrelevant or late. Appeal-stay labels will need subfields showing whether the interim state is merits-based, evidence-based, timing-based, or silence-based.

### 4. Source vendors become quiet adjudication infrastructure

Native-system providers may not want to be witnesses, but their API semantics, retention promises, audit exports, and support response times will determine whether downstream packet markets can resolve disputes. Vendor support tiers may begin to include “diligence dispute response” or “historical-state confirmation” clauses.

### 5. Retention windows become appeal windows

If a source system retains detailed history for only 30 or 90 days, the practical appeal right may expire earlier than the contractual appeal period. Mature packets will disclose source-retention horizons and indicate which fields are no longer independently verifiable.

### 6. Nonresponse metrics become broker scorecard inputs

Brokers may publish or privately maintain rates of source-witness nonresponse by source system, seller, vendor, data-room provider, or object class. High nonresponse rates may lower replay-quality grades, increase reserves, or force broader manual review.

### 7. Witness escalation becomes a service tier

For high-value transactions, brokers may offer paid escalation: pre-cleared vendor contacts, source-system administrator attestations, neutral custodian requests, and expedited native-log retrieval. Lower-tier packets may rely on default nonresponse rules.

### 8. Silence can be abused by every side

Sellers can slow-roll source access to delay adverse corrections. Buyers can send overbroad witness requests to create nonresponse and force holdbacks. Vendors can monetize historical confirmation. Brokers can hide weak custody behind “source unavailable.” Nonresponse defaults are therefore anti-abuse infrastructure, not just appeal procedure.

## Likely artifact shape

The mature artifact is a **source-witness response schedule** attached to the appeal and stay layer. It would include:

- **Witness identity** — source vendor, source owner, data-room custodian, registry operator, issuer, map authority, or successor system.
- **Control relation** — controlled by seller, buyer, broker, third party, regulator, public authority, or no longer extant.
- **Requested fact** — native ID stability, export completeness, deletion, rename, split, merge, historical status, relation type, timestamp, source precedence, or retention window.
- **Request timestamp and channel** — API ticket, signed notice, support case, registered endpoint, data-room message, regulator query, or neutral custodian request.
- **Response deadline** — ordinary, expedited, transaction-critical, stay-critical, or regulatory.
- **Response status** — no response, partial response, refusal, cannot verify, conflicting answer, source unavailable, stale retention, answered, or certified answer.
- **Effect on stay** — no-stay, disclosure-only, manual-review-only, score-excluded, holdback-reserved, eligibility-suspended, non-reliance-pending.
- **Burden rule** — which party bears silence under each control relation.
- **Abuse filter** — frivolous, duplicate, overbroad, late, impossible, wrong-forum, or leverage-only witness requests.
- **Final disposition** — witness confirmed, contradicted, could not verify, or remained silent past decision window.
- **Disclosure rule** — what recipients learn about silence without exposing privileged or commercially sensitive source details.

## Who pays / who saves / who captures

Buyers and lenders save by avoiding blind reliance on contested packet fields. Sellers save when a known nonresponse rule prevents every missing vendor answer from becoming a full holdback or eligibility freeze. Brokers capture value by operating the witness-request queue and by turning historical confirmation into a priced service tier. Source vendors may capture value by selling export retention, audit support, and historical-state confirmations.

The burden falls hardest on small suppliers and low-capacity source owners. If every appeal demands sophisticated source evidence, firms with messy systems or weak vendor contracts will be priced as unverifiable even when they are substantively low risk. This is why nonresponse defaults must distinguish bad faith, third-party unavailability, expired retention, and harmless uncertainty.

## How this gets abused

- A buyer files broad witness requests to trigger nonresponse and create settlement leverage.
- A seller controls the source administrator and delays evidence until a stay expires.
- A broker classifies its own missing custody record as source nonresponse.
- A vendor sells premium dispute support and leaves ordinary users with slow unverifiable states.
- A party uses expired retention as a cleansing strategy: wait until source logs disappear, then challenge the packet.
- Repeated unverifiable states become a quiet exclusion label for firms with weaker digital systems.

## Near misses

A help-desk ticket is not the thesis. The thesis begins when source-witness silence changes admissible reliance.

A general support SLA is not the thesis. The thesis is a default rule for what happens when the answer is missing at the moment a packet appeal, stay, correction, or non-reliance decision must be made.

A disclaimer that “source systems may be incomplete” is not the thesis. The thesis requires named outcome states and consequence rules.

## What could falsify or weaken the thesis

- Packet disputes are mostly resolved from broker-held snapshots without needing native source witnesses.
- Buyers accept broad disclaimers rather than paying for source-witness response machinery.
- Native platforms expose stable enough history APIs that nonresponse rarely matters.
- Appeal systems remain low-stakes correspondence rather than affecting eligibility, holdbacks, underwriting, procurement, or covenant treatment.
- Courts, regulators, and buyers reject silence-based defaults as too mechanical or unfair.
- Nonresponse rates are too low or too random to become scorecard inputs.

## Research queue

- Which source class first becomes a bottleneck witness: ticket systems, scanner vendors, SBOM issuers, cloud platforms, identity issuers, map registries, product-passport providers, or data-room custodians?
- Do contracts allocate silence by source control, reliance purpose, or object class?
- Which nonresponse outcome becomes most common: manual-review-only, disclosure-only, score-excluded, or non-reliance pending?
- Do vendors add “historical-state confirmation” APIs because diligence markets demand it?
- Do small suppliers need evidence brokers or cooperatives to handle source-witness requests at reasonable cost?
