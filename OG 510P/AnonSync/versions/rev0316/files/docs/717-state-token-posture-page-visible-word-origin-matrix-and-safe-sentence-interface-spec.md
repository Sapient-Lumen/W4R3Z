# State token posture page: visible word, origin, matrix, and safe sentence interface spec

## Purpose

Give one ordinary page that answers:

> what exact behavior does this visible state word mean here, what origin gave it that meaning, and what stronger sentence would be dishonest?

This page exists because labels like `Paused`, `Protected`, `Connected`, or `Read only` are often treated as self-explanatory even when their real contract depends on origin and exceptions.

## Core rule

Every durable visible state token must compile to a **state token posture**.
The posture must distinguish at least these things:

- visible token text
- origin that assigned the token
- effective signal matrix
- exceptions that remain alive despite the token
- strongest safe sentence
- stronger forbidden sentence

A UI may choose short labels, but it may not let the label outrun the actual matrix.

## Required sections

### 1) Visible token now

Show:

- current visible token
- current origin (`manual`, `scheduled`, `global`, `inherited`, `emergency`, `unknown`)
- whether the token has one stable meaning or several origin-specific meanings
- strongest safe sentence

Example sentences:

- `Paused here means inbound and outbound byte replay are blocked, but deletes still propagate.`
- `Paused here is scheduled and still permits outbound serving to non-paused peers.`
- `Connected here means reachable, not fully hydrated.`
- `Protected here hides Recents but does not turn external edits into live in-place edits.`

### 2) Effective matrix

Always render the matrix explicitly:

- outbound bytes
- inbound bytes
- delete propagation
- namespace/indexing
- discovery/watcher activity
- control-plane communication if materially distinct

Values should be one of:

- `allowed`
- `blocked`
- `limited`
- `reviewed only`
- `unknown`

### 3) Origin basis

Show the reasons this token means what it means here:

- manual toggle
- scheduled rule
- inherited parent/runtime state
- emergency/incident posture
- edition/runtime restriction
- platform or substrate exception

### 4) Exceptions and contradiction risk

Show what survives the state word unexpectedly:

- zero-sized objects still propagate
- deletions still propagate
- indexing still advances
- outbound serving still allowed
- local edits still accumulate
- token meaning differs across origins

### 5) Safe wording boundary

The product must show:

- strongest safe sentence
- stronger forbidden sentence
- why the stronger sentence is unsafe

Examples:

- safe: `Paused for inbound download work.`
- forbidden: `Fully frozen.`
- safe: `Paused, but delete propagation continues.`
- forbidden: `Nothing changes while paused.`

## Required actions

- `Inspect state-token evidence`
- `Review state-token change`
- `Split this token into qualified variants`
- `Keep current wording`

Never let the product reuse one visible token across different matrices unless the posture page makes the variance explicit.

## Data model

- `state_token_posture_id`
- `scope_kind`
- `scope_ref`
- `visible_token`
- `origin_kind`
- `signal_matrix`
- `exceptions[]`
- `stable_meaning` boolean
- `safe_sentence`
- `forbidden_sentence`
- `evidence_ref`
- `last_computed_at`

## Failure this page prevents

Without this page, operators trust the visible word more than the actual contract and only learn later that the same token meant different live lanes by origin.

AnonSync should instead keep token, origin, matrix, and wording boundary adjacent.
