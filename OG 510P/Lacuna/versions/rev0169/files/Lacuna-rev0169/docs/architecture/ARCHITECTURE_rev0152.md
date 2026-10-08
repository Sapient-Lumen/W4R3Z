# Architecture — rev0152

## Architectural thesis

Lacuna is an epistemic custody kernel, not a storyteller and not a monolithic world simulator. It stores typed claims about what happened, who observed or believes what, which hidden-world hypotheses remain live, how those hypotheses are constrained, what later records explicitly depend on them, and which planning weights have been changed by which evidence factors.

Rev0152 adds the first governed plural-world evidence update while preserving rev0151 fair-play seals and rev0150 consequence repair. The central architecture is now:

```text
immutable events
      ↓ deterministic replay
semantic projections
      ↓ access policy
human / host / model views
      ↓ typed reviewed proposal
atomic validation + append or refusal
```

Narrative prose is presentation. Semantic mutation happens only through accepted typed operations.

## Boundary diagram

```text
player / human author / external LLM / game engine
                    │
                    │ turn request, change set, host command
                    ▼
        ┌───────────────────────────────┐
        │ entrances                    │
        │ campaigns · CLI · Python     │
        │ turn packets · JSON schemas  │
        └──────────────┬────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │ authority + validation        │
        │ strict fields · aliases       │
        │ visibility · stale receipts  │
        │ world/constraint invariants  │
        │ particle completeness        │
        └──────────────┬────────────────┘
                       │ append or refuse
                       ▼
        ┌───────────────────────────────┐
        │ immutable custody             │
        │ events · changesets · hashes │
        │ schema migrations             │
        └──────────────┬────────────────┘
                       │ deterministic replay
                       ▼
        ┌───────────────────────────────┐
        │ projections                   │
        │ claims · assertions · worlds │
        │ constraints · commitments    │
        │ consequences · seals         │
        │ particle updates · questions │
        └──────────────┬────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
      audience context    planner context
      visibility-safe     hidden-world capable
```

The host owns model invocation, transcript retention, physical simulation, secret-file custody, and presentation policy. Lacuna owns the typed custody and refusal boundary.

## Storage layers

### Immutable event ledger

`events` is an append-only, SHA-256-linked sequence. Every event includes:

- sequence and event identity;
- change-set identity;
- event type and event-schema version;
- actor and recorded timestamp;
- canonical JSON payload;
- previous hash; and
- event hash.

`changesets` records atomic request custody: actor, message, expected/base head, resulting head, operation count, time, and payload digest.

The local chain is mutation-evident when verified. It is not a signature, trusted timestamp, transparency service, or hostile-host fork detector.

### Replayable projections

SQLite tables for agents, sources, claims, relations, cardinalities, assertions, worlds, assignments, commitments, evidence links, consequences, repairs, seals, particle updates, and questions are projections. They can be deleted and rebuilt from events.

Verification binds each projection row to its origin event, checks event/projection parity, and recomputes domain invariants. Projection corruption is repairable; event corruption is an audit failure.

### Database migration custody

Database schema evolves independently from event schema. Rev0152 uses database schema 7 and event schema 1.

Schema migration:

- is explicit;
- records deterministic step digests in `schema_migrations`;
- validates physical shape and integrity;
- preserves the story event-ledger head; and
- refuses ambiguous or unowned state.

The rev0151 schema-number collision and 6→7 repair are documented in [`../protocols/SCHEMA_LINEAGE.md`](../protocols/SCHEMA_LINEAGE.md).

### Campaign library

A campaign library is an outer human entrance. It maps a slug, title, and summary to one cube and records which campaign is selected. Campaign metadata is not canon and is not inserted into the story ledger.

## Epistemic model

### Claims are content, not truth

A claim is a neutral proposition. Assertions attach stance, assertor, perspective, source, basis, standing, confidence, visibility, and temporal interval. Declaring a claim asserts nothing.

### Unknown is first-class

An absent assignment and explicit `unknown` are not false. Pairwise relations and cardinality bounds reject impossible explicit partial valuations but do not manufacture unstored closure.

### Candidate worlds are partial hypotheses

A candidate world contains explicit assignments, status, weight, parent lineage, and rationale. Several worlds may disagree. `selected` means planning preference, not global canon.

Assignments occupy one no-clobber slot defined by world, claim, timeline, and exact interval. Changing truth creates a governed successor; it never overwrites the predecessor.

### Commitment governs mutation

Assignment commitments progress through `tentative → soft → firm → hard`. Raises are adjacent, monotone, event-backed, and basis-custodied. Commitment is not confidence and hard is not cross-world canon.

### Consequences record authored dependence

A consequence link is an explicit directed edge from an assignment to an assertion, assignment, or question. It is authored custody, not discovered physics. Binding edges block revision. Softer edges can survive endpoint revision as visible repair debt and be replaced through digest-reviewed predecessor→successor lineage.

### Fair-play seals bind selected openings

A fair-play seal stores a salted commitment digest and public/restricted metadata. Payload and nonce remain outside the cube until reveal. The stable receipt core can be retained or externally anchored. A seal proves exact-opening continuity under its assumptions, not truth, uniqueness, authorship, trusted time, clue sufficiency, or fairness.

## Governed particle bank

### Why plural worlds need a separate weight layer

World assignments express what a hypothesis says. World weights express how much current planning attention it receives. Conflating the two would make a numerical preference become truth.

The particle bank is a deterministic planner projection over all `live` and `selected` worlds. It normalizes raw weights, fingerprints explicit valuations and custody, groups duplicate valuations, and reports concentration diagnostics.

### Fingerprints

A valuation fingerprint contains only active proposition tuples:

```text
claim_id, truth, timeline_id, valid_from, valid_to
```

A custody fingerprint additionally contains assignment identity, commitment, provenance, confidence, inheritance, and revision lineage.

The bank digest binds world identity, status, raw weight, valuation fingerprint, and custody fingerprint for the complete population.

### Evidence update flow

```text
active evidence assertion
          +
complete current bank receipt
          +
one likelihood per member
          │
          ▼
validate exact coverage + fresh digest + single-use factor
          │
          ▼
q_i ∝ p_i × likelihood_i
          │
          ▼
particle.updated event
          │
          ▼
weights + immutable per-world calculation projection
```

The update changes weights only. It cannot create, delete, select, prune, merge, resample, assign, anchor, or reveal a world.

### Single-use factor custody

The same evidence assertion cannot be applied twice. A unique database index and operation-level refusal prevent accidental double multiplication.

If applied evidence is later superseded, the historical event remains. The current bank reports **reweighting debt** rather than silently unapplying or recomputing it. This preserves history while exposing that the current weight vector no longer has a clean active-factor interpretation.

### Why reweighting is not resampling

Sequential Monte Carlo often interleaves reweighting, resampling, and mutation. Lacuna deliberately implements only governed reweighting in rev0152. Resampling can delete minority hypotheses, duplicate ancestry, and create new candidate custody; it requires a separate event type, review receipt, diversity policy, and lineage representation.

## Access architecture

### Audience context

Perspective context includes only records visible to a named agent. It structurally omits:

- candidate worlds and weights;
- particle update IDs, rationales, diagnostics, and debt;
- cross-world consensus;
- constraints and their derived conflicts;
- consequence/revision governance;
- privileged evidence interpretation;
- hidden source topology; and
- unrevealed restricted records.

This is not planner context with fields redacted after construction. It is a separately constructed projection.

### Planner context

Unscoped planner context contains the complete candidate population, particle bank, recent update custody, constraints, consequences, revision guards, and repair frontier.

World-scoped planner context intentionally omits the global particle bank and update history. Normalizing a filtered subset would create a false probability surface.

### Model turn authority

A turn packet records the player-input digest and an immutable least-authority operation grant before model output. Director mode adds a separately labelled planner view. An unscoped director may propose a complete-bank update; a world-scoped director may not.

Fair-play seal custody remains host-only even in director mode.

## Human and model entrances

The same kernel is reachable through:

- human CLI commands;
- strict JSON change sets;
- turn request/proposal envelopes for external LLMs;
- direct Python methods;
- campaign-library selection; and
- read-only status, context, explanation, snapshot, and verification surfaces.

The executable can therefore be used by a ChatGPT-like host that returns narration to the player and separately commits or displays the latest semantic receipt. Lacuna itself does not invoke the model.

## Verification architecture

`verify` checks, among other things:

- event sequence, previous hash, and event hash;
- change receipt contiguity and head custody;
- database schema shape and migration digests;
- foreign keys and SQLite integrity;
- origin-event binding for replayable projections;
- claim, interval, relation, and cardinality invariants;
- assignment revision and commitment chains;
- consequence cycles, repair lineage, and debt;
- fair-play seal lifecycle and reveal digests;
- particle update arithmetic, numeric finiteness, membership ordering, bank digests, and factor uniqueness; and
- perspective-safe explanation access.

`rebuild-projections` clears projection tables in dependency order and replays every event. It does not rewrite events or repair a corrupt ledger.

## Exchange contracts

Strict Draft 2020-12 schemas cover:

- cube and campaign metadata;
- change sets;
- turn requests and proposals;
- fair-play openings and receipts.

The runtime also performs field-exact validation so behavior does not depend on an optional JSON Schema library.

`update_particle_bank` is present in both the change-set operation union and turn-proposal operation registry. Nested world aliases are resolved before mutation.

## Executable boundary

The bundled `./lacuna` launcher runs local source with `python3 -S`, preventing ambient site packages and `sitecustomize` hooks from silently entering the zero-dependency runtime boundary.

This narrows dependency custody. It is not an operating-system sandbox.

## Deliberately external

Rev0152 leaves these outside the kernel:

- LLM vendor calls and credentials;
- prose generation and entailment scoring;
- dramatic or thematic optimization;
- transcript-body hosting;
- physical game simulation;
- automatic world proposal, resampling, merging, or winning-world selection;
- calibrated likelihood estimation;
- factor retraction and posterior recomputation;
- causal-agency and counterfactual simulation;
- external signatures, witnesses, and transparency logs;
- secret storage before seal reveal; and
- deployment, cloud orchestration, and self-building machinery.

The boundary is a feature: Lacuna should make a host's epistemic decisions inspectable without pretending to be the entire creative system.
