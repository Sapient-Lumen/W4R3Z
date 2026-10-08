# Explicit consequence links

## Purpose

A consequence link records one authored dependency claim whose premise is a latent-world assignment. It exists because proximity is not causality and because a revision engine needs to know which downstream records were deliberately built on a premise.

## Shape

```text
world assignment --relation/severity--> assertion | world assignment | question
```

Every link stores:

- stable consequence ID;
- active premise assignment;
- typed dependent ID;
- relation;
- severity;
- optional source;
- rationale;
- creation and optional retirement custody;
- optional predecessor/successor repair lineage.

## Relations

| Relation | Intended use |
|---|---|
| `causes` | the premise produces the dependent state/event claim |
| `explains` | the premise is an authored explanation for the dependent |
| `discloses` | the dependent exposes information about the premise |
| `motivates` | the premise gives a character/question/action its reason |
| `promises` | the premise establishes a future-facing audience or author promise |
| `constrains` | the premise limits which dependent state is acceptable |

These names are semantic custody supplied by an author or planner. Lacuna does not discover or prove them.

## Severities

| Severity | Revision effect |
|---|---|
| `notice` | included in review burden |
| `material` | stronger review burden; surviving endpoint debt is prominent |
| `binding` | blocks revision until retired or otherwise repaired |

Severity is policy. A host may require human approval for material links even though the kernel does not block them.

## Create and inspect

```bash
./lacuna consequence-link CUBE asn_hidden question qst_why \
  motivates \
  --severity material \
  --consequence-id csq_hidden_motivates_question \
  --rationale "The investigation exists because this hypothesis was adopted."

./lacuna consequences CUBE
```

## Assignment graph discipline

When the dependent is another world assignment, active links form a directed acyclic graph. A proposed self-loop or cycle is refused atomically with a deterministic cycle witness. Replacement checks the graph after excluding the predecessor edge, because that edge ends in the same transaction.

The graph is bounded during revision impact traversal. If depth or node limits are reached, the impact is incomplete and revision is blocked rather than pretending the unseen remainder is safe.

## Endpoint lifecycle and repair debt

A consequence is not silently deleted when its premise or dependent ends. Query output includes:

- `premise_active`;
- dependent lifecycle state;
- `dependent_active`;
- `repair_required`.

The conflict projection emits `orphaned-consequence` attention records. This is not a database corruption: it is unresolved semantic custody.

Repair options include:

1. retire the obsolete link with a reason;
2. request a digest-bound repair review and atomically replace it with a custodied successor;
3. preserve the debt deliberately for later author review.

A replacement is not ordinary `retire` plus `link`. It emits one event that ends the predecessor, creates the successor, and records an identified one-to-one repair relation. See [`CONSEQUENCE_REPAIR.md`](CONSEQUENCE_REPAIR.md).

```bash
./lacuna consequence-retire CUBE csq_hidden_motivates_question \
  --reason "The question was reframed and no longer depends on the old premise."
```

## Why links are not inferred

A same-claim assertion, a nearby scene, an open question, or a shared timestamp may increase revision exposure. None automatically becomes a consequence. Automatic linking would encourage paranoid overfitting in which every atmospheric detail becomes a clue.

## Access boundary

Consequence links are planner-only. Perspective context omits the link ontology and all IDs. Perspective-scoped explanations also omit links to privileged records, preventing hidden-world structure from leaking through an otherwise visible assertion or source.

## Verification invariants

`verify` checks:

- premise and dependent existence;
- recognized kinds, relations, and severities;
- nonnegative custody intervals;
- uniqueness of active equivalent links;
- cycle freedom for active assignment-to-assignment edges;
- one-to-one repair lineage and shared sequence boundaries;
- repair/event payload agreement and missing repair projections.

## Nonclaims

- A link is not a proof of physical causality.
- `binding` does not mean metaphysically irreversible.
- Retirement does not erase the historical dependency claim.
- An orphaned link is an explicit repair obligation, not automatic evidence that the successor inherits it.
- Replacement lineage records authorship; it does not prove predecessor/successor equivalence.
