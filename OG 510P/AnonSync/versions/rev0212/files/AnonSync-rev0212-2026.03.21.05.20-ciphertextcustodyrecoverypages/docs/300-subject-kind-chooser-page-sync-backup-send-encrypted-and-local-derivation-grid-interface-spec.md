# Subject kind chooser page — sync, backup, send, encrypted, and local derivation grid interface spec

## Purpose

The archive already treats subject kinds as real semantics rather than cosmetics.
What it still lacked was one ordinary page for the moment where the operator chooses a new kind:

> what kind of thing am I creating here, what authority/retention/deletion contract comes with it, and why is one kind available while another is blocked?

This page exists so creation meaning does not leak through whichever `+` menu, share dialog, or platform-specific article happened to be used first.

## Core rule

Creation is a kind choice, not only a path choice.
The product must distinguish at least:

- collaborative sync subject
- backup/capture sink
- one-time send or transfer
- ciphertext-only custody subject
- same-host derivation subject

If the operator still has to infer retention, authority, and onward-share meaning from menu wording alone, the page is not explicit enough.

## Fixed review order

Every serious subject-kind chooser page should render the same sections in the same order:

1. **Chooser context**
2. **Kind comparison grid**
3. **Consequences of each kind**
4. **Seat/platform constraints**
5. **Chosen plan and receipt**

### 1) Chooser context

This section should answer:

- which seat, path, and current runtime profile are under review
- whether the operator is creating fresh, receiving/adopting, or deriving from an existing subject
- which subject kinds are currently admissible, inadmissible, or degraded here

The operator must be able to answer: **what creation decision am I actually making in this context?**

### 2) Kind comparison grid

This section should have stable rows for at least:

- `sync subject`
- `backup sink`
- `one-time send`
- `ciphertext-only custody`
- `same-host derivation`

Columns should include:

- primary purpose
- who can write back
- whether local deletion removes the source of truth
- whether onward share is allowed
- whether retention/history is expected
- whether bytes may remain ciphertext-only
- default lifecycle

The operator must be able to answer: **which kind matches the intent instead of merely the nearest button?**

### 3) Consequences of each kind

This section should show for the chosen or hovered row:

- authority consequences
- retention/deletion consequences
- materialization expectations
- restore and recovery expectations
- whether the subject is continuous, ephemeral, or custody-only

The operator must be able to answer: **what contract comes with this kind after I create it?**

### 4) Seat/platform constraints

This section should show:

- which kinds are unavailable on this seat or surface
- which kinds require stronger capability or reviewed posture
- storage-class, background, or shell limits that change the experience
- whether another seat or surface can complete the same plan more safely

The operator must be able to answer: **why is one kind greyed out here, and where can I do it honestly?**

### 5) Chosen plan and receipt

This section should show:

- the chosen kind
- path/subject target
- major contract consequences acknowledged
- any follow-up review required
- receipt after creation

The operator must be able to answer: **what exact kind did I choose, and what proof records that choice?**

## States

Use a small stable vocabulary:

- `sync subject`
- `backup sink`
- `one-time send`
- `ciphertext custody`
- `same-host derivation`
- `unsupported here`

## Main surface

A compact **Subject kind chooser** card should show:

- chosen or recommended kind
- strongest blocked alternative
- most important contract difference
- next review if the chosen kind is high-risk

## Key prohibitions

The product must not:

- let menu position or platform-specific habit substitute for kind explanation
- collapse `backup`, `sync`, and `send` into one generic `share`
- hide deletion/retention differences until after creation
- let a blocked kind appear merely absent without a visible reason and stronger alternative
