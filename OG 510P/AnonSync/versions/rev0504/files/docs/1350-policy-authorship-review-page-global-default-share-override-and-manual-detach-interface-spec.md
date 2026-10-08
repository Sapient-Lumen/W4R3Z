# Policy-authorship review page — global default, share override, manual detach, and config takeover

## Purpose

This review answers one ordinary question before acceptance or troubleshooting:

> am I still using the global default, have I detached this subject into a private override, or has a colder governance plane already taken ownership away from the ordinary UI?

## Core decision

Whenever a value could be mistaken for inherited default when it is actually detached, pinned, or owned by another plane, the product must open one first-class **Policy-authorship review**.

## Fixed review order

1. request summary  
2. authorship comparison table  
3. inheritance warning  
4. plane takeover warning  
5. commit review  
6. receipt preview

### 1) Request summary

Show:

- value
- target scope
- requested change
- current claimed source of truth
- stronger simpler story the operator may be assuming

### 2) Authorship comparison table

Columns:

- `live inherited default`
- `manual subject override`
- `startup-config pinned`
- `service-world owned`
- `current value`

Rows:

- who can edit it
- who can witness it here
- whether future global changes will still flow through
- whether same-looking neutral value restores inheritance
- what restart or cutover boundary applies

The operator must be able to answer: **what kind of ownership am I accepting?**

### 3) Inheritance warning

If the subject is detached from the default, show:

- the event that severed inheritance
- what future global changes will no longer affect this subject
- what proof would be required to claim inheritance is truly restored

### 4) Plane takeover warning

If a colder or stronger plane owns the value, show:

- which plane took ownership
- what ordinary UI surface is now weaker than it looks
- whether the current surface can only witness or cannot even do that reliably

### 5) Commit review

Allowed buttons:

- `Keep live inheritance`
- `Detach into subject override`
- `Accept config / service ownership`
- `Stop and inspect winning plane`

### 6) Receipt preview

Preview the governance-plane receipt fields:

- winning plane
- losing planes
- inheritance status
- activation boundary
- blocked stronger sentence

## Review rules

- Never let `None`, blank, or neutral-looking values impersonate restored inheritance.
- Never let a colder startup or service plane hide behind an ordinary UI save.
- Never let `same displayed value` impersonate `same authorship lineage`.