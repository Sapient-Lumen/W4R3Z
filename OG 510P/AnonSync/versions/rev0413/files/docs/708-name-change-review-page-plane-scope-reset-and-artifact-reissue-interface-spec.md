# Name change review page: plane, scope, reset, and artifact reissue interface spec

## Purpose

This page exists for the moment when an operator is not asking about names in the abstract.
They are changing a concrete label and need one answer:

> which plane am I changing, who will see it, what stays untouched, and do I also need reset, regenerate, or reissue work so the visible world stays honest?

## Core decision

Every serious sync product must own one first-class **Name change review** page.
That page is the semantic home of:

- requested plane mutation
- audience/scope preview
- unchanged planes
- residue consequences
- artifact freshness impact
- allowed next actions
- post-decision receipt plan

## Fixed page order

The page always renders the same sections in the same order:

1. requested name mutation strip
2. affected-plane card
3. audience/scope matrix
4. reset and reissue consequences
5. allowed decisions
6. receipt preview

### 1) Requested name mutation strip

Show:

- subject and seat
- requested plane
- requested value
- review verdict: `safe-local-only`, `safe-with-artifact-reissue`, `safe-with-reset`, `mixed-plane-risk`, `insufficient-proof`, `unknown`
- one next honest action

### 2) Affected-plane card

Show whether the request changes:

- subject title
- local UI title
- on-disk basename
- outward artifact label
- peer-visible alias

The operator must be able to answer: **what exactly is being renamed?**

### 3) Audience/scope matrix

Rows should include each plane above.
For each row show:

- current value
- post-change value
- audience/scope
- change class: `changed`, `unchanged`, `stale-until-reissue`, `reset-required`, `unknown`
- consequence class: `local-only`, `outward-label-shift`, `disk-path-shift`, `residue-risk`, `needs-regeneration`

### 4) Reset and reissue consequences

Show what extra work is required, such as:

- reset local title to baseline
- regenerate QR / outward artifact
- reissue outward invitation with fresh label
- rename disk path separately
- keep plane separation and do nothing else

The operator must be able to answer: **what else must happen so the change is true everywhere it claims to be true?**

### 5) Allowed decisions

Allowed decisions may include:

- `change this plane only`
- `change plane and regenerate outward artifact`
- `reset residue first`
- `rename disk path separately`
- `keep names separate and explain why`
- `block mixed-plane rename`

Each decision preview must disclose:

- continuity impact
- scope of visibility
- whether any stale outward artifact remains

### 6) Receipt preview

Show what the name receipt will preserve:

- changed plane
- unchanged planes
- reset requirement if any
- artifact freshness result
- strongest safe sentence

## Guardrails

The page must never:

- imply a local UI rename changed the disk path when it did not
- imply an outward artifact label is fresh if reissue/regeneration is still pending
- hide residue under generic `renamed` language
- let one click silently span several name planes without review

## Success criteria

The page is successful only when an operator can answer:

1. what exact plane was changed
2. who will see the changed name
3. what planes remain untouched
4. whether reset or reissue is still required
5. what claim ceiling follows from the chosen decision
