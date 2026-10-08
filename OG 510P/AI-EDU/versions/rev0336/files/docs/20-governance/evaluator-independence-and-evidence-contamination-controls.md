# Evaluator independence and evidence-contamination controls

AI education services can look evidenced before they are evidenced. Vendor claims, operator pride,
staff convenience, learner enthusiasm, tidy schemas, and public-summary polish can all contaminate
evaluation if the archive does not separate evidence roles.

The rule is: **the person who benefits from promotion should not be the only person who certifies
promotion**.

## Evidence-contamination classes

| Code | Contamination risk | Default control |
|---|---|---|
| `ECI0` | no evaluation claim | Keep as design rationale or example. |
| `ECI1` | operator-only claim | Label as local judgment; do not promote evidence grade. |
| `ECI2` | vendor or model-provider claim | Require local owner review and claim-family separation. |
| `ECI3` | convenience mistaken for learning | Split workload, usability, and learning claims. |
| `ECI4` | protected facts used to strengthen public story | Keep protected review local and publish only abstract safeguards. |
| `ECI5` | security test details used as transparency proof | Publish risk class and owner, not exploit payloads. |
| `ECI6` | conflicted closure review | Add independent reviewer or keep followthrough live. |
| `ECIX` | evidence laundering or fake source elevation | Quarantine and fail closure. |

## Reviewer independence minimums

For ordinary sandbox examples, one named local owner may be enough. For `FT-0181` closure, use a
minimum split:

- one educational or assessment reviewer who can judge construct, cognitive effort, and claim family;
- one record, privacy, security, accessibility, or operations reviewer who can judge leakage,
  authority, public summary, and rollback;
- no reviewer may treat their own implementation convenience as learning evidence without a separate
  learning claim check;
- vendor-authored metrics require local owner interpretation before they can support a public claim;
- protected facts may inform local safety decisions but must not become public evidence decoration.

When reviewers disagree about source class, claim strength, action authority, protected-route
separation, or public-summary safety, the default is no closure until the disagreement is resolved or
converted into a visible unresolved block.

## Claim-family separation

A strong claim in one family cannot average away weak evidence elsewhere:

- usability does not prove learning;
- time saving does not prove reduced burden after review and repair;
- absence of incidents does not prove security;
- accessibility feature presence does not prove equitable access;
- student satisfaction does not prove durable understanding;
- compliance review does not prove pedagogical value;
- schema validity does not prove field evidence.

Use the claim-family evidence matrix before a public summary, procurement note, or lifecycle
decision repeats a broad claim.

## Contamination log

A real-import closeout should record contamination risks explicitly:

- which claims came from vendor text, implementer notes, learner/family feedback, teacher review,
  aggregate metrics, or independent assessment;
- which claims were downgraded, removed, or held as local judgment;
- which protected or security facts were kept out of the public archive;
- which reviewer conflicts remain unresolved;
- which public words were removed because the evidence grade did not support them.

## Current archive bet

The hardest late-stage error is not a broken schema. It is a clean schema that laundered weak or
conflicted evidence into a stronger public story. Independence controls make overclaiming visible
before it becomes policy, procurement, or assessment infrastructure.

See [`../30-operations/real-import-acceptance-tests-and-reviewer-calibration.md`](../30-operations/real-import-acceptance-tests-and-reviewer-calibration.md),
[`../30-operations/real-import-closeout-board-and-decision-minutes.md`](../30-operations/real-import-closeout-board-and-decision-minutes.md),
[`claim-family-evidence-matrix.md`](claim-family-evidence-matrix.md), and `AS-0238`.
