# 410 — Public deployment registries for automated state action

## One-line thesis

When public institutions use automated or AI-assisted systems that shape decisions, entitlements, enforcement, or public interaction, there should be a **living deployment registry** that shows what is in use, in what phase, under whose authority, and with what transparency record.

## Why this matters

Public controversy over automated systems often begins with basic discovery failure. Nobody can easily answer:

- what systems are actually in use,
- which ones are only pilots,
- which ones are retired but still influential through legacy outputs,
- who owns them,
- where people can find the relevant transparency record, impact review, or appeal path.

This opacity makes oversight slow and public trust brittle. It also lets institutions overstate experimentation while understating production use.

A deployment registry is therefore not a public-relations flourish. It is the minimum map required for accountable operation.

## Design rule

Any public body using consequential automated systems should maintain a searchable registry that records, at minimum:

- system name,
- owning body,
- function,
- decision context,
- operational phase,
- legal or policy basis,
- public documentation links,
- contact or complaint route,
- review and retirement status.

## Pattern pack

### 1. Registry the whole lifecycle

Track systems across phases such as:

- pre-deployment,
- pilot,
- beta,
- production,
- degraded operation,
- retired.

A public system should not become visible only after scandal.

### 2. Register use, not just procurement

The registry should focus on actual public deployment:

- where the system affects a real decision,
- where it directly interacts with the public,
- where staff rely on outputs to triage or prioritise cases,
- where previous outputs continue shaping downstream action.

Buying software is not the same thing as putting automated state action into service.

### 3. Link to the evidence trail

Each entry should link, where applicable, to:

- transparency records,
- impact assessments,
- data protection assessments,
- testing summaries,
- incident notices,
- appeal or complaint guidance,
- procurement or vendor information at the right level of abstraction.

### 4. Record the authority boundary

Each entry should show:

- who can operate the system,
- who can pause it,
- who approves model or rule changes,
- whether the public body or vendor holds the release gate,
- what human review exists in the loop.

### 5. Make phase changes visible

When a system moves from pilot to production, narrows scope, or is retired, the registry should log:

- date of change,
- reason,
- decision maker,
- whether previous documentation still applies,
- whether affected people need notice.

### 6. Separate public visibility tiers carefully

Some information may need restricted handling, but the default should be public discoverability. Use a layered model:

- public summary for discovery and accountability,
- oversight-access detail for audit and supervision,
- restricted technical detail only where justified.

“Security” should not become a blanket excuse for registry absence.

### 7. Audit the registry against reality

At regular intervals, reconcile the registry against:

- procurement records,
- vendor invoices,
- API traffic,
- model repositories,
- incident rosters,
- internal inventories,
- frontline service reports.

An unverified registry decays into symbolic compliance.

## Guardrails

- Registry scope should follow public effect, not branding labels such as “AI” or “advanced analytics.”
- Systems influencing rights, benefits, access, safety, or public contact deserve the strongest presumption of inclusion.
- Retired systems should remain visible long enough to support challenge and audit.
- Entries should be understandable by non-specialists.
- Public bodies should assign named ownership for keeping entries current.

## Failure modes

- **inventory theater**: organisations list experiments but omit consequential production tools.
- **phase laundering**: live systems are described as pilots indefinitely.
- **orphaned records**: old transparency documents stay online while the real system changes underneath them.
- **hidden release gates**: no one outside the vendor boundary knows who can ship changes.
- **retirement amnesia**: harmful systems disappear from the record just when accountability matters most.

## Practical tests

A public deployment registry passes when it can answer yes to all of the following:

1. Can a member of the public discover which automated systems materially affect them?
2. Does each entry show phase, owner, purpose, and complaint or appeal route?
3. Are material changes to scope or deployment status dated and visible?
4. Can oversight bodies reconcile the registry against actual operational use?
5. Do retired entries remain available long enough to support review and remedy?

## Compression rule for the archive

When the state automates public action, ask:

**Where is the live map of what exists, who owns it, and what record trails go with it?**

If that map is missing, oversight starts in the dark.
