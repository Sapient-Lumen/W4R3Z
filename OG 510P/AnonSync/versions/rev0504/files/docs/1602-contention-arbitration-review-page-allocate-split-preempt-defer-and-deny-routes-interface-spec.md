# Contention arbitration review page — allocate, split, preempt, defer, and deny routes

## Purpose

This page is where the operator decides what happens when contested room cannot satisfy every claimant as requested.
It must turn raw claimant competition into one explicit allocation verdict.

## Review question

> given the contested room, reserve rules, deadlines, claimant classes, and fairness obligations, what is the least-deceptive allocation verdict: allocate fully, split, preempt, defer, deny, or escalate?

## Inputs

- reservation contention contract sheet
- active capacity proof
- protected reserve policy
- promise authority and co-sign rules
- claimant expiry and starvation age
- existing published commitments affected by the verdict

## Allocation routes

### 1) Allocate fully

Use only when:

- claimant fits without reserve breach
- no stronger protected claimant is displaced
- fairness rules do not require a split or escalation

### 2) Split allocation

Use only when:

- claimants may honestly receive partial room
- the split itself remains legible and time-bounded
- blocked stronger sentences for every claimant remain explicit

### 3) Preempt

Use only when:

- a higher class claimant or emergency doctrine really outranks the loser
- preemption does not secretly breach protected reserve rules
- losing claimants receive explicit downgrade, expiry, or rescue route

### 4) Defer

Use only when:

- claimant can remain live without false hope
- next review time and holding basis are explicit
- starvation guard is armed

### 5) Deny

Use only when:

- room honestly does not exist or must remain protected
- denial basis is stronger than mere convenience
- the losing claimant's blocked stronger sentence is preserved

### 6) Escalate

Use when:

- claimant classes conflict beyond local authority
- reserve breach would have estate-level impact
- competing commitments require policy-level override or co-sign

## Required comparison blocks

- claimant rank and policy class
- starvation age comparison
- urgency versus reserve integrity
- preemption blast radius
- commitment damage if winner later fails
- recoverability for losing claimants

## Output object

The page must publish one typed verdict:

- `full-allocation`
- `split-allocation`
- `preemption`
- `defer`
- `deny`
- `escalate`

And for each claimant:

- winner/loser status
- scope granted
- scope denied
- next review or release trigger
- strongest sentence still blocked

## Clone-veto rule

If the page can only express `higher priority won` without naming reserve boundary, losing claimant consequence, and starvation treatment, it is still cloning Resilio's scattered priority-and-pause shape too closely.
