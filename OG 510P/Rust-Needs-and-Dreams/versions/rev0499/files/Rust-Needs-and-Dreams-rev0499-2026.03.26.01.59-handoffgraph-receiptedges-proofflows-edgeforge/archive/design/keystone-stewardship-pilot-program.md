# Design: Keystone Stewardship Pilot Program (criticality, institutional support, continuity, obligations)

## Goal
Turn the **Keystone Stewardship Stack** from an interesting strategic synthesis into a ranked execution program that can prove real value on a few high-leverage subjects before the archive starts talking as if Rust already has a mature “critical projects” program.

## Why this needs a pilot layer
The archive already has strong maintenance, trust, release, and support layers. What it did not yet state clearly enough is:
- which projects should be piloted as keystone subjects first;
- how to distinguish keystone criticality from mere popularity;
- when institutional support posture is relevant enough to publish;
- when private operational details can be summarized safely;
- and when a subject is ready to be called `keystone`, `watch`, `candidate`, or `defer`.

Without this layer, the archive risks two opposite failures:
1. **critical-crate theater** — projects are casually described as foundational without continuity, governance, or obligation evidence;
2. **institutional-theater** — a project receives funding or hosting attention, but the ecosystem still cannot tell what changed or what obligations now follow.

## Design principles
1. **Start with subjects whose criticality is legible.** Avoid ambiguous “maybe important” cases first.
2. **Keep public summaries honest about restricted detail.** “Not published” is allowed.
3. **Support posture must stay explicit.** Volunteer, employer-backed, grant-backed, and foundation-hosted are not interchangeable.
4. **Transitions matter.** A keystone pilot should capture before/after stewardship changes, not only steady-state status.
5. **Consumers come after evidence.** Atlas/adoption/funding/policy views should import pilot outputs.
6. **Not every important project graduates.** `candidate`, `watch`, and `defer` are useful outcomes.

## Pilot artifact family
### 1) `keystone-pilot-brief/v0`
Explains why a subject is a good keystone pilot now:
- subject id and summary
- why the ecosystem role is legible
- why the review is timely
- likely consumer classes
- likely restricted-detail boundaries

### 2) `keystone-criticality-budget/v0`
Declares what must be shown to justify keystone treatment:
- ecosystem-role evidence required
- blast-radius or operational-dependence factors
- exclusions and non-claims
- freshness requirements

### 3) `keystone-support-contract/v0`
States what support/governance posture the pilot is trying to make reviewable:
- maintainer/staffing posture
- governance or host arrangement
- funding/support channels
- public-vs-restricted detail policy
- declared obligations and escalation paths

### 4) `keystone-risk-budget/v0`
Defines what continuity and governance risks must be surfaced:
- key-person risks
- authority concentration
- funding uncertainty
- infra/ops concentration
- succession gaps
- mitigation expectations

### 5) `keystone-pilot-scorecard/v0`
Decides whether the pilot is credible:
- is criticality justified?
- is support posture legible enough?
- are restricted details handled honestly?
- are obligations explicit enough for consumers?
- should the subject be `keystone`, `candidate`, `watch`, or `defer`?

### 6) `keystone-pilot-pack/v0`
Bundle for publication and reuse:
- pilot brief
- criticality budget
- support contract
- risk budget
- imported maintenance/trust/release/support attachments
- scorecard
- consumer summary

## Ranked first pilots

### 1) Security keystone lane
**Why first**
- The Rust Innovation Lab launch with Rustls is the clearest current public example of a Rust project being treated as foundational infrastructure that needs stronger support and neutral backing.
- Security-facing projects make continuity, governance, and response posture especially legible.

**What must be explicit**
- why the subject counts as keystone infrastructure
- what institutional support exists
- what continuity/security obligations are declared versus aspirational
- what risks remain despite support

**Success bar**
A reviewer can understand why a security project is keystone infrastructure and what changed when it gained stronger institutional support.

### 2) Shared-building-block lane
**Why second**
- Rust has widely reused common building blocks whose ecosystem role is clear even when they are not flashy products.
- This pilot proves keystone review is not only for security projects.

**What must be explicit**
- the kind of common-ground role the project plays
- whether stewardship is mostly volunteer, employer, or institutionally supported
- what compatibility/support obligations are realistic for a building block
- what would trigger a succession or escalation concern

**Success bar**
A neutral common building block can be described as keystone infrastructure without collapsing into a “most downloaded crates” chart.

### 3) Ecosystem-service / infra lane
**Why third**
- Some keystone subjects are services or infra components rather than ordinary library releases.
- This pilot proves the stack can handle hosted/project-service subjects and public-vs-restricted operational boundaries.

**What must be explicit**
- service or infra subject identity
- public support/continuity claims
- what details are intentionally restricted
- what obligations downstream users may still rely on

**Success bar**
A service-style subject can publish a useful keystone summary without exposing unsafe operational detail.

### 4) Continuity-transition lane
**Why fourth**
- The stack matters most when stewardship posture changes.
- This is where the archive can capture movement into maintainer funding, foundation hosting, or formal succession.

**What must be explicit**
- before/after support posture
- added or removed obligations
- what continuity risk was reduced
- what remained unresolved

**Success bar**
A project transition can be described as more than a celebratory announcement or a vague governance note.

### 5) Consumer-import lane
**Why fifth**
- Once earlier pilots exist, Atlas/adoption, policy/trust, and support/funding programs can import them.
- This is how keystone stewardship becomes ecosystem infrastructure instead of archive-local theory.

**What must be explicit**
- which consumer gets which facts
- freshness and non-claim posture
- what private detail was intentionally not imported
- how a consumer should avoid overclaiming

**Success bar**
At least one adoption/atlas-style consumer and one funding/support-style consumer can reuse keystone facts honestly.

## Pilots to defer
These matter later, but are weaker opening bets:
- **global critical-crate rankings** — too easy to become prestige theater;
- **foundation-only governance schemas** — too narrow and too political for the opening move;
- **fully automated criticality scoring** — too lossy and too easy to confuse with responsibility;
- **private risk databases** — important operationally, but poor first public archive material.

## Immediate archive consequences
Read this file together with:
- [`design/keystone-stewardship-stack.md`](./keystone-stewardship-stack.md)
- [`gaps/keystone-projects-critical-infrastructure-and-institutional-stewardship-contracts.md`](../gaps/keystone-projects-critical-infrastructure-and-institutional-stewardship-contracts.md)
- [`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md)
- [`design/trust-decision-stack.md`](./trust-decision-stack.md)
- [`design/library-productization-stack.md`](./library-productization-stack.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)

The archive should now prefer:
- **criticality reviews over popularity talk**,
- **institutional-support truth over vague “well funded” language**,
- **transition reports over celebratory anecdotes**,
- **restricted-detail honesty over fake transparency**,
- and **consumer imports over repeated prose summaries**.

## What should wait
Do **not** start with:
- a universal critical-project badge,
- a foundation-managed crate canon,
- automated download-count thresholds as keystone proof,
- or a private governance program hidden behind public labels.

Those may become consumers or overlays later.
They are not the missing substrate.
