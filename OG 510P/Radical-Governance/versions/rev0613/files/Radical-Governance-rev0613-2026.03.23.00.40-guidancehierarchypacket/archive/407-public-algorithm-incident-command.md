# 407 — Public algorithm incident command

## One-line thesis

When an automated or model-assisted public system starts causing harm, instability, or loss of control, government should respond with **incident command**, not slow-motion policy theater.

## Why this matters

A large share of governance failure happens during operation, not procurement. Systems drift, models degrade, upstream data changes, contractors misconfigure thresholds, appeals queues clog, false positives propagate, and public trust collapses faster than formal review cycles can react.

Public institutions therefore need an operating doctrine for machine incidents analogous to outage response or public-health incident management: classify, pause, contain, communicate, repair, review.

## Design rule

Every consequential automated system should have a named incident function with authority to:

- receive alerts,
- declare severity,
- freeze or degrade service,
- preserve evidence,
- coordinate legal, technical, and service teams,
- notify affected communities,
- trigger remedy and after-action change.

## Pattern pack

### 1. Severity ladder

Create a shared severity taxonomy for public algorithm incidents.

Example classes:

- **SEV-1**: imminent or ongoing risk of widespread wrongful denial, detention, benefit interruption, safety harm, or rights infringement;
- **SEV-2**: significant service degradation, repeated high-impact error, or material integrity failure;
- **SEV-3**: contained failure, important near-miss, or recurrent edge-case breakdown;
- **SEV-4**: low-impact defect or documentation discrepancy with no present user harm.

The ladder should bind to concrete response times and decision rights.

### 2. Kill switch and safe degradation

A public model or rules engine should not exist without a defined off-ramp:

- pause automated execution,
- revert to manual review,
- disable a high-risk feature,
- narrow the eligible case set,
- slow batch processing,
- place outputs behind secondary approval.

“Too integrated to pause” is an indictment of system design, not an excuse.

### 3. Evidence capture packet

At incident declaration, preserve:

- model or ruleset version,
- feature and threshold state,
- input data snapshot policy,
- affected cohorts and case counts,
- override logs,
- user complaints,
- vendor tickets,
- public communications issued.

Without evidence capture, institutional memory gets replaced by blame diffusion.

### 4. Joint command cell

The command function should include, at minimum:

- operational owner,
- technical lead,
- service lead,
- legal or rights lead,
- communications lead,
- appeals or remediation lead,
- vendor liaison where relevant,
- independent reviewer trigger for severe cases.

This avoids the common pattern where engineering, legal, and frontline service teams all learn different versions of the same incident.

### 5. Rights-first notification

When an incident can affect entitlements, obligations, safety, or status, notice should not wait for polished certainty. Institutions should publish:

- what failed,
- who may be affected,
- what interim protection applies,
- whether previous decisions are being reviewed,
- how people can report harm,
- when the next update is due.

### 6. Near-miss register

Most catastrophic failures begin as “small anomalies.” Record:

- unexplained overrides,
- recurring operator workarounds,
- sudden distribution shifts,
- unusual appeal surges,
- moderation reversals,
- data feed irregularities,
- inconsistencies between policy and model behavior.

Near-miss discipline turns weak signals into governance intelligence.

### 7. After-action change duty

After each serious incident, publish or retain an after-action record covering:

- root cause,
- exposure window,
- affected populations,
- immediate fixes,
- structural fixes,
- procurement or governance implications,
- whether deployment should resume, narrow, or sunset.

## Guardrails

- Incident command must not become a secrecy shield; severe incidents need external visibility.
- Vendor confidentiality cannot override evidence preservation or public-law duties.
- “Human in the loop” does not negate incident obligations if the system materially structured the outcome.
- Pause authority must exist before launch, not be invented during crisis.
- Appeals, ombuds, and oversight bodies need a route into the incident process.

## Failure modes

- **alert without authority**: staff can see the problem but cannot pause it.
- **technical containment only**: teams restore throughput while ignoring rights impacts.
- **communications vacuum**: the public learns from leaks, not the institution.
- **incident amnesia**: lessons are not encoded into thresholds, contracts, or governance.
- **vendor buffering**: responsibility disappears into the contractor boundary.

## Metrics that matter

Track:

- time from first signal to incident declaration,
- time to safe degradation or pause,
- number of affected cases identified and reviewed,
- near-miss volume by system and office,
- time to public notice,
- time to remedy,
- repeated incidents by root-cause family.

## Compression rule for the archive

When a system is too important to fail quietly, ask:

**Who can stop it today, on what evidence, and what happens to affected people during the stop?**

If the answer is vague, the system is not operationally governable yet.
