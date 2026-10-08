# 415 — Phase-labeled public automation lifecycles

## One-line thesis

Public automated systems should never drift through hidden stages. They should carry an explicit **lifecycle phase label** — such as pre-deployment, beta or pilot, production, paused, or retired — with different evidence, visibility, and approval requirements at each phase.

## Why this matters

A common public-sector failure pattern is phase ambiguity:

- a “pilot” quietly becomes operational dependence,
- a production system keeps changing without a new approval moment,
- a retired system lingers in service contracts and workflows,
- a registry lists a tool but not whether it is still experimental, consequential, paused, or dead.

Recent official practice is already pointing the other way. Public inventories and transparency records are increasingly distinguishing whether systems are pre-deployment, in beta or pilot, in production, or retired. That distinction matters because the acceptable evidence for a prototype is not the acceptable evidence for live public dependence.

## Design rule

Every public automated system should have a visible lifecycle state and explicit transition rules. The minimum working state model is:

- **pre-deployment** — being built, tested, or evaluated without live consequential dependency,
- **beta/pilot** — used in bounded live conditions with explicit limits,
- **production** — relied on in normal operations,
- **paused** — temporarily stopped while issues are investigated or corrected,
- **retired** — no longer in live use, but historically documented.

The public record should show the current state, the last state change date, the responsible organisation, and the evidence needed for the next transition.

## Pattern pack

### 1. Use lifecycle labels as governance labels, not product jargon

Do not let “pilot”, “beta”, or “production” remain informal team language. In public governance, those words should indicate:

- what kind of public exposure exists,
- what evidence has been reviewed,
- what level of sign-off is required,
- what claims may be made about readiness,
- what remedial options are already in place.

### 2. Give each phase a different evidence burden

Require different artifacts at different stages.

For example:

- **pre-deployment** should require problem definition, intended purpose, test design, and known limits;
- **beta/pilot** should require bounded scope, rollback conditions, human fallback, and explicit learning goals;
- **production** should require stable operating ownership, public documentation, incident routing, and updated risk evidence;
- **paused** should require a reason code, review path, and restart criteria;
- **retired** should require the retirement date, archival retention rules, and migration notes if a successor exists.

### 3. Publish phase changes as first-class events

A system moving from pilot to production is not just a technical update. It is a governance transition. Treat it as a distinct event that triggers:

- record updates,
- renewed internal clearance,
- refreshed public explanations,
- operational readiness confirmation,
- changed expectations about reliability and remedy.

### 4. Keep “paused” visible

Official taxonomies often emphasise pre-deployment, pilot, deployed, and retired. Public operators should add **paused** as a visible status instead of forcing every interruption into either “production” or “retired”. A paused label lets the public distinguish between:

- stable ongoing service,
- active rollback or investigation,
- permanent decommissioning.

That makes incident command legible rather than internal.

### 5. Treat retirement as a state, not disappearance

Retired systems should remain visible in registries and inventories for historical accountability. Otherwise the archive forgets:

- what systems actually existed,
- which tool made which class of decision,
- whether old outputs are still being relied upon,
- how often tools were replaced, merged, or quietly abandoned.

### 6. Mark legacy public systems before compliance deadlines arrive

Where legal obligations phase in over time, public authorities should not wait until the last deadline to find old systems. Legacy tools should be marked early, especially when later legal review or applicability dates are already known.

### 7. Let inventories and transparency records interoperate on phase

Deployment registries, transparency records, procurement continuity records, and incident logs should all be able to align on the same lifecycle state. That makes it possible to answer simple but crucial questions:

- how many systems are still experimental,
- which pilots affect the public,
- which tools are paused under review,
- what was retired and what replaced it.

## Guardrails

- Keep the phase model short enough that outsiders can understand it.
- Do not let “pilot” become a euphemism for live use without production controls.
- Require dates for phase transitions, not just labels.
- Do not delete retired records unless law requires it.
- Where a system is paused, publish what sort of restart evidence is needed.

## Failure modes

- **pilot laundering**: a consequential system stays in “pilot” language to dodge stronger controls.
- **production by drift**: a tool becomes relied upon without any explicit promotion decision.
- **retirement amnesia**: the public record loses track of old systems and their historical effects.
- **status flattening**: everything is either “live” or “not live”, hiding investigation states.
- **deadline panic**: legacy public systems are discovered only when a statutory date arrives.

## Practical tests

A lifecycle regime passes when it can answer yes to all of the following:

1. Does every listed system have a current phase label?
2. Are phase transitions dated and explainable?
3. Is moving from pilot to production treated as a governance event rather than a silent rollout?
4. Can the public distinguish between paused and retired systems?
5. Are legacy systems visible early enough to prepare for later review and compliance obligations?

## Compression rule for the archive

Before trusting any public automation record, ask:

**What phase is this system in, what changed at the last phase transition, and what evidence will be required for the next one?**

If there is no crisp answer, the system is already too invisible.
