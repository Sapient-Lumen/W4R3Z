# Retention horizon watch page — expiring history, mobile retention gaps, and export-before-loss

## Purpose

Warn before evidence silently decays.
This page answers:

> what proof is about to expire, what platform differences matter, and what should be exported or receipted now if I want to keep my strongest safe sentence?

## Layout

1. watch strip
2. expiring-families list
3. platform-retention differences card
4. consequence card
5. export ladder
6. horizon receipts

### 1) Watch strip

Show:

- scope label
- verdict: `stable`, `expiring-soon`, `already-weakened`, `mobile-gap-present`, `export-recommended`
- one next honest action

### 2) Expiring-families list

Each row shows:

- evidence family
- current horizon
- expected expiry time
- fact families that will be lost
- what weaker sentence would remain afterward

### 3) Platform-retention differences card

This card publishes differences such as:

- desktop history/event windows versus mobile-specific transfer or archive horizons
- archive-retention asymmetry across device classes
- surfaces that persist a UI row after local bytes are removed
- surfaces unavailable on certain platforms but still referenced elsewhere

### 4) Consequence card

Say explicitly:

- `If no export occurs, actor attribution will fall from complete to partial.`
- `Byte witness remains after history expiry.`
- `Transfer row remains, but subject-local byte presence will be gone.`
- `Only durable receipt will preserve the current strongest safe sentence.`

### 5) Export ladder

Actions:

- `Create durable receipt now`
- `Export bounded incident bundle`
- `Mark local note only — no durable proof uplift`
- `Let evidence expire and accept weaker future claims`

### 6) Horizon receipts

Receipts preserve:

- families nearing expiry
- export action taken or waived
- expected post-expiry sentence
- reminders suppressed or acknowledged

## Rules

- Any evidence family within its warning window must be surfaced proactively.
- Platform asymmetry must not be left to support trivia.
- `No action` is allowed, but only after the weaker future sentence is shown.
