# Encrypted custody page: capability, restoreability, and promotion ladder interface spec

The archive already treats encrypted-only storage as a first-class posture rather than a weird folder subtype.
What it still lacked was one ordinary page that answers the operator question current products still make surprisingly hard:

> what can this ciphertext-only seat actually do, what can it never do, what recovery path remains honest here, and what stronger state could I upgrade toward if I need more than encrypted custody?

Current Resilio docs make this seam unusually concrete.
They openly document ciphertext-only storage on an untrusted machine, but also require the operator to remember key continuity, database continuity, read-only limits, overwrite posture, and special restore/decrypt paths.

## Page promise

The Encrypted custody page should make five answers adjacent:

1. custody role now
2. capability ceiling now
3. restoreability ladder now
4. current risks and blockers
5. strongest honest next action

The page may celebrate encrypted custody as useful.
It may not romanticize it into `safe backup` without naming what recovery still depends on.

## Fixed page order

Every encrypted-custody page should render the same sections in the same order:

1. **Seat role and custody class**
2. **Capabilities and hard ceilings**
3. **Restoreability ladder**
4. **Risk and degradation notes**
5. **Admissible actions**
6. **Receipt promise**

### 1) Seat role and custody class

This section should show:

- seat identity
- governed subject/share
- custody class (`ciphertext-only`, `plaintext-capable`, `mixed`, `unknown`)
- whether this seat is acting as intermediary seed, cold backup, temporary custody, or another reviewed role
- whether the current path is ordinary, detached, or degraded

The operator should be able to answer: **what kind of node is this, really?**

### 2) Capabilities and hard ceilings

This section should show at minimum:

- can store ciphertext
- can seed encrypted bytes
- can accept live plaintext opens locally or not
- can decrypt locally in ordinary product flow or not
- can write back authoritative plaintext changes or not
- can share onward, and in what form

Hard ceilings should be explicit, for example:

- `read-only encrypted seat`
- `cannot produce live plaintext from this page`
- `cannot restore deleted file back into live share from encrypted Archive alone`

The operator should be able to answer: **what can this seat honestly do, and what is permanently out of bounds?**

### 3) Restoreability ladder

This section is the heart of the page.
It should list recovery states in strength order, for example:

1. `plaintext-capable peer online now`
2. `saved RW/RO capability and database continuity preserved`
3. `local CLI/offline decrypt path available with required materials`
4. `ciphertext copies exist but current restore path is guarded`
5. `ciphertext present without sufficient recovery proof`

The page should show which rung is currently true and why.
It should also name the missing prerequisites for any stronger rung.

The operator should be able to answer: **if the source fails, what real recovery path still exists from here?**

### 4) Risk and degradation notes

This section should name the non-obvious caveats in product language rather than support-article prose, such as:

- saved keys missing
- database continuity broken
- overwrite posture may reassert deleted state
- encrypted Archive present but not live-share-restorable from this seat
- CPU or memory burden elevated
- current continuity only guarded, not proven

The operator should be able to answer: **what is the sharp edge here that optimism would otherwise hide?**

### 5) Admissible actions

Example actions:

- `Verify saved recovery materials`
- `Export recovery packet`
- `Promote to stronger custody review`
- `Prepare plaintext-capable restore on another seat`
- `Rotate encrypted custody`
- `Replace broken continuity with fresh encrypted node`

The page must not offer impossible verbs such as a plain `Open file` or `Restore here` when the seat lacks that capability.

The operator should be able to answer: **what is the strongest honest move available from this page?**

### 6) Receipt promise

A custody receipt should preserve:

- seat and subject
- custody class
- capability ceiling reviewed
- current restoreability rung
- missing prerequisites for stronger recovery
- chosen action or explicit abstention

The operator should be able to answer: **what later evidence will prove the team understood this node's real recovery ceiling?**

## Compact card contract

A trustworthy compact encrypted-custody card should preserve this order:

1. subject and seat
2. custody class
3. current restoreability rung
4. strongest blocker or missing prerequisite
5. next honest action

Example:

```text
Projects-Archive / vps-1   ciphertext-only seed   restoreability: guarded via saved RW+db continuity   blocker: no recent recovery-material attestation   Review
```

## What this page must never imply

The page must never imply that:

- ciphertext presence equals plaintext recovery
- encrypted seeding equals authoritative write capability
- encrypted Archive equals ordinary restore path
- saved key alone equals sufficient recovery proof if database continuity is gone
- `backup exists` equals `recovery has been operationally verified`

## Result

This page is how AnonSync borrows Resilio's excellent encrypted-intermediary idea without cloning the weaker habit of hiding recovery conditions inside support-style caveats.
