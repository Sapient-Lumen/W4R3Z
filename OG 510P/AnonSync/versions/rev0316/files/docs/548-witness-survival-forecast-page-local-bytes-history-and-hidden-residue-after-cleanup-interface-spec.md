# Witness survival forecast page: local bytes, history, and hidden residue after cleanup interface spec

## Purpose

This page answers:

> after the cleanup I am considering, which witness classes will still survive, where will they survive, and which surfaces will still be able to reach them?

The page exists because `cleanup succeeded` does not answer whether rollback, audit, or simple later explanation also survived.

## Core rule

Every cleanup review stronger than a trivial temp-file trim must render one first-class **Witness survival forecast**.
That forecast owns:

- local byte survival
- placeholder / namespace survival
- event/history survival
- hidden archive / service-state survival
- surviving host classes and reachability
- strongest safe sentence after apply

## Primary layout

The page always renders the same regions:

1. current-versus-after strip
2. survival matrix
3. reachability-after card
4. preservation gap card
5. safe post-cleanup sentence
6. receipt linkage

### 1) Current-versus-after strip

Show:

- current witness count by class
- forecast surviving witness count by class
- largest forecast weakening
- earliest future cliff after cleanup

### 2) Survival matrix

Each row should cover one witness family:

- local materialized bytes
- placeholders / names-only visibility
- prior-version archive bytes
- event/history witness
- service/log/config roots
- external peer-only witness
- manual export or pinned copy

For each row show:

- current host
- current reachability
- post-cleanup host
- post-cleanup reachability
- survival verdict (`survives`, `survives-weaker`, `moved`, `removed`, `unknown`)
- note explaining why

### 3) Reachability-after card

Show:

- whether the acting surface will still be able to inspect the witness
- whether only another seat / surface will retain practical access
- whether the witness survives only as hidden residue
- whether app removal or detach changes practical reach more than byte existence

### 4) Preservation gap card

Show any gap between survival and usefulness:

- `bytes survive but not on this surface`
- `event witness survives but byte witness does not`
- `hidden archive survives but ordinary operator path disappears`
- `local path survives but app/event ledger does not`
- `only external peer witness remains`

### 5) Safe post-cleanup sentence

Always render three lines:

- strongest approved sentence
- weaker fallback sentence if the best surviving witness becomes unreachable
- stronger forbidden sentence

### 6) Receipt linkage

Show which cleanup receipt and which existing recovery-horizon receipt the forecast depends on or will supersede.

## Rules

### Rule 1 — survival and reach must stay separate

A witness can survive in bytes while becoming unreachable from the current surface.
The page must show both facts.

### Rule 2 — hidden residue must not masquerade as easy recovery

If the only surviving witness is hidden control storage, say so directly.

### Rule 3 — forecast must name the weakest surviving proof floor

After cleanup, the page must say what minimum proof still supports later claims.

## Event language

Use phrases such as:

- `archive witness survives only as hidden local residue`
- `history witness is preserved, but local rollback bytes are not`
- `local placeholders remain; full-copy witness moves to remote desktop only`
- `cleanup preserves no credible recovery witness on this seat`

Avoid phrases such as:

- `you can always restore later`
- `cleanup does not affect sync history`
- `everything important remains`
