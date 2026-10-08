# Architecture — rev0149

## System boundary

Lacuna is an event-sourced epistemic custody kernel for interactive worlds. It records the difference between observation, assertion, belief, hidden-world hypothesis, commitment, explicit consequence, and unresolved possibility. It does not generate prose or decide which story is best.

```text
human campaign / CLI                    external model / director
          |                                        |
          |                              narration + typed proposal
          |                                        |
          +--------------------+-------------------+
                               v
                     protocol normalization
            aliases | grants | visibility preflight | schemas
                               |
                        atomic change-set
                               v
                    validation or refusal
                               |
                    immutable event ledger
                               |
                  deterministic SQLite projection
                               v
 agents | sources | claims | assertions | worlds | assignments | questions
 relations | cardinalities | commitments | consequences | migration custody
                               |
 context | impact reviews | explanations | conflicts | receipts | snapshots
```

Model invocation, transcript hosting, plot search, dramatic scoring, world resampling, semantic parsing of prose, and release automation remain outside the cube.

## The rev0149 control loop

A hidden-world assignment no longer changes by occupying the same slot again. Revision is an explicit protocol:

```text
inspect active assignment
        |
        v
revision-impact at ledger head H
        |
        +--> blockers? hard commitment / binding consequence / bounded traversal
        |        |
        |        +--> fork, repair, or retire explicit custody
        |
        v
submit revise_world with exact impact digest and expected head H
        |
        v
append world.revised event
        |
        v
end predecessor and create successor with lineage, reason, and review digest
```

Any intervening ledger event changes the head and invalidates the review digest. This is intentionally conservative: a revision decision is authorized against one inspectable state, not a moving target.

## Four kinds of pressure

Rev0149 separates pressures that were previously easy to blur.

### 1. Commitment

Each active assignment carries one level:

```text
tentative -> soft -> firm -> hard
```

A raise crosses exactly one boundary and emits a `world.commitment_raised` event plus a `commitment_transitions` projection row. Lowering is not an in-place operation. Changing assigned truth creates a revision successor; a hard assignment requires a fork or explicit custody repair.

Commitment bases are `legacy`, `planning`, `authored`, `evidence`, `disclosure`, and `precommitment`. Hard assignments require a durable basis. Evidence and disclosure bases require a source. The labels record policy custody; they do not prove that evidence is sound or that a precommitment is cryptographically valid.

### 2. Ambient exposure

`revision_impact` surveys records near the target assignment:

- overlapping public, restricted, and private assertion history;
- active anchors;
- evidence links involving the claim;
- open questions;
- pairwise and cardinality constraints;
- inherited live descendants;
- agreement across live worlds.

This footprint is conservative proximity. It does **not** assert causality.

### 3. Explicit consequence

A `consequence_link` is an authored, directed claim from one world assignment to an assertion, another world assignment, or a question. Relations are `causes`, `explains`, `discloses`, `motivates`, `promises`, and `constrains`; severities are `notice`, `material`, and `binding`.

Only explicit links make dependency claims. Active assignment-to-assignment links must remain acyclic. A binding incident link blocks revision. Notice and material links increase review burden but do not block; if their premise or dependent ends, they remain visible repair obligations until explicitly retired or relinked.

### 4. Revision burden

The impact report emits a transparent ordinal score over recorded custody. It has named components and a policy identifier. The score is not a probability, utility, causal proof, quality metric, or fairness certificate.

## Event and projection additions

Database schema advances to 4 while immutable event schema remains 1.

New event types:

```text
world.revised
world.commitment_raised
consequence.linked
consequence.retired
```

New or extended projections:

```text
world_assignments
  commitment_basis
  commitment_source_id
  revision_of_assignment_id
  revision_reason
  revision_impact_sha256

commitment_transitions
consequence_links
```

A schema-1, schema-2, or schema-3 cube is migrated through the ordered chain to schema 4 without changing the event-ledger head.

## Candidate worlds remain plural

Lacuna does not compress all ambiguity into one winning state card. Multiple live worlds may disagree. A selected world is a planning preference, not canon. Revision changes one assignment in one world; it does not silently rewrite all alternatives.

World forks and assignment revision serve different purposes:

- **fork** when alternatives should continue to coexist, or when hard custody prevents mutation;
- **revise** when one active hypothesis is deliberately corrected while preserving lineage and downstream repair debt.

## Explanation noninterference

Record-level `explain` has two access modes.

Planner mode may return full target records, dependency/dependent IDs, and raw custody events. Perspective mode is a separate projection, not a redacted planner object. It now enforces visibility on every returned link and emits only safe event envelopes.

Perspective mode refuses worlds, world assignments, commitment transitions, consequence links, evidence links, constraints, events, and changes. It also:

- removes source locators and metadata;
- removes agent metadata;
- hides invisible supersession and resolution IDs;
- omits links to any privileged or invisible record;
- omits raw event payloads and change IDs.

This closes the rev0148 side channel where a visible assertion could disclose a hidden world or consequence merely through a dependent identifier.

## Human and model entrances

### Human

A campaign library selects one real cube. The CLI supports inspection, planning, revision review, consequence repair, and verification. Humans can run the two-step revision protocol directly.

### Model or ChatGPT host

A host opens a source-bound turn packet containing audience context and, only when authorized, a separately labelled planner context. The model returns:

1. presentation text;
2. typed operations and declared disclosures.

The cube validates and either returns a structured refusal or commits the operations and returns receipts plus updated projections. The executable can therefore be wielded as a deterministic tool inside a chat session without becoming the model host itself.

### Direct application integration

Applications may call `Cube` methods directly, invoke the CLI as a subprocess, or build a transport adapter such as MCP around the same packets and receipts. All entrances converge on the same atomic event path.

## Invariants introduced or strengthened

- `assign_world` cannot silently replace an occupied active slot.
- Every truth-changing revision cites a current-head impact digest.
- Revision preserves predecessor, successor, reason, interval, world, claim, and digest custody.
- Commitment raises are adjacent and monotone.
- Hard commitment requires durable basis and blocks in-place revision.
- Binding incident consequences block revision.
- Notice and material consequences remain explicit repair debt when endpoints end.
- Active assignment consequence links are cycle-free.
- Ambient exposure is never promoted into an implicit causal edge.
- Perspective explanations cannot leak privileged IDs through links, ancestry, or event payloads.
- Schema 1/2/3 migration to schema 4 preserves the event-ledger head.
- Projection rebuild reproduces governed revision and consequence state.

## Deliberate nonclaims

- Lacuna does not determine whether a revision is artistically wise.
- Burden is not an empirical estimate of player surprise or harm.
- A consequence link is authored policy, not discovered causality.
- A hard commitment is not necessarily irreversible in the universe; it means this world must fork or its custody must be explicitly repaired.
- The kernel does not automatically transfer consequences from an ended predecessor to its successor.
- The kernel does not invoke an LLM, parse prose entailment, or select a winning world.
