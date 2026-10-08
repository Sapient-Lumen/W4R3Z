# Meta: Evidence renewal protocol (rev0428)

## Purpose
Use this protocol when a revision is primarily about **refreshing, narrowing, degrading, superseding, or retiring** existing canon claims rather than promoting a new seam.

The goal is simple:
- keep the archive's strongest claims fresh enough to trust,
- avoid silent evergreen prose,
- and avoid overreacting to one new source by rewriting the whole ladder.

Pair with:
- `design/portfolio-evidence-renewal-2026Q1.md`
- `meta/CANONICAL_RENEWAL_QUEUE.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Required renewal card
Every serious renewal should leave a compact card with these fields.

### A) Identity
- note or file renewed;
- prior revision;
- current revision;
- renewal date;
- reviewer / steward class.

### B) Claim shape
- primary claim class: structural / substrate / service-behavior / security-incident / ecosystem-tooling;
- authority lane: docs / goals-updates / hosted-service docs / maintainer docs / survey / mixed;
- drift horizon: hot / warm / cool / cold.

### C) Trigger
At least one of:
- calendar review;
- official upstream change;
- incident/advisory;
- contradiction found;
- adjacent note changed;
- steward challenge / user confusion.

### D) Sources re-checked
List the strongest sources actually re-opened.
Do not say "refreshed" if you only re-read your own old prose.

### E) Outcome
Exactly one primary verdict:
- **confirmed**
- **narrowed**
- **degraded**
- **superseded**
- **retired**

Optional secondary tags:
- wording-only
- scope-shift
- urgency-up
- urgency-down
- source-moved
- service-default-changed
- security-model-changed

### F) Material change summary
State:
- which claim stayed intact;
- which claim narrowed or weakened;
- what the repo should now say differently;
- and whether any adjacent note now carries the stronger current argument.

### G) Follow-up posture
- next review horizon;
- explicit trigger that should force earlier review;
- any open residue.

## Verdict definitions
### Confirmed
Use when the claim still holds substantially as written.
Minor citation updates or wording cleanup are fine.
Do not call something confirmed if a key scope assumption got smaller.

### Narrowed
Use when the broad seam still holds but some present-tense support got smaller, more conditional, or more lane-specific.
This should be the default verdict when the note remains useful but should make fewer confident claims.

### Degraded
Use when the note is still worth keeping, but it should carry less argumentative weight until fresher evidence appears.
Typical examples:
- annual survey claim used as a live service claim;
- formerly current goal no longer clearly active;
- ecosystem-tooling comparison older than the current surface.

### Superseded
Use when a newer note or stronger source should now be the canonical entry point.
Leave a pointer.
Do not silently strand readers on the weaker note.

### Retired
Use when the claim should stop guiding current decisions.
Keep historical context if useful, but mark it as no longer current.

## Default drift horizons
### Hot
Review within weeks or on visible upstream motion.
Typical notes:
- service-behavior claims;
- security-sensitive seams;
- current goals / active roadmap arguments;
- recommendation/default notes that lean on live ecosystem status.

### Warm
Review roughly quarterly or when adjacent substrate shifts.
Typical notes:
- execution blueprints with active upstream dependencies;
- pilot evaluations tied to current machine-usable evidence.

### Cool
Review semiannually or on contradiction.
Typical notes:
- portfolio grammar;
- sequencing;
- selection rubric.

### Cold
Review mainly when the broad ladder or frontier is reconsidered.
Typical notes:
- taxonomy-heavy foundational notes;
- broad ladder synthesis whose support comes from many slower-moving signals.

## Minimum repo updates for a renewal revision
If a revision's primary class is renewal, update at least:
- `INDEX.md`
- `PRIORITIES.md`
- `STRATEGIC_FRONTIER.md`
- `RESEARCH_LOG.md`
- `AGENTS.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

Also update:
- the renewed note itself;
- this protocol if the process changed;
- `meta/CANONICAL_RENEWAL_QUEUE.md` if review priorities shifted.

## Anti-patterns
Do **not**:
- quietly swap citations without saying whether the conclusion changed;
- keep saying "current" after checking no current source;
- rewrite the broad ladder because one service default changed;
- treat a security advisory as permanent evergreen proof without revisiting residual scope;
- or let assistant summaries outlive the canonical evidence they summarized.

## Default interpretation rule after rev0428
A good renewal revision should make it easier to answer:
- what still holds strongly,
- what narrowed,
- what is aging,
- what has fresher support elsewhere,
- and what should be retired.

If it cannot answer those cleanly, it is probably just an edit pass, not real renewal discipline.
