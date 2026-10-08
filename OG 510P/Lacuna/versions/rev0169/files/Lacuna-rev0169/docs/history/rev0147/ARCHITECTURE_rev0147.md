# Architecture — rev0147

## System boundary

Lacuna is an event-sourced epistemic custody kernel with thin entrances for humans, models, and auditors.

```text
human                           language model / external director
  |                                           |
campaign library                    source-bound turn request
  |                       audience view + optional planner view
selected campaign                              |
  |                                   least-authority proposal
  +-------------------+-----------------------+
                      v
            adapter normalization
 aliases + grant enforcement + disclosure preflight + source digests
                      |
                JSON change-set
                      v
             validation + refusal
                      |
           immutable event ledger
                      |
          deterministic projections
                      v
 agents | sources | claims | relations | assertions | worlds | evidence | questions
                      |
       context | canon | conflicts | unknowns | explanation
```

Generation, model hosting, plot scoring, logical closure, and dramatic policy remain outside the kernel. The turn adapter does not call a model. It provides a source-backed contract by which a model or human can propose one mutation.

## Three custody layers

### Immutable story events

Every semantic mutation is an event with sequence, change-set identity, actor, timestamp, payload, previous hash, and event hash. Events remain schema version 1 in rev0147.

### Deterministic projections

SQLite tables provide current queryable state. They may be deleted and replayed from the event stream. Rev0147 adds the `claim_relations` projection.

### Database schema custody

Physical schema version is independent from event schema. Rev0147 moves the database to schema 2 and adds `schema_migrations`. A migration changes projection/storage structure, records a migration digest, and must leave the event head byte-for-byte unchanged.

## Human-facing storage

### Cube

```text
cube.json
lacuna.sqlite3
```

### Campaign

```text
campaign.json
cube.json
lacuna.sqlite3
```

`campaign.json` names the campaign and records default owner, player, and narrator IDs. It is mutable application metadata, not event-sourced story state.

### Library

```text
lacuna-library.json
campaigns/
  campaign-slug/
    campaign.json
    cube.json
    lacuna.sqlite3
```

The library’s selected campaign is a user-interface preference. Every normal cube-opening command accepts either a cube path or a library path with an active selected campaign.

## Semantic model

### Claims and assertions

A claim is neutral content. An assertion is a perspective-bearing stance toward that claim. Multiple agents can disagree without corrupting the ledger.

### Candidate worlds

A world stores explicit truth assignments as one latent explanation. Worlds may branch, diverge, receive weights, be selected for planning, or be pruned. None is global truth merely because it is selected.

### Claim relations

A relation is a first-class, sourced, rationale-bearing constraint between two distinct claims:

```text
excludes    reject true / true
negates     reject equal known values
entails     reject left=true / right=false
equivalent  reject unequal known values
```

`unknown` never causes a relation violation. Relations check compatibility only. They do not write inferred endpoint assignments.

Symmetric relation endpoints are canonicalized for stable duplicate detection. Relations can be retired additively; their origin and termination remain queryable.

### Temporal consistency

Contradiction checks operate only where narrative intervals overlap on the same timeline. One consistency engine is used for:

- new anchored assertions;
- assignments inside a live/selected world;
- reactivation of a world;
- declaration of a new relation against existing live state;
- conflict reporting and verification.

An exact-interval world assignment may replace the active assignment it supersedes through ordinary event application. Partially overlapping opposite assignments are refused.

## Constraint versus closure

Lacuna stores authored facts and constraints. It does not silently compute a closed theory.

For example:

```text
A entails B
A = true
```

is compatible but does not create `B = true`. A future closure engine may compute that consequence as a labelled, inspectable projection with provenance to the rule and premises. It may not pass the consequence off as an original observation or assertion.

This is essential for epistemic safety: compatibility policy can prune a candidate world without pretending an agent observed the logical consequence or that the consequence has been deliberately committed.

## Context projection

One structured builder feeds both JSON and Markdown renderers.

Two access modes exist:

- **perspective** — visible assertions, questions, anchors, and visible tensions for one agent;
- **planner** — privileged assertions, relations, candidate worlds, world-scoped evidence, consensus, and unresolved state.

A perspective context and a named candidate world are mutually exclusive. A director turn receives two separately labelled projections. Claim relations are omitted from perspective packets because they can reveal hidden world design even when their endpoint claims are visible.

## Turn boundary

Opening a turn is itself a one-event mutation. Lacuna commits an input source containing:

- exact player-input SHA-256;
- request, proposal, actor, audience, narration-source, and optional world IDs;
- access mode and least-authority write grant;
- base head and issue time;
- an explicit marker that the input body was not retained.

The packet’s `expected_head` is the hash after this source event. A `lacuna.turn-proposal.v2` must echo all source-bound identity fields and the input digest.

At commit, Lacuna:

1. resolves and verifies the request source against its original one-event change receipt;
2. checks the proposal’s expected head;
3. expands sequential aliases and generates explicit IDs;
4. validates declared disclosure symmetry;
5. enforces the immutable write grant, anchor authority, audience visibility, and optional world scope;
6. prepends a narration source containing the exact prose digest;
7. applies the complete semantic delta atomically through the ordinary kernel;
8. returns narration, receipt, bindings, new head, and refreshed contexts.

Text inside player input, planner context, or narration cannot widen the write grant.

## Custody explanation

`explain` resolves one ID across record namespaces and returns:

- normalized target record;
- access mode;
- event that created it;
- event that ended it, when applicable;
- direct structural dependencies;
- direct structural dependents;
- an explicit nonclaim that custody is not proof.

Planner access may inspect all supported records. Perspective access refuses relations, worlds, assignments, evidence links, events, and change receipts, and applies normal visibility checks to assertions, questions, claims, and sources.

This query is deliberately one hop. It is groundwork for revision-cost analysis, not yet a theorem prover or complete causal graph.

## Database migration

`Cube.open` refuses a schema-1 database with `database-migration-required`. `Cube.migrate` supports only coherent schema 1 → 2:

1. verify cube identity, SQLite integrity, and foreign keys;
2. begin an immediate transaction;
3. create relation and schema-migration structures;
4. update schema metadata and `PRAGMA user_version`;
5. record runtime version and migration-statement digest;
6. commit;
7. assert that ledger head before and after is identical.

Old event envelopes are not rewritten or relabelled.

## Invariants added or repaired in rev0147

- Two overlapping opposite assignments to one claim cannot coexist in one world.
- Active relations constrain anchors and all live/selected worlds.
- A relation cannot be introduced when it would retroactively invalidate active committed state.
- Retiring a relation preserves declaration custody and projection replay.
- `unknown` has no closed-world effect.
- Relations appear only in privileged planner context.
- Custody explanations obey perspective visibility.
- Database and event schema versions are independent.
- Schema migration is explicit and ledger-head preserving.
- Turn proposals are source-bound v2 objects with immutable grants.

## Deliberate nonclaims

- Relations do not express exactly-one, at-least-one, arbitrary formulas, probabilities, or natural-language semantics.
- `explain` does not prove truth, relevance, fairness, or transitive causation.
- The runtime does not choose candidate worlds, assign posterior weights, or score story quality.
- Narration and player-input digests are not transcript archives.
- A selected campaign or selected world is not canon.
