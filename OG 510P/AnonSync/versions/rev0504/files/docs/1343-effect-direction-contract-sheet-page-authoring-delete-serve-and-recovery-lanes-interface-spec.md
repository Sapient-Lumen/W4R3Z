# Effect-direction contract sheet page — authoring, delete, serve, and reverse-recovery lanes

## Purpose

This page answers one ordinary question:

> on this seat, for this subject, which effects can actually travel outward, which can only be received, which can only be retained locally, and which recovery lane can ever run in reverse?

The page exists because materialization, visibility, and directional power are not interchangeable.

## Core decision

Every subject-seat pair must render one first-class **Effect-direction contract sheet**.
The page owns:

- local materialization class
- authoring direction
- delete direction
- serve eligibility
- onward-reshare direction
- reverse-recovery direction
- disconnect survivor behavior
- strongest safe sentence now

## Fixed page order

1. direction strip  
2. lane matrix  
3. delete-direction card  
4. recovery-direction card  
5. disconnect survivor card  
6. receipts

### 1) Direction strip

Show:

- subject
- seat
- local posture: `absent`, `placeholder`, `full-local-bytes`, `storage-only-copy`, `opaque-custody`, `unknown`
- authoring lane: `outbound`, `inbound-only`, `local-only`, `unknown`
- delete lane: `bidirectional`, `outbound-only`, `inbound-only`, `none`, `unknown`
- reverse-recovery lane: `ordinary`, `narrow`, `blocked`, `unknown`
- one honest next action

### 2) Lane matrix

Rows:

- edit existing local file
- add new local file
- rename local file
- delete local file
- serve bytes to peers
- re-share onward
- restore older bytes into live path

Columns:

- `can originate here?`
- `can publish outward?`
- `can be received from elsewhere?`
- `strongest safe sentence`
- `blocked stronger sentence`

The operator must be able to answer: **what can actually move outward from here, and what only arrives or stays?**

### 3) Delete-direction card

This card publishes:

- whether a local delete can ever remove remote bytes
- whether a remote delete can remove or overwrite local bytes
- whether delete follows source authority automatically
- whether already-landed copies survive local disconnect

The operator must be able to answer: **whose delete wins, and in which direction?**

### 4) Recovery-direction card

This card publishes:

- whether local recovery can republish back into the live subject
- whether recovery is ordinary, key-dependent, database-dependent, or blocked
- whether local Archive or local bytes can only help via a narrower side lane
- which stronger recovery sentence is forbidden

The operator must be able to answer: **can this side truly recover the world, or only save itself?**

### 5) Disconnect survivor card

Show:

- what survives after disconnect here
- whether disconnect stops only future arrival or also local bytes
- whether disconnect changes directionality or only continuity
- whether already-landed bytes become inert, collaborative, or still serve-eligible

### 6) Receipts

Link to:

- current effect-direction receipt
- most recent reverse-lane proof
- most recent delete-direction review

## Copy rules

- Never let `full copy` imply `can publish`.
- Never let `Read Only` stand alone without lane detail.
- Never let `backup` imply `reverse restore` without an explicit lane statement.
- Never let `encrypted copy exists` imply `ordinary recovery`.
