# 411 — Diffable public rules, version windows, and change logs

## One-line thesis

Public rules should be **dated, versioned, diffable, and announced with compatibility windows** so people, agencies, and vendors can tell what changed, when it changed, and how long they have to adapt.

## Why this matters

Governments often publish a new rule, interface, eligibility logic, or documentation page as though publication itself solved the coordination problem. In practice, institutions need more than a fresh PDF or silent page update. They need to know:

- what version is in force,
- what changed from the previous version,
- when the new version becomes mandatory,
- what compatibility window exists,
- where earlier versions can still be inspected,
- whether public feedback altered the final rule.

Without those disciplines, change becomes administratively expensive and politically slippery. Agencies scramble, vendors improvise, and affected people cannot prove what the rule said when their case was handled.

## Design rule

Any consequential public rule layer — legal text, API contract, policy schema, eligibility logic, or operational standard — should publish:

- a stable identifier,
- dated versions,
- a human-readable change log,
- machine-readable access where practical,
- deprecation and compatibility windows,
- a notice of how feedback shaped the final change.

## Pattern pack

### 1. Separate current, historical, and prospective views

Public systems should expose at least:

- the current version,
- prior dated versions,
- where relevant, prospective versions not yet in force.

This is essential where decisions can be contested later.

### 2. Publish the delta, not just the document

For each meaningful revision, publish a concise change log that states:

- what changed,
- why it changed,
- who approved it,
- when it takes effect,
- what breaks or deprecates,
- where migration guidance lives.

People should not need forensic comparison to discover a policy shift.

### 3. Promise compatibility windows

Where interfaces or operational rules change, define:

- minimum notice period,
- support window for the previous version,
- dual-running expectation where needed,
- retirement date,
- emergency-change exception process.

This keeps public adaptation from becoming a race won only by the biggest actors.

### 4. Make machine-readable access normal

Where the rule layer is operationally consumed by software, publish machine-readable forms where practical:

- structured schemas,
- versioned specifications,
- open APIs,
- formal status codes,
- downloadable reference data.

Machine-readability is not a luxury when the state expects other systems to comply.

### 5. Preserve the reason trail

When consultation or stakeholder input shaped the final version, publish a compact explanation of:

- what concerns were raised,
- which changes were made,
- which suggestions were rejected,
- why the final design took its present form.

Silence about the reason trail makes participation feel cosmetic.

### 6. Version the documentation too

Rules fail when the implementation guide, legal basis, and API docs drift apart. Version:

- the rule itself,
- the implementation guidance,
- the example payloads or forms,
- the test environment,
- the migration guide.

### 7. Build challenge-ready records

Where a rule affects benefits, obligations, enforcement, or eligibility, the system should retain enough information to reconstruct:

- which version governed a decision,
- what documentation was available at the time,
- whether the transition period had ended,
- whether the affected person received appropriate notice.

## Guardrails

- Emergency changes should still receive retrospective change logs and dated records.
- Silent edits to consequential guidance should be avoided.
- Compatibility promises should be short enough to maintain progress but long enough to prevent coercive churn.
- Public archives should not erase superseded versions needed for review.
- Versioning should cover both legal text and operational interfaces when both matter.

## Failure modes

- **silent drift**: the guidance changes without dated notice.
- **one-version amnesia**: historical versions disappear, undermining audit and challenge.
- **breaking by surprise**: agencies or vendors learn about change only when integrations fail.
- **participation void**: the public sees consultation requests but never sees what changed because of them.
- **document divergence**: the law, guidance, and API contract no longer describe the same operating reality.

## Practical tests

A public rule layer passes when it can answer yes to all of the following:

1. Can a user retrieve the current, historical, and, where relevant, prospective version?
2. Does each significant change have a dated human-readable change log?
3. Are compatibility and deprecation windows explicit?
4. Is there machine-readable access where software compliance is expected?
5. Can a later reviewer reconstruct which version governed a contested decision?

## Compression rule for the archive

When a public rule changes, ask:

**Could an outsider tell what changed, when it changed, and how long everyone had to adapt?**

If not, the change process is still too opaque.
