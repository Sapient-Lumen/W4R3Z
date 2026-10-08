# Consequence repair protocol

## Purpose

A consequence link may remain active after its premise or dependent ends. That is deliberate repair debt: deleting the link loses history, while silently moving it to a successor invents dependency. This protocol lets an authorized human or planner replace one consequence with one reviewed successor atomically.

## Objects

A repair creates three durable records from one event sequence:

```text
predecessor consequence  --ended by repair-->  successor consequence
                         \-- repair record --/
```

The repair record stores its own ID, predecessor ID, successor ID, authored reason, review digest, and creation sequence.

## Phase 1: review

CLI:

```bash
./lacuna consequence-repair-frontier CUBE [--world-id WORLD]
./lacuna consequence-repair-review CUBE csq_old > /tmp/repair-review.json
```

The frontier contains only active repair debt; healthy links remain reviewable explicitly but are not suggested for replacement.

Python:

```python
review = cube.consequence_repair_review("csq_old")
```

The `lacuna.consequence-repair-review.v1` response contains:

- cube ID and digest head;
- complete current predecessor semantics and lifecycle diagnostics;
- active descendants in explicit assignment-revision or assertion-supersession lineages;
- blockers;
- repair mode: `orphan-repair` or `semantic-replacement`;
- `repair_review_sha256`.

The review does not choose an endpoint, assert equivalence, or prove causality.

## Phase 2: replace

CLI:

```bash
./lacuna consequence-replace CUBE \
  csq_old asn_premise_v2 world_assignment asn_dependent constrains \
  --consequence-id csq_new \
  --repair-id cpr_old_to_new \
  --severity material \
  --rationale "The revised premise now constrains the same live dependent." \
  --expected-repair-sha256 DIGEST_FROM_REVIEW \
  --reason "Replace dependency custody after premise revision."
```

Typed operation:

```json
{
  "op": "replace_consequence",
  "repair_id": "cpr_old_to_new",
  "consequence_id": "csq_new",
  "replaces_consequence_id": "csq_old",
  "premise_assignment_id": "asn_premise_v2",
  "dependent_kind": "world_assignment",
  "dependent_id": "asn_dependent",
  "relation": "constrains",
  "severity": "material",
  "source_id": null,
  "rationale": "The revised premise now constrains the same live dependent.",
  "expected_repair_sha256": "<64 lowercase hex characters>",
  "reason": "Replace dependency custody after premise revision."
}
```

## Authorization semantics

The digest is bound to the base head of the atomic change-set. A separately committed event after review makes it stale. Operations earlier in the same change-set are included in current-state recomputation but do not replace the base-head component. Review issuance and turn-packet rebinding use one canonical digest constructor.

This permits a turn commit to add its narration source and then execute a review obtained for that same turn. It does not permit target mutation to pass unnoticed: any earlier operation that changes review-relevant state changes the recomputed digest.

## Validation

Replacement is refused when:

- the review digest is malformed or stale;
- the predecessor is ended or already has a successor;
- repair or successor IDs already exist;
- the new premise assignment is ended;
- the dependent assertion/assignment is ended or the question is closed;
- the candidate leaves every recorded semantic field unchanged;
- an equivalent active consequence already exists;
- the post-replacement assignment graph would contain a cycle;
- any ordinary identity, source, grant, or schema rule fails.

No event is appended on refusal.

## Atomic projection

One `consequence.replaced` event:

1. ends the predecessor with the repair reason;
2. inserts the successor consequence;
3. inserts the immutable repair row.

The three writes share one sequence number. There is no intermediate visible state in which both links are active or the predecessor is ended without lineage.

## Querying

```bash
./lacuna consequences CUBE --include-retired
./lacuna consequence-repair-frontier CUBE [--world-id WORLD]
./lacuna consequence-repairs CUBE
./lacuna explain CUBE cpr_old_to_new
```

`consequence_links` reports predecessor/successor IDs and one lineage state: `original`, `replaced`, `replacement`, `middle`, or `retired`.

A byte-identical semantic successor is refused. A source or rationale correction is itself recorded custody and may justify replacement; Lacuna validates inspectable change, not artistic sufficiency.

## Chained replacement

A successor can later be reviewed and replaced. This creates a chain:

```text
C0 --R1--> C1 --R2--> C2
```

`C1` then has lineage state `middle`. Each edge has its own review, reason, event, and repair ID. Rev0150 does not collapse the chain.

## Turn use

A director packet may include a `consequence_repair_frontier`. Each entry is a current repair-required consequence plus its review receipt. A `replace_consequence` proposal may cite that digest. Alias normalization binds `as` to the new consequence ID and independently generates a repair ID when absent.

Audience packets omit the frontier and all repair lineage.

## Nonclaims

- Replacement records authored custody; it does not prove causal continuity.
- Known lineage successors are suggestions for inspection, not recommendations.
- A review receipt does not certify the artistic wisdom of a candidate.
- Repair does not undo already presented narration or external side effects.
- The protocol is one-to-one. Split/merge semantics require a future contract.
