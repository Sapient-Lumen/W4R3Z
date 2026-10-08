# Residual allowance review page — expected residue, quiet violation, and sentence survival interface spec

## Purpose

The quiet event page introduces a challenge.
This page decides what the challenge means.
It answers:

> did this event fit the previously declared residual allowances, or did it actually violate the quiet claim?

That judgment should not depend on remembered help text.
It should be a first-class review.

## Core decision

Every quiet event against an active quiet receipt must pass through a **residual allowance review** before AnonSync says `quiet survived` or `quiet failed`.

## Fixed review order

1. **Active allowance matrix**
2. **Observed event fit**
3. **Verdict ladder**
4. **Claim survival**
5. **Safe sentence now**
6. **Successor action**

## 1) Active allowance matrix

Render the exact allowances carried by the prior quiet receipt.
At minimum show verdicts for:

- delete propagation
- zero-byte/control-shaped events
- indexing/share-size growth
- queue/visibility churn
- counterpart upload
- counterpart download
- runtime return / schedule expiry

Each row must say one of:

- `explicitly allowed`
- `explicitly forbidden`
- `not covered by prior receipt`
- `unknown / not declared`

## 2) Observed event fit

For the challenge event, show:

- event class
- event seat and scope
- prior allowance row matched
- strength of fit (`strong`, `partial`, `poor`, `none`)
- notes on why the fit did or did not hold

## 3) Verdict ladder

Allowed final verdicts are:

- `allowed-residual`
- `outside-prior-claim`
- `quiet-claim-narrowed`
- `quiet-violation`
- `insufficient-evidence`

The page must say why each stronger verdict lost.

## 4) Claim survival

Compute one of:

- `prior-claim-unchanged`
- `prior-claim-still-valid-but-narrower`
- `prior-claim-superseded`
- `prior-claim-never-earned-for-this-scope`
- `unknown`

Do not silently convert an out-of-scope or allowed event into `quiet failed`.

## 5) Safe sentence now

Below the verdict, show:

- strongest allowed sentence now
- stronger forbidden sentence now

Examples:

- allowed: `index growth on nas-01 was an allowed residual under receipt qcr_01K; the covered quiet claim still stands`
- forbidden: `no movement happened during the quiet window`

or:

- allowed: `counterpart upload from laptop-ops was not allowed by receipt qcr_01K and the prior cohort-wide quiet claim is now superseded`
- forbidden: `the original quiet receipt still covers all writable seats`

## 6) Successor action

Recommend the lightest honest next step, such as:

- keep prior receipt active
- narrow the surviving claim
- open quiet break review
- request new quiet from one seat
- issue successor quiet receipt

## Example projection

```text
Residual allowance review — evt_01L

Active allowance matrix
  delete propagation ........ explicitly allowed
  index/share-size growth ... explicitly allowed
  counterpart upload ........ explicitly forbidden

Observed event fit
  event class ............... index-growth
  matched allowance ......... index/share-size growth
  fit strength .............. strong

Verdict ladder
  final verdict ............. allowed-residual
  stronger rejected ......... quiet-violation

Claim survival
  survival .................. prior-claim-unchanged

Safe sentence now
  allowed ................... prior quiet claim still stands; this event fits declared residual indexing behavior
  forbidden ................. no activity whatsoever occurred during the quiet window
```

## Commands

```text
anonsync residual-review open --event <event_id>
anonsync residual-review show <review_id>
anonsync residual-review show <review_id> --json
```

## Success condition

A good residual allowance review lets an operator answer:

- whether the event was expected residue or a true violation
- whether the old quiet claim survived, narrowed, or failed
- what exact sentence is still safe now
