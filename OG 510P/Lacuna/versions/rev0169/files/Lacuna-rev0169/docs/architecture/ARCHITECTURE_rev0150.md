# Architecture — rev0150

## System boundary

Lacuna is an event-sourced epistemic custody kernel for adaptive worlds. It records observations, assertions, beliefs, candidate-world assignments, constraints, commitments, explicit consequences, revisions, repairs, and unresolved questions without collapsing them into one mutable canon paragraph.

```text
human / campaign CLI                    external model / director
          |                                         |
          |                              narration + typed proposal
          +---------------------+-------------------+
                                v
                      protocol normalization
       aliases | grants | visibility preflight | exchange schemas
                                |
                         atomic change-set
                                v
                       validate or refuse
                                |
                      immutable event ledger
                                |
                 deterministic SQLite projections
                                v
 agents | sources | claims | assertions | worlds | assignments | questions
 relations | cardinalities | commitments | consequences | repair lineage
                                |
 contexts | reviews | explanations | conflicts | receipts | snapshots
```

The cube does not call a model, retain transcript bodies, generate prose, search plots, resample worlds, infer causality from chronology, or choose a winning hidden world. Those are host/planner responsibilities.

## The rev0150 repair loop

Rev0149 made nonbinding consequence debt visible when a premise or dependent ended. Rev0150 makes that debt repairable without deleting history or pretending dependency transfers automatically.

```text
active consequence C0
        |
        v
consequence-repair-review at change-set base head H
        |
        +--> lifecycle state
        +--> known explicit assignment/assertion successors
        +--> blockers
        +--> digest R = sha256(review core)
        |
        v
replace_consequence(expected_repair_sha256=R)
        |
        +--> validate predecessor is active and unreplaced
        +--> validate successor endpoints are currently active
        +--> refuse semantic no-op or duplicate active edge
        +--> cycle-check the post-replacement assignment graph
        |
        v
one atomic consequence.replaced event
        |
        +--> end C0 at sequence S
        +--> create successor C1 at sequence S
        +--> create repair record C0 --repair--> C1 at sequence S
```

The predecessor remains queryable. The successor does not inherit truth by implication; the operation is an authored claim that the old dependency custody is being replaced by this new dependency custody.

## Review receipts and atomic base heads

High-impact review receipts are bound to the **base head of the atomic change-set**, not mechanically to the head after every earlier operation in the same transaction.

That gives the turn adapter a safe and useful property:

```text
review at head H
turn commit expected_head = H
  1. add narration source
  2. apply reviewed replacement
```

The source event does not by itself invalidate the review. Validation still recomputes the review from the transaction's current projected state while substituting base head `H` into the digest. Therefore:

- a separately committed event after `H` makes the receipt stale;
- an earlier operation in the same atomic change-set that alters the review's target or dependency footprint changes the recomputed digest and is refused;
- a benign provenance operation in the same transaction may coexist with the reviewed mutation;
- the entire change-set still succeeds or fails atomically.

This rule is shared by `revise_world` and `replace_consequence`.

## Consequence custody model

A consequence link is a directed authored dependency:

```text
world assignment --relation/severity--> assertion | world assignment | question
```

Relations are `causes`, `explains`, `discloses`, `motivates`, `promises`, and `constrains`. Severities are `notice`, `material`, and `binding`.

### Lifecycle

A consequence may be:

- **original** — active or retired without replacement lineage;
- **replaced** — predecessor ended by a replacement event;
- **replacement** — successor created by a replacement event;
- **middle** — a successor that was itself later replaced;
- **retired** — explicitly ended without a replacement successor.

Rev0150 deliberately supports one predecessor and one successor per repair. Repeated repairs form a chain. Split and merge repair are deferred because they need a different review and cardinality contract.

### Active endpoint rule

New links and replacement successors may target only:

- an active premise world assignment;
- an active dependent assertion;
- an active dependent world assignment; or
- an open dependent question.

This closes a lifecycle defect in which new custody could be born already orphaned. Historical links may remain orphaned after an endpoint later ends; that is repair debt, not invalid projection state.

### Post-replacement graph validation

For assignment-to-assignment links, cycle detection evaluates the graph that would exist **after** removing the predecessor edge and adding the successor edge. Testing against the pre-repair graph would incorrectly refuse valid edge reversals where the predecessor is precisely the edge being replaced.

## Review does not select the successor

`consequence_repair_review` exposes known explicit successors in assignment-revision or assertion-supersession lineages. They are candidates for human or planner attention. They are not auto-selected, ranked, or certified as semantically equivalent.

The replacement operation independently validates the authored successor. This keeps three claims distinct:

1. a predecessor endpoint has a recorded successor;
2. a planner chooses to bind a new consequence to some active endpoint;
3. the new dependency is narratively or causally justified.

Lacuna records the first two. It does not prove the third.

## Event and projection additions

Database schema advances to 5 while immutable event schema remains 1.

New event type:

```text
consequence.replaced
```

New projection:

```text
consequence_repairs
  repair_id
  predecessor_consequence_id  UNIQUE
  successor_consequence_id    UNIQUE
  reason
  review_sha256
  created_seq
```

The verifier binds each projection row back to its originating `consequence.replaced` event and detects replacement events missing a repair projection. Projection rebuild recreates predecessor ending, successor creation, and repair lineage from the event ledger.

Schema 1, 2, 3, or 4 migrates through the ordered chain to schema 5 without changing the event-ledger head.

## Context and explanation boundary

### Planner context

Privileged planner context may contain:

- consequence links and lifecycle diagnostics;
- immutable replacement lineage;
- a `consequence_repair_frontier` of current repair-required links with digest-bound review receipts.

This allows a director turn to consume a review already embedded in its packet. When opening a turn adds the immutable request source, the adapter recomputes the embedded receipt against the turn's new base head because that source addition does not alter epistemic projections.

### Perspective context

Audience context structurally omits consequence links, repair lineage, and repair-frontier receipts. It does not return redacted IDs or counts. A perspective explanation for a repair record is refused.

### Explanations

Planner explanations expose:

```text
repair -> predecessor consequence
repair -> successor consequence
predecessor <- replaced_by repair
successor <- created_by_repair repair
```

These are provenance edges, not causal derivations.

## Human and model entrances

All entrances converge on the same operation and event path.

### Human CLI

```text
consequence-repair-review
consequence-repair-frontier
consequence-replace
consequence-repairs
```

A human may inspect the debt-only frontier, inspect one review, author a successor, supply the exact digest, and receive an atomic receipt.

### Direct Python

Applications may call `Cube.consequence_repair_frontier` or `Cube.consequence_repair_review`, submit `replace_consequence` through `apply_changeset`, and query `consequence_repairs`. Repair queries include the origin event/change identity and the receipt-derived reviewed base head.

### Director turn

A privileged packet may include repair-frontier receipts. The model or human director returns narration plus typed operations. Alias normalization generates both a successor consequence ID and a distinct repair ID when omitted. The narration source and replacement commit in one atomic change-set.

### Read-only audience

Ordinary audience packets never receive repair internals. The host may narrate an accepted visible consequence through separately authorized assertions, but the hidden repair graph is not disclosed automatically.

## Invariants introduced or strengthened

- A consequence replacement requires a digest-bound review.
- A separately committed intervening event makes the review stale.
- Earlier operations in the same atomic change-set are evaluated against one shared base head and current projected state.
- A predecessor may have at most one replacement successor.
- A successor may originate from at most one replacement repair.
- Replacement ends the predecessor, creates the successor, and records lineage at one event sequence.
- New consequence custody cannot target an already-ended assignment/assertion or closed question.
- Replacement must change an endpoint or recorded semantic field.
- An equivalent active edge cannot be duplicated.
- Assignment-cycle validation uses the post-replacement graph.
- Repair projections must agree with their immutable origin events.
- The event-recorded repair review head must equal the origin change receipt's base head.
- Repair digest serialization is shared by review issuance and turn-packet rebinding.
- The repair frontier contains actual lifecycle debt, not every semantically revisable link.
- Repair lineage rebuilds deterministically.
- Repair data and receipts do not cross the perspective firewall.
- Database schema 1/2/3/4 migration to schema 5 preserves the event-ledger head.

## Deliberate nonclaims

- Replacement is not rollback and does not restore a prior universe.
- Replacement does not prove that predecessor and successor are semantically equivalent.
- A known endpoint successor is not an automatic destination for a consequence.
- Repair lineage does not prove physical causality, artistic quality, player agency, or fairness.
- The review digest authorizes inspection against recorded state; it does not authorize every possible candidate successor semantically.
- One-to-many and many-to-one repair are not represented in rev0150.
- Lacuna does not automatically repair chains, infer dependencies from prose, or generate the narration that explains a repair.
