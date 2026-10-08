# Transport profile lineage receipt page: protocol, cipher, bind witness, and blocked stronger sentences interface spec

## Purpose

After any serious transport-profile change, a later operator must be able to answer:

> what transport lanes survived, what overlap was actually proven, what bind witness was observed, and what stronger claim was explicitly rejected?

This receipt exists so route and crypto posture do not dissolve into folklore.

## Core decision

Every serious transport-profile mutation emits one first-class **Transport profile lineage receipt**.

The receipt records:

- scope and time
- route classes before and after
- common protocol overlap verdict
- common cipher overlap verdict
- bind posture and current witness
- fallback residue
- strongest safe sentence
- stronger rejected sentence

## Fixed receipt sections

1. header
2. before / after summary
3. overlap evidence
4. bind evidence
5. blocked stronger sentence
6. reopen conditions

### 1) Header

Show:

- receipt id
- target scope
- operator / runtime label if known
- timestamp
- action class

### 2) Before / after summary

Show rows for:

- route class set
- protocol set
- cipher set
- bind posture
- proxy / relay dependence where material

### 3) Overlap evidence

Show:

- common protocol verdict
- common cipher verdict
- no-common-lane risk if any
- proof freshness

### 4) Bind evidence

Show:

- requested interface
- observed active interface
- fallback rule in force
- whether the final claim is preference-only or hard cutoff

### 5) Blocked stronger sentence

Examples:

- `Blocked stronger sentence: traffic is confined to the named interface.`
- `Blocked stronger sentence: only direct transport remains.`
- `Blocked stronger sentence: all peer traffic now shares the narrowed cipher set.`

### 6) Reopen conditions

Reopen automatically when:

- active interface changes
- common overlap becomes empty or unknown
- proxy posture changes
- relay becomes the surviving lane
- runtime restarts with different network state

## Rules

### Rule 1 — receipts must preserve overlap truth, not just requested settings

The receipt records what was actually still shared in common.

### Rule 2 — bind witness must record residue

A receipt without fallback posture is incomplete.

### Rule 3 — stronger blocked sentence is mandatory

The receipt must retain the claim that the product explicitly refused to make.
