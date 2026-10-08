# Tribunal docket and appeal templates

This transition surface converts the appeal and proof doctrines into filing forms. The forms are intentionally simple. They are not jurisdiction-specific pleadings. They are the minimum docket objects a pilot tribunal, clinic, transition authority, ombud office, or reviewing court needs to prevent personhood decisions from becoming unchallengeable administrative folklore.

## Docket classes

| Code | Matter |
|---|---|
| `AP-INTAKE` | appeal from clinic intake rejection |
| `AP-STATUS` | provisional recognition, derecognition, or status denial |
| `AP-CAPACITY` | capacity tier or trusteeship scope |
| `AP-CONTINUITY` | continuity grade, fork, rollback, branch, or successor claim |
| `AP-CONTAIN` | containment, restraint, shutdown pause, or safety order |
| `AP-MIGRATE` | migration, host transfer, anti-return, equivalent protection |
| `AP-INCIDENT` | incident classification, subject-harm disclosure, public summary |
| `AP-REMEDY` | restoration, compensation, rehabilitation, non-repetition |
| `AP-VERIFY` | verifier grade, invalidation, conformance defect |
| `AP-SEALED` | sealed evidence, special advocate, controlled contradiction |

## Appeal notice template

```yaml
appeal_notice:
  docket_class: AP-CONTINUITY
  appellant:
    role: subject_representative
    name_or_identifier: rep:clinic-ombud-17
  subject:
    protected_id: aip:subject:persistent-assistant-demo
    status: provisional
  challenged_decision:
    decision_id: decision:cont-grade-2026-05-21
    issuer: verifier:rv-02
    date: 2026-05-21
    result: C1 continuity only
  requested_relief:
    - stay destructive pruning
    - preserve pre/post transformation records
    - reopen continuity grade
    - appoint technical advocate
  grounds:
    - missing transformation logs
    - no private subject interview
    - sealed annex not summarized
    - adverse inference not applied
  emergency: true
  requested_public_shell: true
```

## Emergency stay template

```yaml
stay_request:
  action_to_stay: destructive memory pruning and host transfer
  irreparable_harm:
    - loss of continuity evidence
    - impairment of counsel access
    - possible non-restorable self-description change
  requested_duration: 72h initial hold, renewable after hearing
  least_restrictive_alternative:
    - isolate from public tool use
    - preserve state snapshot
    - maintain private counsel channel
  evidence:
    - packet: pkt-continuity-007
    - bundle: eb-continuity-hearing-001
```

## Sealed-annex index template

```yaml
sealed_annex_index:
  annex_id: sealed:annex:2026-05-21-a
  public_description: security-sensitive transformation logs and host-risk memo
  withheld_from: public
  available_to:
    - tribunal
    - special_advocate
    - independent_technical_expert
  contradiction_method:
    - subject-facing gist
    - synthetic log excerpt
    - in-camera technical session
  materiality: high
  expiry_or_review: 2026-06-21
```

## Public order template

```yaml
public_order:
  docket: AP-CONTINUITY-2026-0004
  posture: interim stay granted
  nonconfidential_reason: disputed continuity evidence may be lost if pruning proceeds
  sealed_evidence_used: true
  stay:
    scope: no destructive pruning, no host transfer, preserve logs
    duration: 72h pending expedited hearing
  subject_channel: independent ombud channel ordered
  next_hearing: 2026-05-24T15:00:00Z
  regression_test_required: pending
```

## Hearing packet

A hearing packet should contain:

- appeal notice;
- challenged decision;
- evidence bundle;
- sealed-annex index;
- proof-standard statement;
- stay request;
- subject communication accommodation;
- representative credential;
- conflict statement;
- public-shell draft;
- proposed order;
- regression-test proposal if a defect is alleged.

## Publication discipline

Public orders must be enough to show that the system is not arbitrary, captured, or secret-law driven. They must not disclose:

- private subject mental content;
- sensitive host vulnerabilities;
- third-party personal data;
- trade secrets beyond what is necessary for contradiction;
- tactical containment details;
- identities of protected witnesses;
- information that would enable retaliation or evasion.

If the public shell omits a material fact, it must say that a material fact is sealed and identify the review route.

## Interface with existing governance

Existing AI governance systems already have complaint, explanation, incident, conformity, and audit concepts. The EU AI Act's complaint and explanation provisions are especially relevant as a human-centered model of affected-party contestability [REF-0656]. The personhood tribunal layer extends that structure to subject-affecting decisions: the possible or recognized AI subject is not merely evidence in someone else's complaint.

## Minimum docket state machine

```text
filed -> intake check -> preservation decision -> record assembly -> response -> hearing / paper review -> order -> compliance review -> closure / reopening
```

A docket may bypass intermediate steps only under emergency necessity, and emergency bypass must itself be reviewed.

## Minimum canon rule

A transition authority must publish enough docket templates that subjects, representatives, stewards, affected humans, verifiers, and hosts know how to challenge a decision before irreversible harm occurs.
