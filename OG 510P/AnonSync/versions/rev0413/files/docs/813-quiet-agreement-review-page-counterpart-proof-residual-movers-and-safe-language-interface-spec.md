# Quiet agreement review page — counterpart proof, residual movers, and safe-language interface spec

## Purpose

Once a quiet cohort exists, the operator needs one decisive review page before using strong language.
This page decides whether local pause has matured into a reviewed quiet agreement.

## Core decision

AnonSync should require a **quiet agreement review** whenever an operation asks for more than local stillness.

The review does not ask `did I pause something?`
It asks:

> do we have enough counterpart proof to claim the affected cohort is quiet enough for this exact job?

## Fixed review order

1. **Requested claim**
2. **Coverage proof**
3. **Residual movers**
4. **Claim ceiling**
5. **Decision**

## 1) Requested claim

Capture:

- requested sentence (`maintenance window started`, `safe to inspect`, `safe to migrate`, `safe to cut source`, `custom`)
- target subject
- required stop classes
- declared risk model

The product must keep the operator's intended sentence visible.
That is the sentence being tested.

## 2) Coverage proof

Show:

- targeted seats
- matched seats
- stale seats
- unresolved seats
- low-risk seats excluded by review

The page should let the operator mark some seats as non-blocking **only with an explicit reason**.

## 3) Residual movers

Render a table of the seats that still weaken the requested claim.

Columns:

- seat
- why it still matters
- remaining perturbation class
- evidence age
- cheapest honest next action

Remaining perturbation classes include:

- `may still publish payload`
- `may still receive and apply remote changes`
- `may still propagate deletes`
- `may still rescan and enlarge visible state`
- `quiet proof missing; behavior not safely bounded`

## 4) Claim ceiling

The review must compute one of these verdicts:

- `local-quiet-only`
- `quiet-across-covered-seats`
- `quiet-enough-for-declared-risk`
- `not-quiet-enough`
- `unknown`

Below the verdict, show:

- strongest allowed sentence
- stronger forbidden sentence

Examples:

- allowed: `quiet on 2 covered seats; one writable peer remains uncovered`
- forbidden: `the subject is fully frozen`

## 5) Decision

Allowed decisions:

- `issue quiet receipt`
- `request more counterparts`
- `narrow operation scope`
- `proceed with weaker sentence only`
- `abort quiet-dependent operation`

## Example projection

```text
Quiet agreement review qagr_01K...

Requested claim
  sentence .............. safe to inspect without perturbation
  subject ............... share finance/close-books
  declared risk ......... evidence-sensitive

Coverage proof
  targeted seats ........ 3
  matched seats ......... 2
  unresolved seats ...... 1 (writable)

Residual movers
  laptop-ops ............ may still publish local edits
    evidence age ........ seen online 4m ago; no quiet receipt
    next action ......... request quiet / narrow scope

Claim ceiling
  verdict ............... not-quiet-enough
  allowed sentence ...... quiet on initiating seat and NAS only
  forbidden sentence .... safe to inspect without perturbation
```

## Commands

```text
anonsync quiet-agreement review <cohort_id>
anonsync quiet-agreement apply <review_id>
```

## Success condition

A good quiet agreement review prevents the product from silently widening:

- local quiet into cohort quiet
- partial coverage into full coverage
- social coordination into technical proof
