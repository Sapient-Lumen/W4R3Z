# Architecture decisions — rev0145

## D-0145-01 — Name the project Lacuna

**Decision:** Rename Datacube proper to **Lacuna**.

**Reason:** The system's defining behavior is not storing everything. It is preserving what has not been decided and preventing absence from being mistaken for falsity or permission to invent.

**Naming note:** “Lacuna” is a common word and appears in other software names. This revision treats it as the project name and uses the distribution identifier `lacuna-epistemic-ledger`. Trademark and package-registry clearance are outside this technical cut.

## D-0145-02 — Cut over instead of incrementally carrying the old runtime

**Decision:** Build a new lean kernel and preserve parent lineage by digest and audit documentation.

**Reason:** Retaining self-building, release, cloud, and historical-corpus machinery would make deletion harder to verify than replacement. The target architecture has a different center.

## D-0145-03 — Use event sourcing with disposable projections

**Decision:** Accepted semantic mutations are append-only events; query tables are replayable projections.

**Reason:** Revision history, refusal, reproducibility, and audit are first-class. Destructive row updates alone would erase why the system changed its mind.

## D-0145-04 — Separate claims from assertions

**Decision:** A content-addressed claim has no truth value by itself. Truth stances live in assertions or world assignments.

**Reason:** This prevents the database from conflating “the proposition exists” with “the proposition is true.”

## D-0145-05 — Separate assertor from perspective holder

**Decision:** Assertions record both who made or registered the assertion and whose epistemic state it represents.

**Reason:** A narrator can record that Mira believes something without the narrator believing it or making it world truth.

## D-0145-06 — Keep several candidate worlds

**Decision:** The hidden world is a weighted set of explicit candidates.

**Reason:** Compressing every cycle to one winner recreates premature commitment. World selection is allowed for planning convenience but carries no automatic canonical force.

## D-0145-07 — Make anchors narrow and enforceable

**Decision:** `anchored` assertions cannot be unknown, superseded in place, or contradicted by overlapping live-world assignments.

**Reason:** The system needs a hard edge where reinterpretation stops. Anchors represent consequences that the experience can no longer revise honestly. A mistaken anchor is a custody error requiring an explicit new lineage, not a routine semantic edit.

## D-0145-08 — Separate ledger time from narrative valid time

**Decision:** Every event has recording order/time; assertions and assignments may also carry narrative timeline intervals.

**Reason:** Learning a fact now about an event then is routine in mystery, simulation, and audit.

## D-0145-09 — Use optimistic head binding

**Decision:** Every external change-set names the head it builds on.

**Reason:** Concurrent writers should fail explicitly rather than unknowingly interleave incompatible assumptions.

## D-0145-10 — Keep the runtime dependency-free

**Decision:** Use Python's standard library and SQLite for rev0145.

**Reason:** The data model is still being cut. Auditability and fast revision matter more than framework convenience. Dependencies may be admitted later under a documented risk argument.

## D-0145-11 — Do not make the cube build itself

**Decision:** Compilation, packaging, deployment, model hosting, and self-improvement remain external workflows.

**Reason:** Semantic custody should not be coupled to artifact custody. A world engine that must also perpetuate its own build system becomes difficult to reason about and harder to delete safely.

## D-0145-12 — Expose nonclaims

**Decision:** Verification output states what its integrity check does not prove.

**Reason:** A checksum can create false confidence. Honest boundaries are part of the interface.
