# Decisions — rev0148

## D-0148-01: Store generic true-count bounds

**Decision:** represent a set-level rule as explicit members plus inclusive `min_true` and `max_true`.

**Reason:** one representation covers exactly-one, at-least-one, at-most-K, exactly-K, and ranged bounds without proliferating operation types.

## D-0148-02: Evaluate partial worlds under open-world semantics

**Decision:** missing and `unknown` members remain unresolved. Refuse only when the currently explicit partial valuation has no satisfying completion.

**Reason:** closed-world counting would turn absence into falsehood and violate Lacuna’s central epistemic doctrine.

**Consequence:** mathematically forced member values are not written automatically.

## D-0148-03: Constraints reject; they never materialize closure

**Decision:** cardinality evaluation may return compatibility diagnostics but may not create assertions or world assignments.

**Reason:** derivability, observation, belief, and deliberate commitment are different custody categories.

## D-0148-04: Combine anchors with each world independently

**Decision:** evaluate anchors alone and anchors plus one candidate world at a time.

**Reason:** every surviving world must respect irreversible commitments, while assignments from alternative worlds must never be mixed.

## D-0148-05: Refuse retroactively invalid declarations

**Decision:** a new cardinality constraint is atomic only if current anchors and every live/selected world already satisfy it.

**Reason:** adding world-integrity policy must not silently convert accepted live state into verifier failure.

## D-0148-06: Return deterministic temporal witnesses

**Decision:** report one stable minimal witness at an interval boundary, including record custody and an explicit nonclaim.

**Reason:** multi-claim constraints need inspectable refusal evidence, and deterministic output is essential for tests, hosts, and audits.

## D-0148-07: Keep constraints and their diagnostics planner-only

**Decision:** omit both definitions and any derived conflict carrying a relation or constraint identifier from perspective context.

**Reason:** hidden ontology can leak through explanations of visible data even when the ontology table itself is absent.

## D-0148-08: Generalize list-valued alias references

**Decision:** use a registry for list ID fields rather than special-casing audience lists.

**Reason:** turn normalization must be extensible and uniform; cardinality member lists are a first concrete consumer.

## D-0148-09: Advance database schema, not event schema

**Decision:** use database schema 3 and retain event schema 1.

**Reason:** new event types fit the existing immutable envelope; only physical projections and migration custody changed.

## D-0148-10: Chain supported migrations in one transaction

**Decision:** migrate coherent schema 1 or 2 cubes to schema 3 with ordered per-step digests and unchanged ledger head.

**Reason:** campaigns should be able to skip a runtime release without losing explicit custody of each physical transformation.

## D-0148-11: Do not add a general solver yet

**Decision:** implement direct deterministic bound checking with zero runtime dependencies.

**Reason:** this satisfies the current authored invariant while preserving a clear boundary for future inspectable closure, SAT/ASP planning, or quantified rules.

**Revisit when:** constraint formulas require disjunction across groups, conditional membership, quantified entities, or solver-generated explanations that cannot be represented honestly by the current evaluator.
