# Quiet challenge ledger page — event clustering, residual fit, and first-real-break interface spec

## Purpose

One quiet receipt may attract several later events.
Some may be allowed residue.
Some may be out of scope.
One may be the first real break.
The operator needs a ledger that answers:

> across all later motion, **which events were harmless, which were merely out of scope, and which one actually became the first real quiet break?**

## Core decision

Every active or recently challenged quiet receipt gets a **quiet challenge ledger**.
This ledger does not flatten all later events into one failure story.
It preserves classification history.

## Fixed review order

1. **Receipt under challenge**
2. **Challenge stack**
3. **Residual-vs-break clustering**
4. **First real break verdict**
5. **Unresolved items**
6. **Receipt lineage now**

## 1) Receipt under challenge

Show:

- quiet receipt id
- covered scope
- issue time
- strongest originally allowed sentence
- current lineage state

## 2) Challenge stack

List every later event in stable order with:

- time
- seat
- event class
- provisional meaning
- final review verdict if available

## 3) Residual-vs-break clustering

Cluster events into exactly these buckets:

- `allowed-residuals`
- `outside-claim`
- `candidate-breaks`
- `confirmed-breaks`
- `insufficient-evidence`

The page must make it obvious that `first observed event` is not always `first confirmed break`.

## 4) First real break verdict

Show one of:

- `no-break-confirmed`
- `first-break-confirmed`
- `multiple-break-candidates-unresolved`
- `prior-claim-never-covered-this-scope`

If confirmed, preserve:

- first real break event id
- break time
- break seat
- break authority class if known
- quiet tenure before break

## 5) Unresolved items

Render any ambiguous events separately with:

- missing proof
- stronger sentence currently blocked
- cheapest next clarifying action

## 6) Receipt lineage now

At the bottom, show:

- prior receipt state (`active`, `narrowed`, `superseded`, `retired`)
- successor receipt if one exists
- surviving strongest sentence
- stronger forbidden sentence

## Example projection

```text
Quiet challenge ledger — qcr_01K

Challenge stack
  03:09:41  nas-01       index-growth          allowed-residual
  03:12:00  laptop-ops   scheduler-boundary    confirmed-break
  03:12:08  peer-a       queue-growth          after-break noise

First real break verdict
  status ................ first-break-confirmed
  event ................. evt_01M
  break seat ............ laptop-ops
  quiet tenure .......... 12m 00s

Receipt lineage now
  prior receipt ......... superseded
  successor ............. qcr_01N required for renewed cohort quiet
```

## Commands

```text
anonsync quiet-challenges show --receipt <receipt_id>
anonsync quiet-challenges show --receipt <receipt_id> --json
```

## Success condition

A good quiet challenge ledger lets an operator answer:

- which later events were allowed residue
- which events were merely outside the earlier claim
- which event, if any, became the first real break
- what receipt state survives now
