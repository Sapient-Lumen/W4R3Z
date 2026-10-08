# Audit — rev0148

## Scope

This pass audited rev0147 for the next failure modes likely to appear when Lacuna is used as the custody core of a long-running mystery, campaign, or adaptive narrative system.

## A-0148-01 — pairwise relations could not express group commitments

**Severity:** architecture-blocking

**Before:** pairwise `excludes` could approximate at-most-one, but there was no direct representation for exactly-one, at-least-one, exactly-K, or bounded sets.

**Risk:** a planner could maintain several mutually incompatible “culprit” claims without a way to say that some member must eventually be true. Encoding large at-most constraints as every pair also obscures the authored rule and its custody.

**Repair:** first-class `min_true` / `max_true` cardinality constraints with explicit members, source, rationale, lifecycle, and deterministic checking.

**Evidence:** exact-one upper/lower tests, temporal tests, anchor/world combination tests, retroactive-declaration refusal, retirement/replay tests.

## A-0148-02 — a hidden ontology could leak through diagnostics

**Severity:** high confidentiality boundary

**Before:** perspective context omitted relation definitions, but `cube.conflicts()` could still return a relation-derived contradiction between two visible assertions. The diagnostic itself revealed that a hidden authored relationship existed.

**Risk:** a player could infer mystery structure from conflict kind, relation ID, or constraint membership even though the planner ontology was nominally omitted.

**Repair:** perspective context now filters every conflict carrying a `relation_id` or `constraint_id`; it advertises `constraint_derived_conflicts` as explicitly omitted.

**Evidence:** regression test creates two visible accepted assertions that violate a hidden cardinality rule. Planner context sees the diagnostic; audience context and Markdown reveal neither ID nor existence beyond a generic omission notice.

## A-0148-03 — alias normalization special-cased one list field

**Severity:** medium, extensibility and correctness

**Before:** scalar ID references used a registry, while only `audience` lists received an ad hoc alias pass.

**Risk:** new list-valued references would be forgotten or normalized inconsistently. Cardinality member lists are exactly such a field.

**Repair:** introduce `REFERENCE_LIST_FIELDS` and normalize all registered list references through one ordered, forward-reference-refusing path.

**Evidence:** one turn proposal declares two claims and then declares a cardinality constraint over both aliases in the same atomic operation list.

## A-0148-04 — migration policy needed an ordered chain

**Severity:** high custody continuity

**Before:** rev0147 supported only schema 1 to 2. A schema-1 campaign skipping a release needed a trustworthy path to the current schema without opening it under intermediate runtimes.

**Repair:** one explicit migration function now executes 1→2→3 or 2→3 under one immediate transaction, records each step digest, and asserts unchanged ledger head.

**Evidence:** independent tests simulate coherent schema-1 and schema-2 databases and verify head preservation plus full post-migration verification.

## A-0148-05 — multi-record temporal failures needed useful witnesses

**Severity:** medium, auditability

**Before:** pairwise errors could name two records, but a lower-bound failure may require several explicit falsehoods and cannot be explained by one pair.

**Repair:** cardinality evaluation returns one deterministic minimal bound witness with claim IDs, record references, timeline, representative tick, and intersection interval.

**Evidence:** inclusive intervals that touch at tick 4 produce a `[4,4]` witness; adjacent non-overlapping intervals remain valid.

## A-0148-06 — the store monolith was absorbing more logic

**Severity:** maintainability

**Before:** rev0147 centralized pairwise checks but the temptation was to place set evaluation and interval search directly into the already-large store module.

**Repair:** keep cardinality semantics as deterministic pure functions in `logic.py`; store code owns querying, lifecycle, and refusal policy.

**Remaining concern:** `store.py` is still large. A later extraction should split schema/migration, event projection, and query services without changing public semantics.

## Rejected alternatives

### Reduce exactly-one to pairwise excludes plus an implied fact

Rejected. Pairwise excludes expresses only the upper bound, while implied-fact materialization would collapse unknown into inferred custody.

### Install constraints and mark worlds invalid afterward

Rejected. This makes validity path-dependent and permits a successful mutation to corrupt every live explanation.

### Use a general SAT/ASP solver immediately

Rejected for this revision. The current requirement is small, deterministic, explainable, dependency-free bounds over explicit claims. A solver adds representation and explanation questions before the kernel has a governed inference layer.

### Show constraint conflicts but hide definitions

Rejected. Diagnostics are part of the information boundary.

## Residual risks

- Constraint members are static IDs, not quantified sets.
- Evaluation is intentionally simple and may need indexing if campaigns hold many large groups and long interval histories.
- A same-claim true/false contradiction is left to the pairwise engine rather than double-counted by cardinality evaluation.
- Authored constraints can be mistaken or malicious even when perfectly custodied.
- No fairness metric proves that a mystery gave the player enough evidence before a constraint collapses possibilities.
- No causal model distinguishes a genuinely divergent outcome from a retrospectively flattering reinterpretation.
- Direct database and verifier replacement remains outside the local hash-chain threat model.
