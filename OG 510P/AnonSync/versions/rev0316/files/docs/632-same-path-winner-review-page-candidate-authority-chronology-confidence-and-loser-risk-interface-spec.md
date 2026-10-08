# Same-path winner review page — candidate authority, chronology confidence, and loser risk interface spec

## Purpose

This page owns the next question after same-path divergence is found:

> if more than one candidate can occupy this exact path, which one is currently favored, why, how trustworthy is that ranking, and what risk does the loser face?

This page exists so `latest`, `newer`, `winner`, or `restored` never substitute for a real winner grammar.

## Core decision

Any same-path divergence that is not already blocked must create one first-class **Same-path winner review**.

The review is required whenever the product might otherwise rank candidates by timestamp, offline-return rule, or weak chronology hints without a typed explanation.

## Fixed review order

1. **Winner verdict strip**
2. **Candidate set**
3. **Winner basis**
4. **Chronology confidence**
5. **Loser risk and preservation**
6. **Admissible outcomes**
7. **Receipt promise**

### 1) Winner verdict strip

Show:

- reviewed path
- number of candidates
- current winner verdict
- strongest safe sentence

Example verdicts:

- `Strong-authority winner identified; loser preserved`
- `Guarded timestamp winner available; manual settlement still safer`
- `Offline-return winner would overwrite later online work`
- `Chronology not trustworthy enough; winner blocked`

### 2) Candidate set

For each candidate or reviewed bucket, show:

- candidate label
- current location/seat
- content summary
- authored time
- observed/returned time if relevant
- current live-path status
- strongest known lineage or authority clue

The operator should be able to answer: **what exact versions are competing for this path?**

### 3) Winner basis

Always show the exact basis currently favoring one candidate.

Allowed basis classes may include:

- `strong-authority-proof`
- `guarded-timestamp-order`
- `offline-return-rule`
- `manual-settlement`
- `blocked-no-honest-winner`

For the currently favored candidate, show:

- why it is ahead
- what weaker basis it relied on, if any
- what stronger proof is still missing

The product must not let `latest timestamp wins` hide as a silent default.

### 4) Chronology confidence

Show:

- chronology confidence (`high`, `guarded`, `low`, `blocked`)
- clock-window status
- timestamp-source status (`disk`, `database`, `mixed`, `unknown`)
- whether authored time, observed time, and return time agree or diverge
- whether ranking remains admissible under current chronology posture

The operator should be able to answer: **how much should I trust the current ranking?**

### 5) Loser risk and preservation

Show:

- losing candidate or losing bucket
- what happens if the current winner is applied
- preservation posture (`archive`, `branch`, `export`, `quarantine`, `none`)
- recoverability class (`easy`, `guarded`, `hard`, `unknown`)
- whether the loser still holds the easiest full-copy recovery path

The operator should be able to answer: **what exactly happens to the loser if I proceed?**

### 6) Admissible outcomes

Good actions include:

- `Apply reviewed winner`
- `Preserve loser, then apply winner`
- `Branch both versions`
- `Export loser before overwrite`
- `Block and escalate to manual settlement`

Poor actions include:

- `OK`
- `Use latest`
- `Restore`

when they hide winner basis and loser fate.

### 7) Receipt promise

The page must say which receipt will preserve:

- candidates reviewed
- winner basis
- chronology confidence
- loser fate
- stronger rejected sentence

## Public object

### `same_path_winner_review`

Fields:

- `same_path_winner_review_id`
- `subject_ref`
- `canonical_path`
- `candidates[]`
- `winner_basis`
- `favored_candidate_ref`
- `chronology_confidence`
- `timestamp_source_status`
- `loser_risk_posture`
- `preservation_options[]`
- `recommended_outcomes[]`
- `generated_at`

## Result

A good same-path winner review prevents five failures:

- `newer` standing in for a real winner basis
- offline-return dominance masquerading as ordinary chronology
- clock warnings living elsewhere while overwrite proceeds here
- loser preservation being rediscovered only after the live path changes
- later operators losing proof of why this winner was allowed at all
