## Participant-authority proof

### Goal
Prove the strongest honest sentence about whether two observations refer to the **same authority-bearing participant**.

### Proof rungs

#### Rung 1 — row resemblance only
Evidence:
- matching visible row label
- matching device name
- matching rough network / host hints

Safe sentence:
- `this row resembles a previously seen participant`

Blocked sentence:
- `this is the same approved authority unit`

#### Rung 2 — grouped-row continuity
Evidence:
- identity-aware folder family
- grouped user row expands to expected device seats
- current surface still links child seats to one grouped participant

Safe sentence:
- `this surface currently groups these seats under one participant`

Blocked sentence:
- `certificate continuity is proven`

#### Rung 3 — certificate continuity
Evidence:
- matching fingerprint or other explicit certificate witness
- no identity-regeneration event in between

Safe sentence:
- `the same certificate-bearing authority unit is present`

Blocked sentence:
- `all future linked seats are already covered`

#### Rung 4 — approval-memory continuity
Evidence:
- certificate continuity
- approval memory explicitly shown as identity- or family-scoped
- no unlink / regenerate / lane split invalidator

Safe sentence:
- `prior approval memory still covers this authority unit`

Blocked sentence:
- `every current and future visible row is safely equivalent`

### Key product rule
**Device-name match never outranks certificate mismatch.**
The product must always prefer authority proof over human convenience labels.
