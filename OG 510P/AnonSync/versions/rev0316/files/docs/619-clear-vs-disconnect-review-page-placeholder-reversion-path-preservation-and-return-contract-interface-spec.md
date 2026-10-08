# Clear-versus-disconnect review page — placeholder reversion, path preservation, and return-contract interface spec

## Purpose

Make local mode-adjacent actions a reviewed choice instead of a confusing cluster of similar verbs.
This page exists to answer:

> if I clear local bytes, remove this share from this device, or disconnect it, what exactly survives, what changes locally, and what will reconnect later require?

## Core decision

Any meaningful local-presence reduction that sounds like clear, local remove, or disconnect must render one first-class **Clear-versus-disconnect review** page.
That page is the semantic home of:

- local byte-preservation truth
- row / bind preservation truth
- path preservation truth
- reconnect return contract
- strongest safe sentence after action

## Primary page layout

The page always renders the same top-level regions in the same order:

1. action verdict strip
2. survives / stops matrix
3. path and reconnect card
4. safer alternative card
5. receipt / reopen card

### 1) Action verdict strip

Show:

- requested action (`clear-to-placeholders`, `remove-from-this-device`, `disconnect-share`, `remove-everywhere`, `unknown`)
- current share posture
- current byte posture
- strongest honest one-line summary

Allowed summaries:

- `Clear local bytes to placeholders; current path remains and future fetch stays possible`
- `Disconnect share from sync; filesystem folder remains but reconnect path must still be reviewed later`
- `Remove from this device; local participation ends while other peers remain authoritative`

### 2) Survives / stops matrix

Show rows for:

- local filesystem material
- local row visibility
- local bind/path memory
- peer-sync participation
- placeholder visibility
- future fetch path
- future linked-device default

For each row show before, after, and strongest safe sentence.

The operator must be able to answer:

> what exactly survives and what exactly stops?

### 3) Path and reconnect card

Show:

- current path basis
- whether the path survives as-is, survives only in history, or becomes pathless
- whether reconnect will propose the original path, a default path, or a path review
- duplicate-path risk such as `(1)` suffix fallback

The operator must be able to answer:

> what will reconnect later actually need to prove?

### 4) Safer alternative card

Show:

- nearest narrower alternative
- capability lost by choosing it
- whether the current path and row remain visible
- whether future fetch stays easier

Typical alternatives:

- `Keep placeholders instead of disconnecting`
- `Disconnect instead of remove-everywhere`
- `Leave future default unchanged`
- `Review path before reconnect`

### 5) Receipt / reopen card

Show:

- exact receipt class
- strongest safe sentence after action
- stronger forbidden sentence
- best reopen action (`Fetch`, `Reconnect`, `Review path`, `Change future default`, `Undo local clear`)

## Behavior rules

- This page must appear when the requested action can plausibly be mistaken for a different local-severance scope.
- The product must not pretend `Clear`, `Remove from this device`, and `Disconnect` are interchangeable.
- If reconnect may propose a different path or duplicate suffix, the page must say so before apply.
- A later stronger delete/remove-everywhere action must remain a separate review family.

## Compact row contract

A compact row should preserve this order:

1. requested action
2. bytes after action
3. bind/path after action
4. reconnect burden
5. safest alternative

Example:

```text
Disconnect    local files remain    path preserved as prior bind history    reconnect may need path confirmation    Keep placeholders
```

## Non-clone reason

Current official Resilio docs are candid that clear, local remove, disconnect, and reconnect do not mean the same thing.
They still do not give one stable page proving survival scope, path preservation, and return contract together.
AnonSync should.
