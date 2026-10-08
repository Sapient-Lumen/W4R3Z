# Bind choice review page — this share vs seat default and suggested root interface spec

## Purpose

Give the operator one reviewed answer to:

- what path is being proposed for **this share**
- whether the proposal came from a seat default, remembered bind, restored path, or manual draft
- whether the operator is changing only this share or also rewriting future defaults
- what byte and collision consequences follow from each choice

This page is the bind-decision companion to `622-future-arrival-defaults-page-scope-default-root-and-manual-bind-right-interface-spec.md` and the continuity companion to `158-adopt-rebind-reconnect-and-pre-existing-path-repair-interface-spec.md`.

## Inputs

- share identifier
- seat identifier
- continuity class (`first-bind`, `reconnect`, `rebind`, `repair`, `unknown`)
- current-share bind truth (`announced-only`, `claimed-unbound`, `previously-bound`, `bound-elsewhere`, `unknown`)
- suggested path
- suggestion source (`seat-default-root`, `remembered-bind`, `reconnect-restoration`, `manual-draft`, `policy-template`, `unknown`)
- whether applying the choice changes seat defaults
- candidate byte effect
- collision class
- strongest safe sentence
- stronger forbidden sentence
- available next actions

## Primary questions this page must answer

1. Why is this path being suggested for this share?
2. Am I deciding only this share or also tomorrow's arrivals?
3. What happens to current bytes, placeholders, or missing local material after apply?
4. What collision or adoption review still stands in the way?
5. What is the most truthful primary action here?

## Layout

### A. Bind verdict strip

Fields:

- share label
- seat label
- continuity class
- suggested path
- suggestion source
- strongest safe sentence

Example verdicts:

- `Reconnect candidate for Projects-2026: suggested path /srv/incoming/Projects-2026 comes from seat default, not from the last reviewed bind.`
- `First bind for Photos-2026: suggested path /Users/alex/Pictures/Photos-2026 comes from remembered family root; future defaults remain unchanged.`

### B. Current-share card

Show:

- whether the share is only announced, claimed-unbound, or previously bound
- whether this is a first bind, restore, or repair
- whether any remembered prior path exists

### C. Suggestion-source card

Show:

- suggested path
- source of suggestion
- strength of that source (`strong`, `helpful draft`, `weak guess`, `unknown`)
- why the product picked this candidate over others

The operator must be able to answer: `why this path?`

### D. This-share-vs-future-default card

Show together:

- whether applying this bind affects only the current share
- whether the seat default stays untouched
- if a checkbox or side action would also update future defaults, show it as a clearly separate mutation
- strongest safe sentence about scope

This card exists so one-share placement does not silently mutate device posture.

### E. Byte-effect card

Show:

- expected starting byte posture after bind
- whether files arrive as placeholders, partial bytes, or full bytes
- whether existing local bytes are adopted, compared, or left untouched pending review
- whether current bytes differ from future default suggestions

### F. Candidate-outcomes card

Show only honest actions:

- `Bind at suggested path`
- `Choose alternate path`
- `Compare and adopt existing directory`
- `Keep announced only`
- `Keep claimed but unbound`
- `Also update future default` (separate secondary mutation)

Each action should show scope and byte effect in one line.

### G. Claim-ceiling card

Show together:

- strongest approved sentence
- stronger forbidden sentence
- blocker basis

Example:

- approved: `Binding this share at /srv/projects/Projects-2026 leaves future arrivals unchanged.`
- forbidden: `This bind also updates the seat's default projects root.`
- blocker basis: `no standing-default mutation selected`

## Compact row contract

A truthful compact bind-review row should preserve this order:

1. share
2. continuity class
3. suggested path
4. suggestion source
5. scope of effect
6. next honest action

Example:

```text
Projects-2026    reconnect    /srv/incoming/Projects-2026    source: seat default    affects: this share only    Review bind
```

## Success criteria

A good page lets a later operator answer:

1. why this path was suggested
2. whether the decision changes only this share or also future defaults
3. what byte posture follows from the bind
4. what compare/adoption blocker remains
5. what exact action was reviewed and approved
