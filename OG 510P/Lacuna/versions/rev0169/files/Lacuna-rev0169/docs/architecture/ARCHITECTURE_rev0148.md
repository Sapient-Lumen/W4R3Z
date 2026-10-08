# Architecture — rev0148

## System boundary

Lacuna is an event-sourced epistemic custody kernel. It gives humans, models, and game hosts one governed place to record what is fixed, what is merely asserted, what hidden explanations remain possible, and which explicit combinations are impossible.

```text
human campaign entrance                 external model / director
          |                                      |
   selected cube                         source-bound turn packet
          |                         audience view || planner view
          +-------------------+------------------+
                              v
                    protocol normalization
          aliases | immutable grants | disclosure preflight
                              |
                     atomic change-set
                              v
                   validation or refusal
                              |
                   immutable event ledger
                              |
                  deterministic projection
                              v
 agents | sources | claims | relations | cardinalities | assertions
 worlds | assignments | evidence | questions | migration custody
                              |
 context | canon | unknowns | conflicts | explanations | snapshots
```

Generation, model invocation, plot scoring, world resampling, transcript hosting, and full logical closure remain outside the kernel.

## Custody layers

### Immutable event ledger

Every semantic mutation is recorded as an event with sequence, change identity, actor, timestamp, payload, previous hash, and event hash. Rev0148 retains event schema 1. New event types are additive:

```text
cardinality.declared
cardinality.retired
```

### Deterministic semantic projections

SQLite tables provide current queryable state. They can be deleted and rebuilt from events. Rev0148 adds:

```text
cardinality_constraints
cardinality_members
```

The member table preserves stable canonical ordering and claim foreign keys. Retirement ends the constraint projection but does not delete its member custody.

### Physical schema custody

Database schema advances from 2 to 3 while event schema remains 1. `Cube.migrate` accepts coherent schema 1 or 2 databases and applies the required ordered steps in one transaction:

```text
1 -> 2 -> 3
2 ------> 3
```

Each step records its migration digest. The event-ledger head must be byte-for-byte identical before and after migration.

## Semantic model

### Claims and assertions

A claim is neutral proposition content. An assertion records a stance by an assertor for a perspective, with source, basis, standing, confidence, visibility, audience, and narrative validity interval.

### Candidate worlds

A candidate world is one explicit partial hidden-world valuation. Worlds may remain incomplete, disagree, branch, receive weights, be selected for planning, or be pruned. Selection is not canonization.

### Pairwise relations

`excludes`, `negates`, `entails`, and `equivalent` constrain pairs of explicit assignments. They remain non-inferential.

### Cardinality constraints

A cardinality constraint bounds the number of true claims in an explicit member set:

```text
min_true <= true_count <= max_true
```

The evaluator is open-world:

- missing and `unknown` values remain unresolved;
- an upper violation needs too many explicit truths;
- a lower violation needs so many explicit falsehoods that no completion can satisfy the minimum;
- no forced value is stored.

Exactly-one is therefore a rejection rule over impossible partial valuations, not a mechanism that fills the final blank.

## Consistency architecture

Pure compatibility functions live in `logic.py`:

- pairwise relation orientation and violation;
- cardinality descriptions;
- deterministic temporal cardinality witnesses.

The store invokes them from all state transitions that can affect integrity:

- new anchors;
- new/replacement world assignments;
- relation or cardinality declaration;
- world reactivation;
- conflict reporting;
- full verification.

A constraint declaration is refused if it would retroactively invalidate anchors or any live/selected world. A retired constraint is ignored by current validation while remaining replayable history.

## Temporal evaluation

Every record belongs to a timeline and has an inclusive validity interval. Constraint evaluation is timeline-local and tests deterministic interval boundary points. A returned witness includes a representative violating tick and the intersection of the selected witness records.

Candidate worlds are isolated from one another. Evaluation uses:

```text
anchors alone
anchors + assignments in each one world
```

It never combines assignments from different worlds into a synthetic contradiction.

## Context firewall

One structured context builder feeds JSON and Markdown.

### Perspective mode

Includes only visible assertions, visible anchors, questions, visible unknowns, and conflicts that can be computed without hidden ontology. It explicitly omits:

- candidate worlds;
- cross-world consensus;
- evidence-link interpretation;
- pairwise relation definitions;
- cardinality definitions;
- all relation- or cardinality-derived conflict diagnostics.

Rev0148 closes a diagnostic side channel: omitting a constraint definition is insufficient if a conflict record still reveals that a hidden relation or group exists.

### Planner mode

Includes the full active constraint ontology, worlds, evidence links, consensus, unsettled state, and invariant/attention diagnostics.

Perspective mode and a named world remain mutually exclusive. A director packet contains separately labelled audience and planner projections rather than one widened object.

## Turn boundary

The source-bound v2 turn contract remains unchanged at the envelope level. Director grants automatically include the two new operations because they are ordinary kernel mutations.

Alias normalization is refactored into scalar-reference and list-reference registries. `claim_ids` in `declare_cardinality` may contain sequential `@alias` references, just like audience lists may contain agent aliases. Forward references remain refused.

The proposal is normalized, grant-checked, disclosure-checked, and committed through the same atomic event path as a human-authored change-set.

## Human entrance

Campaign libraries remain application metadata around real cubes. New CLI surfaces are:

```text
cardinalities
cardinality-add
cardinality-retire
```

`context`, `snapshot`, `status`, `conflicts`, `explain`, `verify`, and `rebuild` all understand the new constraint type.

## Invariants added or repaired in rev0148

- Set-level lower, upper, exact, and ranged bounds are first-class custody records.
- Unknown members never acquire truth through closure.
- Constraints apply across anchors and each live/selected world.
- New constraints cannot retroactively corrupt active state.
- Pruned worlds must pass current constraints before reactivation.
- Violations report deterministic temporal custody witnesses.
- Constraint definitions and derived diagnostics do not leak through perspective context.
- List-valued alias references use the same general normalization path.
- Schema-1 and schema-2 cubes migrate to schema 3 without ledger rewriting.
- Constraint declaration, retirement, replay, explanation, snapshot, CLI, context, and schemas are covered by executable tests.

## Deliberate nonclaims

- Lacuna is not a general constraint solver.
- It does not compute logical closure, quantified membership, or probabilities.
- It does not decide which constraint should exist or whether the author is fair.
- It does not choose a winning hidden world or generate narration.
- Constraint witnesses are incompatibility evidence, not proof of objective fictional truth.
