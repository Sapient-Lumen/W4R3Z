# Fact capture proof page: question answered, evidence quality, and route update interface spec

## Purpose

Once the chosen ask is executed, the product still needs one page that answers:

> what exactly came back, how trustworthy is it, which ambiguity did it actually collapse, and what route or stronger sentence changed because of it?

## Core decision

AnonSync must expose one first-class **Fact capture proof** page whenever a chosen evidence ask returns anything material, including partial, stale, contradictory, or failed capture.

## Fixed page order

1. **Capture header**
2. **Requested-ask card**
3. **Returned-evidence card**
4. **Evidence-quality card**
5. **Route-update card**
6. **Proof sentence**

### 1) Capture header

Show:

- capture proof id
- source acquisition sheet id
- source ask id
- answer state
- current best route after capture
- strongest safe sentence now

Supported `answer_state` values:

- `answered-cleanly`
- `answered-partially`
- `answered-but-stale`
- `contradictory-return`
- `capture-failed`
- `capture-declined`

Hard rule:

A failed or declined capture still gets a proof page.
Absence of evidence is not absence of product truth.

### 2) Requested-ask card

Required rows:

- original question or capture request
- target channel
- expected discriminator value
- why it was selected
- pre-capture sentence ceiling

### 3) Returned-evidence card

Required rows:

- returned fact or artifact summary
- collection time
- collector identity or source
- missing pieces
- contradictions found
- retained raw reference or receipt pointer

Hard rule:

The page must preserve the delta between what was requested and what actually came back.

### 4) Evidence-quality card

Supported `evidence_quality` values:

- `high-direct`
- `high-but-narrow`
- `medium-usable`
- `weak-contextual`
- `stale-or-fragile`
- `failed-to-capture`

Required rows:

- evidence quality
- freshness class
- scope covered
- route-collapsing power actually achieved
- residual ambiguity that survives

Hard rule:

Evidence quality is about the return, not the effort spent to get it.
Heavy capture can still return weak evidence.

### 5) Route-update card

Supported `route_update` values:

- `governing-route-confirmed`
- `leading-lookalike-disqualified`
- `ambiguity-narrowed`
- `no-material-change`
- `route-reversal-triggered`
- `escalation-now-justified`

Required rows:

- route update
- doctrine or intervention change caused
- stronger sentence newly allowed
- stronger sentence still blocked
- next ask if ambiguity remains

Hard rule:

The page must publish what changed because of the capture.
A returned artifact without route consequences is incomplete proof.

### 6) Proof sentence

Render one sentence only:

- `The selected ask [answer_state]; returned evidence quality is [quality], resulting in [route_update]. The strongest safe sentence is now [sentence].`

## Required interactions

- **Attach returned evidence**
- **Downgrade or upgrade evidence quality**
- **Confirm route change**
- **Spawn next ask**
- **Accept no-material-change**

## Failure state

If capture failed or was declined, show:

- `This capture did not return usable new evidence. The prior ceiling remains, unless a weaker or alternative ask is now justified.`
