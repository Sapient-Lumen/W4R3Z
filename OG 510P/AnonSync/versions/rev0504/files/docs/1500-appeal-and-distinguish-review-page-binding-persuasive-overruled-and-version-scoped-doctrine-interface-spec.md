# Appeal and distinguish review page: binding, persuasive, overruled, and version-scoped doctrine interface spec

## Purpose

After the archive learned how to attach precedent dockets, it still needed one ordinary workspace for the next harder question:

> should this earlier ruling actually govern the new case, should we distinguish it, or should we overrule or sunset it because the facts, version, or world changed too much?

## Core decision

AnonSync must expose one first-class **Appeal and distinguish review** page whenever precedent weight is being materially affirmed, narrowed, distinguished, overruled, or sunset.

## Fixed page order

1. **Review header**
2. **Precedent stack card**
3. **Distinguishing-facts card**
4. **Version-drift card**
5. **Appeal gate card**
6. **Proposed doctrine verdict card**
7. **Decision sentence**

### 1) Review header

Show:

- review id
- current case id
- active precedent dockets reviewed
- review owner
- current doctrine risk level
- current strongest safe sentence

Supported `doctrine_risk_level` values:

- `low-consistency-risk`
- `moderate-consistency-risk`
- `high-overrule-risk`
- `unknown-doctrine-risk`

### 2) Precedent stack card

For each attached precedent, show:

- source ruling id
- binding weight
- source version window
- source world scope
- current status
- why it was attached

Hard rule:

The page must support more than one precedent at once.
Operators should not have to compare doctrine one article at a time.

### 3) Distinguishing-facts card

Required rows:

- facts common to all attached precedents
- facts distinguishing the current case
- facts that weaken only some precedents
- facts still unresolved
- disputed distinction claims

Hard rule:

A distinction must name the fact that does the doctrinal work.
`This one feels different` is not enough.

### 4) Version-drift card

Required rows:

- version or release drift since each source ruling
- world or lane drift since each source ruling
- later fixes or wording changes already known
- whether drift weakens, leaves intact, or supersedes old doctrine
- strongest blocked sentence because drift remains unresolved

Hard rule:

Later fixes or warning-text changes cannot remain implicit.
If doctrine changed because the product changed, the review must say so.

### 5) Appeal gate card

Required rows:

- who may uphold doctrine as-is
- who may distinguish locally
- who may overrule or sunset doctrine
- burden needed for overrule
- burden needed for emergency exception
- whether interim hold is allowed

Hard rule:

Not every reviewer may overrule doctrine.
The page must publish the gate.

### 6) Proposed doctrine verdict card

Supported `doctrine_verdict` values:

- `apply-binding-doctrine`
- `apply-presumptive-doctrine`
- `treat-as-persuasive-only`
- `distinguish-current-case`
- `narrow-existing-precedent`
- `overrule-existing-precedent`
- `sunset-existing-precedent`
- `create-new-precedent`
- `issue-interim-hold`

Required rows:

- proposed doctrine verdict
- exact scope affected
- who must be notified
- downstream case impact
- stronger allowed sentence if accepted
- stronger blocked sentence if rejected

Hard rule:

The verdict must name whether old doctrine survives, narrows, or dies.
A review may not quietly resolve the current case without updating doctrine state.

### 7) Decision sentence

Render one sentence only:

- `This review currently [doctrine_verdict] for [scope], based on [distinguishing fact or drift], and leaves [blocked sentence] unsafe until finalized.`

## Required interactions

- **Compare attached precedents side by side**
- **Mark material distinction**
- **Downgrade precedent weight**
- **Open overrule path**
- **Issue interim hold**
- **Finalize doctrine verdict**

## Failure and edge states

If all attached precedents are only informative, show:

- `No attached precedent currently binds this case. Create new doctrine or proceed with local case-only reasoning.`

If version drift is unresolved, show:

- `Doctrine comparison incomplete: product drift may have changed the meaning of the older ruling.`
