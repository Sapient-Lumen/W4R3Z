# Decisions — rev0150

## D-0150-01 — repair is forward replacement, not rollback

**Decision:** append a new replacement event that ends the predecessor and creates a successor. Never rewrite or insert into historical event order.

**Why:** experienced narration and external effects may already exist. A current correction can be audited; simulated time travel can erase evidence of what the system actually did.

**Rejected:** delete the old link; mutate it in place; insert a retroactive event and replay the world as though the old dependency never existed.

## D-0150-02 — the repair relation has its own identity

**Decision:** store an identified `consequence_repairs` row rather than only a predecessor pointer on the successor.

**Why:** the act of replacement has reason, review, event, and explanation custody independent of either consequence.

## D-0150-03 — one repair is one predecessor to one successor

**Decision:** enforce unique predecessor and successor membership in repair rows.

**Why:** one-to-one semantics are easy to explain, replay, and verify. Split/merge needs explicit cardinality and allocation policy rather than accidental fan-out.

**Future:** add distinct split/merge operations instead of weakening this invariant.

## D-0150-04 — review exposes lineage candidates but never auto-transfers

**Decision:** list active explicit assignment/assertion descendants in the review; require the author to choose and fully restate successor semantics.

**Why:** structural succession does not prove that the dependency survives, keeps the same relation, or deserves the same severity.

## D-0150-05 — review authorization binds to the atomic base head

**Decision:** validate reviewed operations against the change-set’s initial head while recomputing all other review fields from current in-transaction projections.

**Why:** source-bound turns need to add provenance before a mutation in the same atomic commit. Outside concurrency must still stale the receipt, and relevant earlier operations must still alter the digest.

**Rejected:** evergreen receipts; binding only to the live head immediately before each operation; exempting all same-transaction changes from recomputation.

## D-0150-06 — new custody requires active endpoints

**Decision:** a new consequence may not target an ended assignment/assertion or closed question.

**Why:** repair debt should arise because a once-valid endpoint later ended, not because invalid custody was created intentionally.

## D-0150-07 — validate the graph after predecessor removal

**Decision:** cycle-check replacement against active assignment edges excluding the predecessor.

**Why:** the predecessor is ended by the same event. Pre-change validation produces false positives and does not model the committed graph.

## D-0150-08 — semantic no-op replacement is refused

**Decision:** at least one endpoint or recorded semantic field must change.

**Why:** generating lineage with no recorded change creates noise and can be used to launder a review timestamp without repairing anything. Endpoint, relation, severity, source, and rationale are all part of authored consequence custody; changing any of them creates an inspectable successor.

## D-0150-09 — repair verification is event-backed

**Decision:** verify every repair projection against the exact `consequence.replaced` payload at its creation sequence and require every such event to project a repair row.

**Why:** uniqueness and foreign keys are insufficient against coordinated projection tampering.

## D-0150-10 — repair internals are planner-only

**Decision:** omit repair rows and review frontiers from perspective contexts and refuse perspective explanations for repair records.

**Why:** repair deliberation exposes hidden-world ontology, abandoned dependencies, and future planning intent.

## D-0150-11 — a replacement operation owns two IDs

**Decision:** `consequence_id` is the primary alias-bound identity; `repair_id` is generated separately when omitted.

**Why:** the successor entity and the relation that created it are different records and must not share a namespace accidentally.

## D-0150-12 — database schema 5, event schema 1

**Decision:** add one projection table and one additive event type without changing the event envelope version.

**Why:** immutable event structure and current physical query layout evolve independently. Schema 4→5 migration preserves the ledger head.

## D-0150-13 — one canonical repair-digest constructor

**Decision:** storage owns the `lacuna.consequence-repair.v1` digest constructor; turn issuance calls that same function when rebinding embedded receipts.

**Why:** authorization must not depend on two independently maintained serializations of the same review surface.

## D-0150-14 — the repair frontier contains debt, not rewrite suggestions

**Decision:** `consequence_repair_frontier` returns only active links whose endpoint lifecycle currently requires repair, optionally scoped to one world.

**Why:** exposing every healthy edge as a candidate rewrite would turn an integrity tool into a constant-retcon prompt. A planner may still request a semantic-replacement review explicitly.

## D-0150-15 — review-head custody is event-backed and receipt-derived

**Decision:** the immutable replacement event records its reviewed base head; query output derives the authoritative `review_head` from the origin change receipt and verification requires both to agree.

**Why:** the event states the authorization claim, while the receipt is the transaction record that can corroborate it. Storing a second mutable projection copy would add drift without adding authority.
