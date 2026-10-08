# Counterevidence adjudication review page: green state, history gap, and scope mismatch interface spec

## Purpose

The dispute contract sheet records the challenge.
This page decides it.
It answers the next ordinary operator question:

> when completion has been challenged, which witness family matters most for this claim type, what contradictions remain unresolved, and what verdict is actually safe?

## Core decision

AnonSync must expose one first-class **Counterevidence adjudication review** whenever contradictory witness families are being reconciled for a challenged completion claim.

## Fixed page order

1. **Claim-and-challenge recap**
2. **Witness ladder**
3. **Contradiction matrix**
4. **Adjudication outcome selector**
5. **Rework routing strip**
6. **Safe-language footer**

### 1) Claim-and-challenge recap

Show side by side:

- original fulfillment claim
- challenger sentence
- scope under review
- currently accepted residue if any
- strongest forbidden overclaim

Hard rule:

This page must not force the reviewer to navigate away to remember what is actually being challenged.

### 2) Witness ladder

For each witness family, show:

- freshness
- scope relevance
- directness to the challenged outcome
- drift risk
- weight in this adjudication

Required weighting prompts:

- `Does this witness prove requested scope, or only general activity?`
- `Does this witness cover all relevant peers/worlds, or only connected ones?`
- `Could this witness be distorted by time skew, disconnected peers, placeholder state, or path drift?`

Hard rule:

General health witnesses must stay weaker than scope-specific witnesses when the challenge is about scope-specific completion.

### 3) Contradiction matrix

Required rows:

- green state vs missing-effect report
- history activity vs missing-present outcome
- permission/right present vs future updates actually suspended
- peer online count vs source availability for the challenged bytes
- same path label vs changed underlying location or placeholder posture

Hard rule:

The page must make contradictions explicit instead of asking the reviewer to infer them.

### 4) Adjudication outcome selector

Supported `adjudication_outcome` values:

- `uphold-as-claimed`
- `uphold-but-weaken-language`
- `accept-narrower-scope-only`
- `overturn-claim`
- `split-verdict-by-subscope`
- `reopen-underlying-case`
- `insufficient-evidence-continue-hold`

Show for each outcome:

- strongest now-safe sentence
- surviving blocked stronger sentence
- required next actor
- whether rework or appeal opens automatically

Hard rule:

`uphold-as-claimed` is forbidden unless the prioritized witness set directly supports the challenged scope.

### 5) Rework routing strip

If any overturn or narrowing occurs, require:

- exact disproved portion
- assigned rework owner
- due / expiry posture
- whether prior acceptance is fully withdrawn or only narrowed
- whether downstream reliance packets must be recalled or weakened

Hard rule:

Rework may not live as a free-text suggestion.
It must become an explicit downstream object.

### 6) Safe-language footer

Render exactly one visible verdict sentence and one blocked sentence.

Example pattern:

- `Safe now: completion is upheld only for [narrow scope].`
- `Still blocked: completion is not yet safe to claim for [broader scope].`

## Required interactions

- **Promote witness family**
- **Downgrade stale witness**
- **Split verdict by sub-scope**
- **Withdraw prior acceptance**
- **Issue rework mandate**
- **Open appeal**

## Empty and failure states

If contradictory witnesses are all stale, show:

- `No decisive witness remains fresh enough to adjudicate this challenge.`

If only general health witnesses exist, show:

- `General activity witnesses exist, but none directly prove the challenged scope.`
