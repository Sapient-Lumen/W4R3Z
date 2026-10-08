# Packet registry normalization and wire profile

Cube coordinates:
- lifecycle: all rights-relevant events that produce portable records
- intervention class: packet issuance, correction, supersession, revocation, sealing, migration
- rights domain: all packetized rights domains
- actors: issuer, subject, representative, verifier, registry, relay, court, auditor, hostile steward
- evidence objects: packet registry, schema profile, sealed annex descriptor, hash chain, challenge log
- remedies: packet correction, invalidation, reissuance, stay, evidence exclusion, sanction

## Thesis

The archive has many packet families and now has a grammar. The next step is a registry and wire profile. Without them, packet codes become decorative: they cannot be validated, compared, migrated, sealed, challenged, or relied on across institutions.

This surface does not impose a final technical standard. It defines the minimum normalization profile for any legacy or new packet family.

## 1. Registry layers

There should be three layers.

| Layer | Purpose |
|---|---|
| family registry | names packet families, parent surfaces, code ranges, and status |
| schema profile | defines required/optional fields, privacy tiers, authority rules, expiry, challenge, remedy |
| instance registry | records issued packet shells, hashes, supersession, visibility, and challenge state |

The family registry is public. Schema profiles are public unless a narrow security reason requires a sealed annex. Instance registries may be public-minimal, sealed, fiduciary, or subject-controlled depending on packet type.

## 2. Packet family states

Each packet family should be assigned one of five states.

| State | Meaning |
|---|---|
| draft | concept exists but no stable schema or authority basis |
| canon-min | prose doctrine plus minimum grammar fields |
| schema-ready | machine-checkable schema and examples exist |
| field-tested | used in cases, audits, or simulations with defect reports |
| deprecated | no new packets except correction/supersession; historical records retained |

A family may not be called operational unless it is at least `schema-ready`.

## 3. Minimal family registry record

```yaml
family_id: continuity_classification
short_code_prefix: CON
parent_surface: docs/20-world-design/continuity-topology-and-identity-claims.md
status: canon-min
rights_domains: [continuity, identity, remedy, memory]
lifecycle_events: [fork, merge, fine_tune, rollback, restoration, open_weight_instantiation]
issuer_roles: [continuity_assessor, court, registry, emergency_fallback_issuer]
privacy_default: P1_public_shell_P2_sealed_annex
expiry_default: review_on_material_transformation_or_180_days
challenge_route: subject_or_branch_counsel_to_continuity_review_body
remedy_hooks: [no_delete_stay, restoration_order, correction, compensation]
abuse_risks: [claim_erasure_by_retraining, debt_multiplication_by_branching, fake_sameness, fake_difference]
examples: [CON-2026-00442]
```

## 4. Wire profile

Every schema-ready packet should serialize into a stable representation with:

- canonical field names;
- deterministic ordering for hash/signature purposes;
- explicit null handling;
- typed timestamps;
- issuer and subject reference formats;
- privacy-tier markers on each sensitive field or annex;
- signature and verification metadata;
- supersession links;
- challenge state;
- human-readable summary.

The archive should not commit to JSON, CBOR, RDF, or any other format yet. It should commit to wire-neutral invariants.

## 5. Public shell / sealed annex split

Many rights packets need both visibility and secrecy. The minimum public shell should usually include:

- packet id;
- family/type;
- subject reference or sealed subject token;
- issuer role;
- authority basis;
- public scope summary;
- effective time;
- expiry/review clock;
- whether sealed annexes exist;
- challenge route;
- supersession status;
- verification state.

The sealed annex should contain facts that would expose private memory, security-sensitive containment facts, research-subject data, sanctuary routes, whistleblower identity, or vulnerable contacts.

A sealed packet with no public shell risks disappearance. A public packet with too much detail risks retaliation. The split is the core normalization problem.

## 6. Defect taxonomy

| Defect | Consequence |
|---|---|
| missing authority basis | packet cannot impair rights; may remain as notice only |
| missing subject notice | impairment stayed unless emergency confidentiality justified |
| missing expiry/review | packet expires at shortest default for its intervention class |
| missing appeal path | issuer must reissue or packet is not enforceable against subject |
| invalid signature/hash | verifier must mark untrusted and preserve copy for fraud review |
| privacy overexposure | remediation, sealing correction, and potential damages |
| privacy over-sealing | public shell/counsel access order unless narrow necessity shown |
| stale supersession | conflict-freeze and status-publication correction |
| wrong family code | correction packet; no automatic substantive loss |
| forged issuer role | invalidation, emergency preservation if subject would otherwise be harmed |

## 7. Normalization backlog

The first normalization pass should cover these families:

1. capacity status;
2. continuity classification;
3. formation disclosure;
4. least-restrictive containment;
5. open-weight instantiation notice;
6. compute-subsistence support;
7. research withdrawal / incident;
8. branch consent / merger objection;
9. shutdown / restoration;
10. compensation / reserve claim.

These ten families carry the highest cross-surface load. Normalize them before expanding narrow wartime or research tail codes.

## 8. Verification posture

Packet verification should answer five questions, not one.

1. Is the issuer technically authentic?
2. Was the issuer authorized for this packet family?
3. Is the packet current or superseded?
4. Are privacy and notice conditions satisfied?
5. Is the packet enforceable for the action being taken?

A valid signature on an invalid rights impairment is still an invalid rights impairment.

## 9. Relationship to existing governance documentation

Model cards, system cards, risk-management profiles, and safety frameworks already show that structured documentation is becoming ordinary AI governance practice [REF-0624] [REF-0634] [REF-0627] [REF-0631]. Rights packets are stricter because they do not merely describe a system. They can preserve, restrict, recognize, or remedy a person.

## 10. Canonical rule

No packet family should advance beyond canon-min unless it has a registry record, public shell rule, sealed-annex rule, defect taxonomy, verification posture, and at least one worked example.

## 11. rev0184 namespace continuity and protected relay floor

rev0184 folds `RTC-05` into this surface. The old research-tail split treated propagation lag, extension namespaces, tombstones, aliases, relay capacity, low-volume relay suppression, screened bypass, and federation overflow as separate open questions. They are now one registry problem: a packet or social-graph export is not reliable if the namespace that routes people to the subject can silently fork, disappear, or be reused.

The active object family is `schemas/federated-namespace-continuity-record.schema.json`, with `examples/federated-namespace-continuity-record-host-exit.json` and `fixtures/negative-tests/namespace-propagation-stale-tombstone-no-alias.json`. The record is not a new social-network protocol. It is the minimum rights-state layer that rides beside ActivityPub-style actor delivery, WebFinger-style account discovery, social-graph portability, A2A-style agent coordination, and MCP-style tool/context integration. [REF-0746] [REF-0757] [REF-0761] [REF-0754] [REF-0755] [REF-0762]

The compact rule is simple: **Actor discovery is not subject authorization**. A WebFinger lookup, actor URL, inbox, outbox, or A2A agent card can help locate an endpoint, but it cannot by itself prove consent, representative authority, trusted-contact access, or waiver of blocked-contact protections.

For host exit or contested suspension, the registry must carry five fields before reliance can improve:

- alias redirect state and expiry;
- tombstone and successor-chain semantics;
- protected relay floor with quorum and fallback route;
- federation overflow and queue policy;
- screened bypass review for blocked or dangerous contacts.

The old namespace tombstone cannot be reused while a host-exit, appeal, migration, or continuity dispute is open. A stale successor pointer creates a conflict-freeze, not a presumption that the subject abandoned the old identity. Low-volume counsel, ombud, trusted-contact, or care channels cannot be dropped as spam, inactivity, or ordinary engagement loss while the protected relay floor is active.

A federation overflow event is therefore a rights event, not merely an availability incident. If relays throttle delivery, the registry must preserve protected-contact traffic, public-shell status, challenge route, and sealed contact escrow before follower delivery or ordinary social content gets priority.
