# Architecture — rev0145

## Boundary

Lacuna is an event-sourced semantic custody layer. It validates and records epistemic transitions, then materializes queryable projections. It does not choose prose or optimize a plot.

```text
external model / author / simulator
              |
        JSON change-set
              v
       validation + refusal
              |
       immutable event ledger  <---- verify hash chain
              |
       deterministic projector <---- rebuild
              v
 claims | assertions | worlds | questions | evidence
              |
 canon / perspective / unknowns / conflicts / context
```

## Storage

Each cube is a directory:

```text
cube.json          stable cube identity and format declaration
lacuna.sqlite3     events, change-set receipts, and projections
```

SQLite is configured with foreign keys, WAL journaling, a busy timeout, and full synchronous durability. A change-set runs inside one immediate transaction.

## Temporal model

Lacuna distinguishes two temporal axes:

- **ledger time**: immutable event sequence and UTC `recorded_at`—when the system learned or recorded something;
- **narrative valid time**: `timeline_id`, `valid_from`, and `valid_to`—when the assertion or assignment is meant to hold inside the represented world.

That prevents “we learned at scene 20 that the door had been open at scene 4” from collapsing into a single timestamp.

Intervals are inclusive. `null` means unbounded. Assertions on different timelines do not conflict merely because their ticks overlap.

## Core entities

### Agent

A human, character, narrator, model, tool, system, organization, or other epistemic actor.

### Source

A scene, utterance, document, sensor reading, user statement, model output, tool output, or other evidence-bearing object. A source may include a locator and content digest.

### Claim

A content-addressed neutral proposition:

```text
(subject, predicate, canonical JSON object, scope)
```

The deterministic claim ID makes duplicate propositions converge. Scope is `world`, `event`, `belief`, or `meta`.

### Assertion

A stance toward a claim, with:

- assertor;
- perspective holder;
- optional source;
- `true`, `false`, or `unknown` stance;
- basis: observation, testimony, inference, belief, hypothesis, commitment, or metadata;
- standing: reported, accepted, or anchored;
- confidence;
- visibility and audience;
- narrative validity interval;
- optional supersession.

`standing` is intentionally independent from `confidence`: a highly confident rumor is still a rumor; an irrevocable observed event may be anchored without claiming metaphysical certainty about its hidden cause.

### Candidate world

A named, weighted hypothesis with a status:

- `live` — still under consideration;
- `selected` — favored for current planning but not made global truth;
- `pruned` — rejected from active consideration;
- `archived` — retained but inactive.

A world may fork from another. Current implementation copies the parent's active assignments into the child as inherited records, preserving lineage.

### World assignment

A world-local stance toward a claim, plus commitment class:

- `tentative`;
- `soft`;
- `firm`;
- `hard`.

Commitment is metadata for policy and future revision-cost logic. In rev0145, only anchors are enforced globally; the graded commitment ladder is exposed but not yet governed by a numeric revision budget.

### Evidence link

A typed relation from an assertion to a target claim, optionally within a candidate world: supports, refutes, explains, or contextualizes. The same observed evidence may support different explanations in different worlds without being rewritten. Evidence-link interpretation is privileged planner state in rev0145 and is omitted from perspective-scoped context packets. Superseding the supporting assertion ends its active evidence links while retaining their ledger history.

### Open question

An explicit unresolved issue, optionally attached to a claim, with the same visibility discipline as assertions. Closure may reference a resolving assertion. When a question names a claim, its resolving assertion must concern that same claim.

## Events and projections

Every accepted operation becomes one event. The event hash covers sequence, IDs, actor, timestamp, payload, and previous hash. The ledger head is the last event hash.

Projection tables are disposable. `lacuna rebuild` first performs a ledger-only verification, then deletes and deterministically recreates agents, sources, claims, assertions, worlds, assignments, evidence, and questions from ledger events. This permits repair when a projection is corrupt but the event/change-set custody chain is valid. A final full verification checks the rebuilt state. Change-set receipts and the event ledger remain authoritative.

## Change-set protocol

A change-set contains:

- schema identifier;
- unique change ID;
- registered actor;
- expected ledger head;
- optional message;
- one to 1,000 operations.

Validation and projection occur inside one transaction. Any invalid operation rolls back the complete change-set. A stale head is refused before semantic mutation.

## Canon projection

The `canon` view contains two deliberately different sets:

1. active anchored assertions;
2. nontrivial truth assignments shared by every live or selected candidate world over the same claim and interval.

Cross-world consensus is useful but is not silently promoted to an anchor. A later branch may reopen it.

## Perspective projection

An agent sees:

- public assertions and questions;
- assertions they hold or made;
- their own questions;
- restricted records naming them in the audience.

Private records belonging only to another agent do not leak into the projection. A perspective-scoped context packet also omits candidate worlds, cross-world consensus, invisible claims, and hidden conflicts. The unscoped context is explicitly privileged.

## Conflict projection

The verifier treats broken hard invariants as failures. The `conflicts` view also reports softer epistemic tensions, such as opposing active accepted assertions or disagreement among live worlds. Tension is not corruption.

## Enforced invariants in rev0145

- event sequence is contiguous and hash-linked;
- cube identity agrees across config and database;
- foreign keys and SQLite integrity hold;
- deterministic claim identity is respected;
- IDs are bounded and typed;
- supersession remains within one claim;
- restricted visibility requires an audience;
- anchors cannot carry `unknown`;
- anchors cannot be superseded in-place;
- overlapping anchors cannot oppose each other;
- live worlds cannot oppose overlapping anchors;
- new anchors cannot invalidate a live world without explicit prior revision;
- pruned or archived worlds cannot receive assignments;
- change-sets are atomic and stale-head protected;
- unrecognized change-set and operation fields are refused rather than ignored;
- event groups and change receipts agree on count, actor, time, and before/after heads;
- question resolutions match the claim explicitly named by the question;
- superseded evidence assertions end their active evidence links.

## Deliberate nonclaims

Rev0145 does not yet provide:

- digital signatures or hostile-host tamper resistance;
- normalized world weights;
- Bayesian updating;
- automatic hypothesis generation;
- automatic contradiction extraction from free text;
- ontology or schema migration machinery;
- branch merge;
- distributed consensus;
- access-control security beyond projection discipline;
- commitment-budget enforcement;
- counterfactual simulation.

Those are roadmap candidates, not hidden promises.
