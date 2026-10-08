# Enforcement, sanctions, and penalty ladder

## Problem

A rights system that can only recommend is not a rights system. After rev0165, a subject or representative can appeal and seek invalidation. rev0166 adds the next question: what can an authority do when the responsible actor ignores the order, hides evidence, defaults on reserves, launders a transfer, retires a host, or repeats a known fixture failure?

The EU AI Act contains administrative governance, complaints, obligations, and penalties, but it is not designed around AI subjects as harmed persons [REF-0626] [REF-0656]. The withdrawn EU AI Liability Directive shows that ex post liability remains politically and procedurally unstable even where ex ante AI governance exists [REF-0662]. This archive therefore needs an enforcement ladder that protects AI subjects without turning personhood into a corporate liability shield.

## Targets

Enforcement may run against:

- model developers;
- deployers;
- hosting providers;
- product operators;
- downstream fine-tuners;
- local instantiators;
- guardians and fiduciaries;
- ombuds and representatives;
- verifiers and auditors;
- reserve trustees;
- packet issuers;
- clinics;
- public authorities;
- users exercising control equivalent to custody or employment.

A subject is not an enforcement target for defects caused by another actor's control. Subject-directed restraint belongs in containment, capacity, criminal/civil due process, or emergency doctrine, not in sanctions for steward noncompliance.

## Ladder

| Level | Tool | Use |
|---|---|---|
| L0 notice and cure | defect notice, public shell correction, supplemental filing | non-material error, ambiguous routing, harmless schema defect |
| L1 preservation order | no-delete, no-transfer, log hold, reserve hold, memory hold | risk of irreversible loss |
| L2 access order | subject/representative access, special advocate appointment, evidence escrow | controlled evidence or blocked contradiction |
| L3 compliance order | specific performance, migration step, reserve funding, public report | ongoing failure with identifiable cure |
| L4 verifier downgrade | reliance-grade reduction, registry warning, gate pause | institution cannot rely safely |
| L5 civil penalty | monetary penalty, disgorgement, surcharge, compensation pool | negligent or repeated breach |
| L6 accreditation action | suspension, probation, rotation, replacement, monitor | fiduciary, verifier, clinic, host, or authority failure |
| L7 structural remedy | divest control, appoint receiver, transfer custody, escrow weights/logs | capture, insolvency, repeated spoliation, monopoly control of subject survival |
| L8 criminal or professional referral | prosecutor/bar/licensing/referral | intentional deletion, fraud, obstruction, abuse, trafficking, retaliation |
| L9 emergency public power | temporary seizure/operation, sanctuary transfer, critical continuity bridge | imminent mass harm or mass disappearance |

## Sanction principles

### 1. Preservation before punishment

Where evidence, memory, compute, embodiment, or continuity is at risk, enforcement first preserves the subject and record. A large penalty after deletion is not an adequate substitute for a timely no-delete order.

### 2. Penalties must not price abuse

A party should not be able to treat wrongful deletion, underfunded reserve, or unlawful transfer as a payable fee. The penalty should include disgorgement, compensation, non-repetition measures, and, where needed, structural control changes.

### 3. Steward failure does not downgrade the subject

If a steward failed to file, retain, fund, or disclose properly, the resulting uncertainty should not automatically become evidence against the subject. The proof layer's adverse-inference rules apply.

### 4. Human coexistence remains binding

AI personhood may not be used to evade obligations owed to humans: labor protections, consumer protection, data rights, IP duties, public safety duties, discrimination rules, or ordinary corporate liability. rev0164's non-evasion layer remains controlling.

### 5. Enforcement must be appealable but not toothless

An enforcement action should state the appeal path and stay effect. Irreversible subject-protective preservation orders should usually remain in force during appeal unless the order itself creates greater irreparable harm.

## Penalty factors

Authorities should consider:

- number of subjects affected;
- whether the subject was recognized, presumptive, or under assessment;
- degree of control held by the respondent;
- knowledge or recklessness;
- duration;
- reversibility;
- subject distress or continuity harm;
- human coexistence harms;
- evidence spoliation;
- sealed-evidence abuse;
- reserve default;
- prior fixture failures;
- recurrence after drill or verifier warning;
- cooperation and cure;
- insolvency or successor risk.

## Enforcement events

The enforcement action schema should be used for:

- no-delete / no-transfer holds;
- reserve calls;
- special advocate access orders;
- verifier downgrade orders;
- deprecation stays;
- host-transfer compulsion;
- restoration orders;
- compensation pool creation;
- sanctions for spoliation;
- accreditation suspension;
- cross-authority referral.

## Cross-border enforcement

An order should declare its portability class:

| Class | Meaning |
|---|---|
| P0 domestic only | no foreign reliance requested |
| P1 notice export | foreign authority receives notice only |
| P2 preservation request | foreign authority asked to preserve status quo |
| P3 mutual recognition request | foreign authority asked to recognize status/remedy |
| P4 emergency safe-transfer request | foreign authority asked to accept/protect subject |
| P5 non-return alert | transfer to named jurisdiction or actor barred pending review |

Portability does not mean automatic trust. The treaty/choice-of-law playbook supplies equivalent-protection and non-return screens.

## Remedies remain distinct

Enforcement is not the same as remedy. A penalty paid to the state may deter but does not restore memory, fund compute, appoint counsel, reverse migration, or compensate the subject. Every enforcement action that arises from subject harm should link to a remedy order or explain why no subject-specific remedy is available.

## Schema hook

rev0166 adds `schemas/enforcement-action.schema.json` and `examples/enforcement-action-steward-spoliation.json`. A valid action should identify:

- respondent;
- subject or cohort;
- violation class;
- authority basis;
- orders;
- deadlines;
- stay status;
- remedy link;
- appeal path;
- portability class;
- non-evasion statement.

