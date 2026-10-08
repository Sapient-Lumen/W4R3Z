# Certificate takeover review page: directionality, shares replacement, and storage survivor interface spec

## Purpose

This page exists for the moment an operator links two already-populated seats or changes a seat's identity.
It answers one ordinary question:

> if this seat adopts that certificate now, what precisely gets replaced in the app, what survives on disk, and which side becomes the graph baseline afterward?

## When this page must appear

Trigger this page for:

- linking two already-running independent Sync instances
- any action that creates a new certificate for an existing seat
- any attempt to merge or replace one populated graph with another
- any action where Advanced-subject disappearance from the app is possible

## Fixed page order

1. takeover intent header
2. direction and replacement card
3. survivor map card
4. risk and ceiling card
5. receipt/export rail

### 1) Takeover intent header

Show:

- adopting seat / source seat / source identity
- takeover verdict (`certificate adoption`, `same-graph no-op`, `new-local-certificate only`, `unsafe-to-claim`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Direction and replacement card

Render rows for:

- which side's M-key or link direction was chosen
- which certificate/fingerprint survives
- which visible share roster becomes baseline
- whether Advanced folders on the adopting seat will disappear from the app
- whether linked-device arrivals will repopulate from the source graph

### 3) Survivor map card

Show the reviewed distinction between:

- app-roster replacement
- filesystem-byte survival
- iOS / platform exception risk
- manual re-share or relink debt that remains after takeover

### 4) Risk and ceiling card

Possible warnings:

- `mixed v2/v3 linking can disturb license/UI/share configuration`
- `certificate takeover is directional and not symmetric`
- `advanced subjects may leave the app even when disk bytes survive`
- `future folder visibility becomes graph-wide after commit`
- `display-name change is certificate-affecting, not merely cosmetic`

### 5) Receipt/export rail

Offer:

- `Emit identity lineage receipt`
- `Open identity-graph adoption contract sheet`
- `Open identity containment reset proof`

## Rules

### Rule 1 — takeover must stay directional

The page must not present `link` as if both sides survive unchanged.

### Rule 2 — app state and disk survivor state must stay separate

A subject leaving the app is weaker than bytes being deleted from storage.

### Rule 3 — name change may not masquerade as rename-only

Any action that regenerates certificate identity must use takeover-grade language.
