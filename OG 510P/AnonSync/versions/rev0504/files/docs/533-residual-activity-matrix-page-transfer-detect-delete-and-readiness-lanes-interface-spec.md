# Residual activity matrix page — transfer, detect, delete, and readiness lanes interface spec

## Purpose

A pause/quiescence action is only honest if the product can also show what remained active.
That answer should not require folklore or troubleshooting articles.
This page is the stable proof surface for that residual activity.

## Core decision

AnonSync should maintain one **residual activity matrix** for every paused, throttled, partially stopped, or maintenance-isolated object.
The matrix is a durable read surface and can also be linked from receipts, rows, and command output.

## Matrix columns

Every row must project these columns:

- **Activity lane**
- **Current verdict**
- **Why**
- **Visible consequence**
- **Counterfactual stronger action**

## Minimum lane set

At minimum, the matrix must contain:

1. `send payload bytes`
2. `receive payload bytes`
3. `propagate delete instructions`
4. `propagate zero-byte or control-shaped artifacts`
5. `detect local changes`
6. `index / update readiness state`
7. `appear as participating subject`

Implementations may add more lanes, but they may not collapse these away.

## Verdict grammar

Each lane uses exactly one verdict:

- `stopped`
- `still active`
- `active only in reduced form`
- `inactive by stronger boundary`
- `unknown / platform-dependent`

No vague badges like `paused-ish` or `limited` are allowed without a row-level verdict.

## Example matrix

```text
Residual activity matrix — share media/raw

lane .................................. verdict ................ visible consequence
send payload bytes .................... stopped ................ no new full-byte egress expected
receive payload bytes ................. stopped ................ no new full-byte ingress expected
propagate delete instructions ......... still active ........... remote deletes may still remove local presence
zero-byte/control artifacts ........... still active ........... control-shaped churn may still appear
detect local changes .................. still active ........... local edits may still enter observed state
index/readiness state ................ still active ........... counts and readiness may continue changing
appear as participating subject ....... still active ........... peers may still see this seat as present
```

## Why column

The `Why` column should name the supporting mechanism in product language, such as:

- `only transfer lanes were stopped`
- `disconnect was not requested`
- `detection remains enabled during this class`
- `this subject still participates in roster state`

This column exists so the matrix is explanatory, not merely declarative.

## Counterfactual column

Every still-active lane should say what stronger action would stop it, for example:

- `disconnect this seat`
- `enter maintenance isolation`
- `use evidence snapshot instead of pause`
- `remove participation entirely`

That turns the page into a decision aid instead of a dead report.

## Derived chips

Rows elsewhere in the interface may summarize this matrix using chips such as:

- `tx stopped`
- `deletes still live`
- `detect still live`
- `not evidence-stable`
- `participation remains`

But every chip must deep-link back to this full matrix.

## CLI projection

```text
anonsync quiesce matrix show <object>
anonsync quiesce matrix show <object> --json
```

JSON should preserve lane names, verdicts, proof basis, and stronger alternatives as first-class fields.

## Audit relevance

When a quiescence-related incident occurs, the audit log should be able to point to the exact matrix that was in force at the time.
The matrix is therefore part of the evidence chain, not just convenience UI.

## Success condition

A good residual activity matrix lets an operator answer, without guessing:

- what is still capable of changing
- why it is still capable of changing
- what user-visible consequences remain
- what exact stronger action would stop each remaining lane
