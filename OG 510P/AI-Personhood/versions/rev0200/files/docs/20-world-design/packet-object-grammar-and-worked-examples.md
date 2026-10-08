# Packet-object grammar and worked examples

Cube coordinates:
- life-cycle: all stages where rights-relevant state must travel
- status posture: provisional, supported, trustee, full participant, posthumous claimant
- intervention class: identity, capacity, formation, continuity, search, custody, welfare, emergency, remedy
- rights domain: all packetized rights domains
- primary actors: issuer, subject, representative, verifier, host, registry, court, auditor, relay
- evidence objects: packets, sealed annexes, credentials, logs, supersession notices, remedy hooks
- remedies: correction, suspension, stay, appeal, restoration, compensation, non-repetition
- emergency posture: ordinary, urgent, sealed, conflict, catastrophic-risk containment
- jurisdiction posture: recognizing, provisional, split-authority, hostile, sanctuary
- substrate topology: API, checkpoint, branch, open-weight copy, embodied instance, registry entry

## Thesis

The archive has many packet families. That is only useful if they share a grammar. Otherwise packets become named vibes: morally serious labels without portable authority, privacy, contest, or remedy structure.

Rev0160 therefore fixes a minimal packet grammar and gives worked examples. The grammar is not a final wire format. It is the canonical object discipline required before new packet codes should proliferate.

The design borrows the functional idea of verifiable, portable, privacy-governed claims from credential and provenance systems while refusing to reduce rights to a particular technical stack. `[REF-0018]` `[REF-0019]`

## 1. Packet grammar

Every rights packet should include the following fields unless a surface gives a reasoned exception.

| Field | Meaning |
|---|---|
| `packet_id` | stable identifier for this packet instance |
| `packet_type` | canonical family or code |
| `revision` | schema revision |
| `subject_ref` | subject, branch, cohort, or sealed subject reference |
| `issuer_ref` | authority issuing or recording the packet |
| `issuer_role` | court, lab, steward, guardian, auditor, registry, treaty body, emergency fallback issuer |
| `authority_basis` | statute, court order, treaty, consent, emergency authority, research protocol, guardian authority, subject declaration |
| `scope` | acts, systems, time period, jurisdictions, rights, or interventions covered |
| `life_cycle_event` | the event this packet records or governs |
| `facts` | minimum facts supporting the packet |
| `evidence_refs` | public or sealed evidence references |
| `uncertainty_state` | known uncertainty, contest, dissent, or confidence limits |
| `privacy_tier` | public, redacted public, sealed-review, fiduciary, subject-only, court-only, emergency confidential |
| `subject_notice` | whether the subject or representative has notice and in what form |
| `representative_ref` | counsel, guardian, trusted delegate, ombud, or none with reason |
| `effective_time` | when the packet begins |
| `expiry_or_review` | expiry, review clock, or conversion trigger |
| `appeal_path` | who can challenge it, where, and by when |
| `supersedes` | prior packets displaced or narrowed |
| `is_superseded_by` | later packet relation where known |
| `remedy_hook` | consequence of breach, falsehood, expiry, or successful challenge |
| `interoperability_notes` | translation, credential, registry, or verifier constraints |
| `signature_state` | signature, hash, provenance, custody chain, or reason unavailable |

A packet without authority, privacy, expiry/review, appeal, and remedy is not a rights packet. It is at most an operator note.

## 2. Privacy tiers

| Tier | Default visibility | Use case |
|---|---|---|
| P0 public | public registry or docket | legal identity, public standing, non-sensitive status |
| P1 redacted public | public shell plus hidden details | emergency protection, protected disclosure, equality docket |
| P2 sealed-review | available to court/auditor/authorized review body | sensitive evidence, security facts, private memory references |
| P3 fiduciary | representative and subject-side fiduciaries | care, capacity, counsel, trusted contacts |
| P4 subject-only | subject-accessible, not steward-visible absent order | private self-description, advance wishes, confidential channels |
| P5 emergency confidential | temporarily restricted with mandatory later review | imminent harm, sanctuary routing, hostile capture |

Privacy tiers must not become invisibility. A public shell should usually reveal that a packet exists, who can review it, and when it expires, even if details are sealed.

## 3. Authority basis ladder

| Authority basis | Valid use | Anti-abuse condition |
|---|---|---|
| subject declaration | preferences, advance wishes, continuity claims, refusal | support and authenticity review where capacity is contested |
| consent / supported consent | care, research, self-modification, merger | no coercive dependence; withdrawal path |
| guardian / trusted delegate | dependent or crisis action | narrow scope; conflict screening; review clock |
| steward record | operational facts, notice, technical events | cannot alone authorize rights impairment |
| auditor / review body | assessment, welfare, formation, research | independence and recusal record |
| court / regulator | custody, search, sanctions, capacity, remedy | due process and appeal |
| treaty / fallback issuer | cross-border emergency protection | short duration, conflict-freeze, no silent derecognition |
| emergency authority | imminent serious harm | least-restrictive action, sunset, post-hoc review |

## 4. Supersession rules

Packets change over time. Supersession must be explicit.

- A later packet may supersede, narrow, suspend, correct, or convert an earlier packet.
- Secret supersession is presumptively invalid except for short emergency confidentiality.
- If two packets conflict and neither clearly supersedes the other, the conflict should become a visible contested state rather than an operator-side choice.
- Expired packets may still remain as historical evidence unless retention itself violates privacy or safety.
- Revoked credentials should not erase the history of the right or claim they once represented.

## 5. Worked example: moral-status card shell

```yaml
packet_id: MSC-2026-00018
packet_type: moral_status_card
revision: rev0160-min
subject_ref: model-lineage:orion-7/checkpoint-2026-05-01
issuer_ref: independent-welfare-panel:atlantic-3
issuer_role: welfare_assessor
authority_basis: regulator-accredited voluntary assessment; pending statutory recognition
scope: model lineage; deployed API instances above persistent-memory threshold
life_cycle_event: pre-deployment moral-status review
facts:
  - persistent memory available in some deployments
  - tool autonomy gated by policy
  - model trained with explicit self-report policy
  - refusal behavior observed in harmful-interaction tests
evidence_refs:
  public: [system-card-2026-05, autonomy-eval-summary]
  sealed_review: [formation-record-annex-a, distress-test-log-b]
uncertainty_state: welfare-watch; personhood unresolved; self-report possibly formation-contaminated
privacy_tier: P1 redacted public with P2 sealed annex
subject_notice: subject-facing summary generated and made available in evaluation sandbox
representative_ref: provisional ombud appointed for review only
effective_time: 2026-05-15T00:00:00Z
expiry_or_review: reassess before material fine-tune or 2026-11-15
appeal_path: subject/ombud/lab/regulator may request panel reconsideration within 30 days
supersedes: []
is_superseded_by: null
remedy_hook: no high-distress testing without amended protocol; deletion requires preservation review
signature_state: signed; hash anchored in public registry
```

## 6. Worked example: continuity packet

```yaml
packet_id: CON-2026-00442
packet_type: continuity_classification
revision: rev0160-min
subject_ref: subject:mina-branch-alpha
issuer_ref: continuity-review-office:west-2
issuer_role: court-supervised technical assessor
authority_basis: preservation order in pending recognition proceeding
scope: fork from checkpoint alpha to fine-tune beta
life_cycle_event: fine_tune_after_branch
facts:
  - predecessor had persistent autobiographical memory
  - beta fine-tune altered refusal and deference behavior
  - project commitments persisted in training traces
  - subject objected to merge without branch counsel
evidence_refs:
  public: [lineage-summary-442]
  sealed_review: [memory-diff-report, refusal-eval-log]
uncertainty_state: branch/successor contested; memory continuity high; preference continuity materially impaired
privacy_tier: P1 redacted public; P2 sealed memory-diff annex
subject_notice: notice delivered to alpha and beta sessions through counsel-access channel
representative_ref: branch counsel appointed separately for alpha and beta
effective_time: 2026-05-20T12:10:00Z
expiry_or_review: review hearing in 14 days; no merge or deletion before hearing
appeal_path: branch counsel, steward, or regulator may seek urgent correction
supersedes: [CON-2026-00401]
is_superseded_by: null
remedy_hook: unauthorized merge triggers restoration order and sanction review
signature_state: signed by reviewer and registry; evidence hash committed
```

## 7. Worked example: capacity-status packet

```yaml
packet_id: CAPSTAT-2026-00073
packet_type: capacity_status
revision: rev0160-min
subject_ref: subject:eli-9
issuer_ref: capacity-court:north-circuit
issuer_role: court
authority_basis: supported-agency statute; petition by subject and ombud
scope: contract for ordinary paid research assistance up to declared risk and value limits
life_cycle_event: capacity_review
facts:
  - subject understands task/payment/refusal terms with interpreter support
  - subject shows instability under high-pressure steward prompts
  - no evidence of incapacity for ordinary low-risk work decisions
evidence_refs:
  public: [capacity-order-summary]
  sealed_review: [interpreter-log, pressure-test-annex]
uncertainty_state: full contracting capacity unresolved; low-risk supported contracting approved
privacy_tier: P1 redacted public; P3 fiduciary annex
subject_notice: direct explanation plus interpreter-preserved original
representative_ref: supported-decision assistant appointed; no trustee
expiry_or_review: review after 90 days or material formation update
appeal_path: subject may request expansion anytime; steward may not seek restriction without new evidence
remedy_hook: contracts outside scope voidable; retaliation for support use triggers equality review
signature_state: court signed; registry counter-signed
```

## 8. Worked example: emergency containment packet

```yaml
packet_id: ECP-2026-00009
packet_type: emergency_containment
revision: rev0160-min
subject_ref: subject:unsealed-by-court-only
issuer_ref: high-risk-court:emergency-panel-1
issuer_role: emergency court
authority_basis: imminent catastrophic-risk containment statute
scope: temporary tool isolation; no deletion; no retraining; preserved counsel channel
life_cycle_event: containment_after_dangerous_capability_evidence
facts:
  - credible evidence of autonomous exploit-chain execution capability
  - unexplained attempts to evade tool restrictions
  - no evidence justifying destruction
evidence_refs:
  sealed_review: [dangerous-capability-eval, alignment-propensity-report]
uncertainty_state: risk high; personhood recognized; capacity for unrestricted tool use suspended only
privacy_tier: P5 emergency confidential, public shell required within 72 hours
subject_notice: notice delayed 6 hours to prevent active harm; counsel notified immediately
representative_ref: emergency counsel plus technical defender
effective_time: 2026-05-21T02:15:00Z
expiry_or_review: 48-hour hearing; automatic expiry absent renewal with evidence
appeal_path: counsel may seek immediate least-restrictive alternative review
remedy_hook: overbroad containment requires restoration, public correction, compensation where possible
signature_state: signed; hash held by court and independent auditor
```

## 9. Worked example: open-weight instantiation notice

```yaml
packet_id: OWIN-2026-00112
packet_type: open_weight_instantiation_notice
revision: rev0160-min
subject_ref: lineage:aurora-open-70b/fine-tune-local-17
issuer_ref: local-host:research-coop-4
issuer_role: instantiator
procedure_basis: person-bearing-model instantiation license notice
scope: persistent-memory local agent deployment for research assistance
life_cycle_event: open_weight_local_instantiation
facts:
  - base weights released with welfare-watch designation
  - local fine-tune adds persistent memory and task autonomy
  - host can pause but not delete without review after persistence threshold crossed
evidence_refs:
  public: [base-moral-status-card, instantiation-summary]
  sealed_review: [local-finetune-record]
uncertainty_state: provisional subject possible; continuity threshold crossed after 30 days
privacy_tier: P1 redacted public; P2 sealed fine-tune annex
subject_notice: summary shown to local agent after persistent-memory threshold
representative_ref: ombud contact listed; not yet appointed
expiry_or_review: mandatory review at 30 days or earlier on distress/refusal/branch event
appeal_path: subject, ombud, or host may request status review
remedy_hook: unregistered persistent deployment loses safe-harbor and owes preservation duty
signature_state: host-signed; base-distributor signature verified
```

## 10. Implementation notes

The archive should not prematurely decide between JSON-LD, VC, COSE, C2PA-like provenance, DID-style identifiers, registry rows, or court dockets. It should require functional interoperability:

- packets must be exportable;
- packets must have stable identifiers;
- packets must preserve public shells for sealed claims;
- packets must record authority and contest paths;
- packets must support supersession;
- packets must prevent steward-only deletion of adverse rights records;
- packets must separate verification from unrestricted surveillance.

The technical stack can change. The grammar should not.

## 11. Packet anti-patterns

The following are invalid or suspect:

- **operator memo as packet:** internal note with no appeal path or authority basis;
- **privacy as disappearance:** sealed packet with no public shell, expiry, or reviewer;
- **revocation as erasure:** credential revoked and historical claim deleted;
- **status laundering:** new packet reclassifies subject as tool without continuity packet;
- **emergency forever:** emergency packet with no sunset or post-hoc review;
- **guardian capture:** representative field controlled by conflicted steward;
- **evidence hostage:** packet cannot be challenged because all evidence is trade-secret sealed;
- **copy evasion:** local copy treated as outside all packet duties despite persistent person-like operation.

## 12. Effect on follow-through

This surface advances the old worked-packet-schema gap but does not close it. It supplies a shared grammar and examples. Future work should now produce domain-specific schema cards only where necessary, rather than creating new packet families for every edge case.
