# Mutation-authority proof page — which surface can set, see, override, and verify this value

## Purpose

This page answers one ordinary question with evidence rather than assumption:

> which surface can actually change this value, which surface can only witness it, and which stronger control claim is still blocked?

## When this page appears

Show this proof page whenever the operator asks to confirm:

- whether the current surface can truly author the value
- whether a global or colder plane will override a local-looking save
- whether a mobile / WebUI / service / CLI surface can prove the active winner
- whether the current subject is still inheriting a default

## Proof ladder

Rank evidence from strongest to weakest:

1. explicit governance contract for this value class
2. reviewed winning-plane evidence on this subject
3. live witness from the active runtime surface
4. saved-but-cold evidence from config or service storage
5. operator memory or visual assumption

The page must never let a weaker rung outrank a stronger one.

## Fixed page order

1. authority verdict  
2. surface capability table  
3. shadowed-plane ledger  
4. blocked stronger claims  
5. strongest safe sentence  
6. reopening conditions

### 1) Authority verdict

Show separate verdicts for:

- can mutate here
- can witness here
- can override broader default here
- can restore inheritance here
- can prove active winner here

Each verdict must be one of:

- `proven allowed`
- `allowed only with colder-plane review`
- `blocked on this surface`
- `unknown`

### 2) Surface capability table

Rows:

- desktop per-subject UI
- desktop global UI
- advanced / power-user surface
- startup config
- service storage world
- launch switch / one-shot invocation
- mobile surface
- current surface

Columns:

- `can author`
- `can witness`
- `can override`
- `activation boundary`
- `missing proof`

### 3) Shadowed-plane ledger

List every shadowed or losing plane explicitly, for example:

- `global default present but detached by manual subject override`
- `desktop UI shows value but startup config pins folder set elsewhere`
- `service world owns storage and old desktop folders are outside current authority`

### 4) Blocked stronger claims

List each blocked stronger claim explicitly, for example:

- `shown on current screen` does not prove `editable here`
- `same neutral value` does not prove `inheritance restored`
- `saved in config` does not prove `already active runtime winner`

### 5) Strongest safe sentence

Show:

- strongest safe sentence now
- stronger blocked sentence

### 6) Reopening conditions

Show what future events would force rereview, such as:

- manual subject override
- service account or storage-world change
- config file takeover
- restart boundary crossing
- surface change to mobile / WebUI / service / desktop