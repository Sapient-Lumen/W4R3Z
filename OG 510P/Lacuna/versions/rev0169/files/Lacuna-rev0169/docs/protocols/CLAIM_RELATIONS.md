# Claim relations: compatibility without closure

## Purpose

A particle bank is useful only if the kernel can tell when one candidate world is internally impossible. Same-claim contradiction is not enough: many world rules connect distinct propositions.

Lacuna stores those rules as explicit claim relations. They are authored constraints with identity, source, rationale, creation event, and optional retirement event.

## Relation kinds

For explicit endpoint values `L` and `R`:

| Relation | Incompatible pair | Meaning |
|---|---|---|
| `excludes` | `L=true`, `R=true` | At most one endpoint may be true. |
| `negates` | both known and equal | Known endpoint values must differ. |
| `entails` | `L=true`, `R=false` | Truth of the left is incompatible with falsity of the right. |
| `equivalent` | both known and unequal | Known endpoint values must agree. |

`unknown` is compatible with every relation. This is intentional. Absence of a value does not close the world.

## Important non-entailments

- `excludes(A, B)` does not mean exactly one is true.
- `negates(A, B)` does not assert either endpoint.
- `entails(A, B)` plus `A=true` does not materialize `B=true`.
- `equivalent(A, B)` does not merge the identities of the claims.
- Retiring a relation does not change or erase any endpoint assignment.

A relation is a **refusal rule**, not an assertion generator.

## Where relations apply

The same compatibility engine checks:

- overlapping anchored assertions;
- active assignments inside each live or selected world;
- a world being reactivated;
- a new relation against all existing live/selected worlds and anchors;
- the `conflicts` and `verify` projections.

Intervals must overlap on the same timeline before a pair can conflict.

## Declare a relation

```bash
./lacuna relation-add ./stories \
  --relation-id rel_one_culprit \
  --left-claim-id clm_ada \
  --right-claim-id clm_basil \
  --relation excludes \
  --source-id src_design_bible \
  --rationale "The mystery premise permits at most one of these people to be the culprit."
```

The operation is refused if:

- either endpoint does not exist;
- the endpoints are identical;
- an identical active relation already exists;
- the source does not exist;
- active anchors or any live/selected world already violate it.

Symmetric relations (`excludes`, `negates`, `equivalent`) canonicalize endpoint order. `entails` preserves direction.

## Retire a relation

```bash
./lacuna relation-retire ./stories rel_one_culprit \
  --reason "The premise was deliberately widened to permit collusion."
```

Retirement ends the active constraint. It does not delete the declaration. `relations` shows active relations; the programmatic query can include retired history, and `explain` shows both origin and termination events.

## Context and turns

Relations are privileged planner state. They can expose hidden ontology or authored mystery structure, so audience context omits them even when the endpoint claims are visible.

Audience-profile turn grants cannot declare or retire relations. Director-profile grants may do so, subject to all normal relation validation. A director model should treat relation changes as high-impact world-integrity edits, not as a convenience for making the latest narration fit.

## Design rule for future inference

A closure engine may eventually derive consequences from relations. Any derived item must remain distinguishable from stored custody and should include:

- premises;
- rule IDs;
- derivation version;
- access scope;
- whether it was materialized or computed on demand;
- invalidation behavior when a premise or relation retires.

Until that exists, Lacuna chooses honest incompleteness over invisible inference.

## When a pair is not enough

Use a cardinality constraint when the authored rule is about a whole set: exactly one culprit, at least two keys, or no more than three active seals. Encoding an at-most-one set as every pair may be logically adequate for the upper bound, but it obscures the single authored rule and cannot express a positive lower bound. See [`CARDINALITY_CONSTRAINTS.md`](CARDINALITY_CONSTRAINTS.md).
