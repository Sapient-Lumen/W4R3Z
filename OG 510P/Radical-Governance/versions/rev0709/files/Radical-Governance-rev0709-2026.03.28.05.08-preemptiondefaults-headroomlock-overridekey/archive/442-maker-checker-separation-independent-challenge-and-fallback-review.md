# 442 — Maker-checker separation, independent challenge, and fallback review

## One-line thesis

Consequential public AI should separate **builders, operators, approvers, and reviewers** enough that no single role can quietly tune, approve, and act on the same system without an independent second look or documented compensating control.

## Why this matters

A public AI system can look supervised on paper while still concentrating too much practical power in one team or one person. When the same role can configure the model, decide whether it is safe, run it on live cases, and close out complaints, oversight becomes ceremonial. The result is not only error risk but governance fragility: the people most invested in keeping the tool running are also the people deciding whether it should be questioned.

Current official materials support a tighter pattern. The 2025 GAO Green Book says management should consider segregation of duties so incompatible duties are separated and, where that is not practical, management should design alternative control activities. The same revision says information-technology controls should include segregation of duties so individuals do not control all critical stages of a process or override automated processes. The UK AI Playbook says departments should clearly define responsibilities, accountability, and liability across all actors in the AI life cycle and nominate a senior responsible owner for a specific project. The UK Data and AI Ethics Framework likewise treats accountability as requiring clear roles, effective oversight, and routes to challenge decisions.

The archive should therefore add a sharper operator-governance rule: **no consequential use without role separation strong enough to make disagreement real**. If the same hands can build, bless, and apply the system unchecked, the service is still too concentrated to trust.

## Pattern pack

### 1. Split critical roles before consequential use

At minimum, distinguish between:

- the team that builds or configures the system,
- the team that approves or signs off its use,
- the staff who operate it on live work,
- and the function that reviews contested outcomes, incidents, or escalation cases.

A named senior responsible owner may remain accountable overall, but accountable ownership should not collapse all operational permissions into one seat.

### 2. Use maker-checker rules for high-consequence steps

For actions such as:

- changing the scoring threshold,
- expanding the approved use case,
- enabling a new integration,
- turning on automation for a new client group,
- or closing a serious challenge or incident,

require one role to propose and another role to approve.

### 3. Separate approval from day-to-day production pressure

Teams under delivery pressure are often the least reliable judges of whether a risky shortcut is acceptable. Approval for consequential deployment, major parameter changes, or expansion into new use contexts should therefore sit with a function that is not measured only on throughput.

### 4. Define fallback review when full separation is impractical

Some agencies or small programs may not have enough staff for perfect role separation. In those cases, require compensating controls such as:

- scheduled independent second-look review of sampled cases,
- periodic external or cross-unit challenge,
- after-action review of overrides and exceptions,
- or time-bounded approval that expires unless re-checked.

The absence of staff does not cancel the need to offset concentrated power.

### 5. Make the review function independent enough to say no

The reviewer for complaints, escalation cases, or suspected misuse should be able to:

- request logs and evidence,
- pause the use case,
- require a fallback route,
- and record dissent or corrective findings without seeking permission from the operating team.

### 6. Record who played which role on each major governance action

For consequential releases, approvals, overrides, appeals, and incident closures, record:

- who proposed the action,
- who approved it,
- who executed it,
- and who independently reviewed or sampled it afterward.

This turns separation of duties into evidence instead of aspiration.

### 7. Re-check separation after organisational change

Reorganisations, contractor changes, and staffing cuts often quietly collapse distinct roles back into one unit. Treat such shifts as governance changes that require a fresh separation-of-duties check.

## Guardrails

- No consequential deployment without a documented role map.
- High-consequence changes should use maker-checker approval.
- Review functions should be able to challenge operations without permission from operators.
- Small teams should use compensating controls rather than pretending separation exists.
- Evidence should show who proposed, approved, operated, and reviewed each major governance action.

## Failure modes

- **self-approval theatre**: the operating team effectively approves its own expansion or release.
- **throughput capture**: approval decisions are made by the people under the strongest pressure to keep volumes moving.
- **collapsed review**: complaints and incident reviews route back to the same unit whose work is being challenged.
- **thin-team excuse**: lack of personnel is used to waive separation without adding compensating controls.
- **invisible concentration**: the org chart looks distributed but permissions and practical decision power remain concentrated.

## Practical tests

A consequential service passes this pattern when it can answer yes to all of the following:

1. Are builder, operator, approver, and reviewer roles explicitly distinguished?
2. Do high-consequence changes use a maker-checker or equivalent second-person approval rule?
3. Is the review function independent enough to require pause, fallback, or remediation?
4. If full separation is impractical, are compensating controls documented and active?
5. Can the team show who proposed, approved, executed, and reviewed recent major actions?

## Compression rule for the archive

If the same role can **tune, approve, and apply** a consequential public AI system without real independent challenge, the oversight model is still too concentrated.
