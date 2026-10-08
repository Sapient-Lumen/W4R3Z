# Cardinality constraints

## Purpose

A pairwise relation can say that two claims cannot both be true. It cannot directly say that one, two, or some bounded number among a larger set must be true. Lacuna therefore stores set-level cardinality constraints as first-class, event-sourced world-integrity policy.

A constraint has:

- a stable `constraint_id` and human label;
- two or more distinct member `claim_ids`;
- inclusive bounds `min_true` and `max_true`;
- a source when one exists;
- an authored rationale;
- creation and optional retirement custody.

The invariant is:

```text
min_true <= number of true members <= max_true
```

at every relevant tick on a timeline.

## Open-world semantics

Cardinality checking operates on a **partial valuation**. A member is:

- known true when an active overlapping record explicitly says `true`;
- known false when an active overlapping record explicitly says `false`;
- unresolved when no record exists or the only record says `unknown`.

An upper bound is violated only when more than `max_true` members are explicitly true.

A lower bound is violated only when enough members are explicitly false that no assignment of the unresolved members could reach `min_true`.

For three members under exactly one:

| Explicit state | Result |
|---|---|
| `A=true`, `B=?`, `C=?` | valid; no value is written for B or C |
| `A=false`, `B=false`, `C=?` | valid; C is not materialized as true |
| `A=true`, `B=true`, `C=?` | refused: upper bound exceeded |
| `A=false`, `B=false`, `C=false` | refused: lower bound impossible |

This is compatibility checking, not logical closure. Even where a truth value is mathematically forced, Lacuna does not pretend that the value was observed, asserted, believed, or deliberately committed.

## Supported forms

The generic bounds cover common authored rules:

```text
exactly one   min_true=1, max_true=1
at most one   min_true=0, max_true=1
at least one  min_true=1, max_true=N
exactly K     min_true=K, max_true=K
between L/U  min_true=L, max_true=U
```

A vacuous `0..N` constraint is refused because it constrains nothing. Bounds must satisfy:

```text
0 <= min_true <= max_true <= member_count
```

Member count is currently limited to 256. Duplicate members and duplicate active definitions are refused.

## Mutation operations

### Declare

```json
{
  "op": "declare_cardinality",
  "constraint_id": "crd.single-culprit",
  "label": "Exactly one culprit",
  "claim_ids": ["clm_ada", "clm_basil", "clm_cora"],
  "min_true": 1,
  "max_true": 1,
  "source_id": "src_mystery-bible",
  "rationale": "The authored mystery contains one culprit."
}
```

Declaration is preflighted against:

1. active anchors by themselves;
2. active anchors combined separately with every live or selected candidate world.

A declaration that would make accepted active state impossible is refused atomically. Lacuna does not install a broken constraint and ask the caller to repair the world afterward.

### Retire

```json
{
  "op": "retire_cardinality",
  "constraint_id": "crd.single-culprit",
  "reason": "The revised scenario permits accomplices."
}
```

Retirement ends the active constraint without deleting its declaration, members, source, rationale, or events. Projection replay preserves the full lifecycle.

## CLI

```bash
./lacuna cardinality-add /path/to/cube \
  --constraint-id crd.single-culprit \
  --label "Exactly one culprit" \
  --claim-id clm_ada \
  --claim-id clm_basil \
  --claim-id clm_cora \
  --min-true 1 \
  --max-true 1 \
  --rationale "The authored mystery contains one culprit."

./lacuna cardinalities /path/to/cube
./lacuna explain /path/to/cube crd.single-culprit
./lacuna cardinality-retire /path/to/cube crd.single-culprit \
  --reason "The revised scenario permits accomplices."
```

## Temporal witnesses

Validity intervals are inclusive. A constraint is evaluated independently on each timeline at deterministic interval boundary points. When a violation exists, Lacuna reports one bounded witness containing:

- constraint and violation kind;
- known true, false, and unresolved counts;
- timeline and representative tick;
- intersection interval of the witness records;
- minimal witness claim IDs for the violated bound;
- assertion/assignment custody references;
- an explicit nonclaim against reading the witness as inferred narrative truth.

For an at-most-one constraint, `A=true` over `[0,4]` and `B=true` over `[5,9]` is valid. If B starts at tick 4, the inclusive intervals overlap at tick 4 and the write is refused with a `[4,4]` witness.

## World and anchor scope

Constraints are global authored policy, but they are checked against each candidate world independently:

```text
anchors + world A
anchors + world B
anchors + world C
```

Assignments from different candidate worlds are never combined. Anchors are combined with every live or selected world because every surviving explanation must respect what can no longer move.

Pruned or archived worlds may remain historically inconsistent with a newer constraint. They must pass current constraints before reactivation.

## Context and turn access

Constraint definitions, member sets, and constraint-derived diagnostics are privileged planner state. Perspective context contains an explicit omission marker but no constraint IDs, labels, members, or derived conflict records.

Director turn proposals may declare and retire cardinality constraints. Sequential `@alias` references are supported inside the `claim_ids` list, so a proposal may declare several claims and then bind one constraint over them in the same atomic change-set.

Audience-profile turn grants cannot create or retire hidden world-integrity policy.

## Deliberate nonclaims

- Cardinality constraints are not a SAT, SMT, ASP, or theorem-proving interface.
- They do not infer, materialize, or disclose forced values.
- They do not choose or weight candidate worlds.
- They do not prove a mystery is fair, a plot is good, or a rule is authored correctly.
- Member sets are explicit and static; there are no quantified predicates or dynamic collections.
- A deterministic witness proves incompatibility of recorded partial state with an authored bound, not objective truth about the fiction.
