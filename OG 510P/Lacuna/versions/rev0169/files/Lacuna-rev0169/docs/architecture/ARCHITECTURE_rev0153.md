# Architecture — rev0153

## Architectural thesis

Lacuna is an epistemic custody kernel, not a storyteller and not a monolithic world simulator. It stores typed claims about what happened, who observed or believes what, which hidden-world hypotheses remain live, how those hypotheses are constrained, what later records explicitly depend on them, and which planning weights have been changed by which evidence factors.

Rev0153 adds governed factor-ledger reconciliation: current particle weights can be rebuilt from an immutable epoch baseline after supporting evidence is withdrawn, without deleting the original updates. Rev0152 evidence reweighting, rev0151 fair-play seals, and rev0150 consequence repair remain intact. The central architecture is now:

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
        │ particle updates/repairs    │
        │ questions                     │
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

SQLite tables for agents, sources, claims, relations, cardinalities, assertions, worlds, assignments, commitments, evidence links, consequences, repairs, seals, particle updates, particle reconciliations, and questions are projections. They can be deleted and rebuilt from events.

Verification binds each projection row to its origin event, checks event/projection parity, and recomputes domain invariants. Projection corruption is repairable; event corruption is an audit failure.

### Database migration custody

Database schema evolves independently from event schema. Rev0153 uses database schema 8 and event schema 1.

Schema migration:

- is explicit;
- records deterministic step digests in `schema_migrations`;
- validates physical shape and integrity;
- preserves the story event-ledger head; and
- refuses ambiguous or unowned state.

The rev0151 schema-number collision, 6→7 repair, and additive 7→8 reconciliation migration are documented in [`../protocols/SCHEMA_LINEAGE.md`](../protocols/SCHEMA_LINEAGE.md).

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

## Governed particle bank and factor ledger

### Plural state remains separate from planning attention

World assignments express what a hypothesis says. World weights express how much current planning attention it receives. Conflating them would make a numerical preference become truth.

The particle bank is a deterministic planner projection over all `live` and `selected` worlds. It normalizes raw weights, fingerprints explicit valuations and custody, groups duplicate valuations, and reports concentration diagnostics.

### Fingerprints and complete denominator

A valuation fingerprint contains only active proposition tuples:

```text
claim_id, truth, timeline_id, valid_from, valid_to
```

A custody fingerprint additionally contains assignment identity, commitment, provenance, confidence, inheritance, and revision lineage.

The bank digest binds world identity, status, raw weight, valuation fingerprint, and custody fingerprint for the complete population. Both evidence updates and reconciliations are refused from a filtered or stale denominator.

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
weights + immutable per-world factor receipt
```

The update changes weights only. It cannot create, delete, select, prune, merge, resample, assign, anchor, or reveal a world.

### Immutable factor custody

The same evidence assertion cannot be applied twice. A unique database index and operation-level refusal prevent accidental exact duplicate multiplication.

Each update records its complete prior and posterior transition, evidence assertion, member likelihoods, status/fingerprint custody, and distribution diagnostics. It is a historical action, not a mutable row in a current belief table.

### Reweighting debt

When applied evidence is later superseded, the old update remains historically true but the current weight vector no longer has a clean active-factor interpretation. The bank marks that factor `reconciliation-required` and reports reweighting debt.

Structural changes begin a new factor epoch and retire older factors from current replay responsibility. This prevents stale likelihoods from crossing changed world membership, valuation, custody, status, or authored prior.

### Factor-ledger reconciliation

```text
latest structural boundary
          +
first update's immutable prior snapshot
          +
all update receipts in the epoch
          +
active/superseded evidence state at the reviewed head
          │
          ▼
deterministic complete review
          │
          ├─ included active factors
          ├─ excluded ended factors
          ├─ log-space posterior
          ├─ per-world arithmetic
          └─ head-bound digest
          │
          ▼
particle.reconciled event
          │
          ▼
new current weights + immutable repair custody
```

The reconciliation baseline is reconstructed from the first update after the latest event that can change the particle population or authored prior:

- `world.created`;
- `world.assigned`;
- `world.revised`;
- `world.commitment_raised`;
- `world.weight_set`; or
- `world.status_set`.

Every factor after that boundary is selected mechanically from assertion state at the review head. Active evidence is included. Ended evidence is excluded but preserved. Factors before the boundary remain historical and are labelled `epoch-retired`.

Positive weights are replayed in log space and normalized with a max-shifted log-sum-exp calculation. This can recover positive relative mass lost only to sequential floating-point underflow. Zero baseline mass or an explicit zero likelihood remains extinguished.

The reconciliation event binds:

- structural boundary and baseline update;
- baseline, pre-repair current, and posterior bank digests;
- ordered factor dispositions and factor-set digest;
- log normalization, ESS, entropy, information gain, and total variation;
- complete per-world base/current/posterior arithmetic;
- review digest and base head; and
- authored reason.

### Why reconciliation is not rollback

`particle.updated` is never deleted or edited. `particle.reconciled` is a later fact about which factors remain authorized and what the derived distribution becomes after replay. Event history retains both the old decision and the new reason-maintenance decision.

### Why reweighting and reconciliation are not resampling

Sequential Monte Carlo often interleaves reweighting, resampling, and mutation. Lacuna deliberately implements only governed reweighting and deterministic factor replay. Resampling can delete minority hypotheses, duplicate ancestry, and create new candidate custody; it requires a separate event type, review receipt, diversity policy, and lineage representation.

See [`../protocols/PARTICLE_BANK.md`](../protocols/PARTICLE_BANK.md) and [`../protocols/FACTOR_LEDGER_RECONCILIATION.md`](../protocols/FACTOR_LEDGER_RECONCILIATION.md).

## Access architecture

### Audience context

Perspective context includes only records visible to a named agent. It structurally omits:

- candidate worlds and weights;
- particle update/reconciliation IDs, rationales, diagnostics, factor dispositions, and debt;
- cross-world consensus;
- constraints and their derived conflicts;
- consequence/revision governance;
- privileged evidence interpretation;
- hidden source topology; and
- unrevealed restricted records.

This is not planner context with fields redacted after construction. It is a separately constructed projection.

### Planner context

Unscoped planner context contains the complete candidate population, particle bank, recent update custody, current factor-ledger reconciliation review, recent reconciliation custody, constraints, consequences, revision guards, and repair frontier.

World-scoped planner context intentionally omits the global particle bank, update history, reconciliation review, and reconciliation history. Normalizing or repairing a filtered subset would create a false probability surface.

### Model turn authority

A turn packet records the player-input digest and an immutable least-authority operation grant before model output. Director mode adds a separately labelled planner view. An unscoped director may propose a complete-bank update or factor-ledger reconciliation; a world-scoped director may do neither.

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
- particle update arithmetic, numeric finiteness, membership ordering, bank digests, and factor uniqueness;
- reconciliation boundaries, historical factor selection, log-space replay, review digests, per-world arithmetic, and projection completeness; and
- perspective-safe explanation access.

`rebuild-projections` clears projection tables in dependency order and replays every event. It does not rewrite events or repair a corrupt ledger.

## Exchange contracts

Strict Draft 2020-12 schemas cover:

- cube and campaign metadata;
- change sets;
- turn requests and proposals;
- fair-play openings and receipts.

The runtime also performs field-exact validation so behavior does not depend on an optional JSON Schema library.

`update_particle_bank` and `reconcile_particle_bank` are present in both the change-set operation union and turn-proposal operation registry. Nested world aliases are resolved before mutation.

## Executable boundary

The bundled `./lacuna` launcher runs local source with `python3 -S`, preventing ambient site packages and `sitecustomize` hooks from silently entering the zero-dependency runtime boundary.

This narrows dependency custody. It is not an operating-system sandbox.

## Deliberately external

Rev0153 leaves these outside the kernel:

- LLM vendor calls and credentials;
- prose generation and entailment scoring;
- dramatic or thematic optimization;
- transcript-body hosting;
- physical game simulation;
- automatic world proposal, resampling, merging, or winning-world selection;
- calibrated likelihood estimation;
- semantic factor correction/replacement and dependence modeling;
- causal-agency and counterfactual simulation;
- external signatures, witnesses, and transparency logs;
- secret storage before seal reveal; and
- deployment, cloud orchestration, and self-building machinery.

The boundary is a feature: Lacuna should make a host's epistemic decisions inspectable without pretending to be the entire creative system.
