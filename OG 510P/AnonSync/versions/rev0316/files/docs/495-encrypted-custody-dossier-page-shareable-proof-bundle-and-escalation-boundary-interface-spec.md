# Encrypted custody dossier page: shareable proof bundle and escalation boundary interface spec

## Purpose

Encrypted custody often becomes important only during handoff, audit, or incident response.
At that moment the operator needs one exportable object that says what is true without leaking what should stay private.

This page exists to answer one ordinary operator question:

> what exact reviewed facts about this encrypted-custody setup can I safely hand to another operator, successor, or support lane without oversharing secrets or forcing them to rediscover the whole setup from scattered receipts?

## Core decision

Every encrypted-custody family must expose one first-class **Encrypted custody dossier** page.
That page is the semantic home of:

- current reviewed facts
- shareability boundary
- redaction classes
- proof-bundle generation
- escalation receipts

The product must not force operators to improvise screenshots, chat summaries, or secret-bearing notes during a stressful handoff.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. dossier scope and current summary
2. reviewed-facts bundle
3. redaction and secrecy boundary
4. recipient / escalation lane preview
5. generated bundle receipts
6. expert evidence drawer

### 1) Dossier scope and current summary

Show:

- subject family and custody seat in scope
- current custody verdict
- current recoverability posture
- strongest current risk
- bundle freshness

The operator must be able to answer: **what setup am I packaging and how current is this summary?**

### 2) Reviewed-facts bundle

The shareable bundle should preserve these fact classes:

- lane classification used at creation
- destination seat posture at commit
- target-admission verdict
- capability ceiling
- current recoverability posture
- continuity verdict
- latest rehearsal posture
- strongest outstanding blocker
- links to underlying receipts inside the product

The bundle must preserve structured facts, not raw internal files.

### 3) Redaction and secrecy boundary

Show explicit classes:

- `safe to share broadly`
- `share with trusted operator only`
- `never include automatically`
- `requires explicit reveal workflow`

Examples:

- safe: verdicts, postures, timestamps, receipt ids
- guarded: host/path hints, operator names, storage-governance hints
- never auto-share: RW/RO secrets, raw database paths when unnecessary, raw decrypt commands containing secret material

The operator must be able to answer: **what can I safely export without compromising recovery materials or privacy posture?**

### 4) Recipient / escalation lane preview

Before export, show the intended lane:

- `same-team operator handoff`
- `successor owner handoff`
- `support / vendor escalation`
- `incident packet`
- `local archive only`

For each lane show:

- minimum fact classes needed
- extra redactions applied
- whether live product links remain accessible to the recipient
- whether the bundle is advisory, evidentiary, or action-driving

The operator must be able to answer: **who is this bundle for, and what is the narrowest sufficient packet?**

### 5) Generated bundle receipts

Every generated dossier receipt must preserve:

- scope
- recipient lane
- fact classes included
- redactions applied
- freshness at generation time
- actor and timestamp
- resulting artifact identifier or local ledger pointer

This lets later reviewers answer: **what exactly left the page, and under what disclosure policy?**

### 6) Expert evidence drawer

The drawer may expose:

- linked receipts
- structured evidence graph
- continuity / rehearsal provenance
- unresolved contradictions
- optional manual notes

These details matter, but they should not pollute the ordinary export preview.

## Acceptance criteria

This spec is satisfied when:

- encrypted-custody handoff no longer depends on ad hoc screenshots or secret-bearing notes
- export lanes preserve reviewed facts without flattening them into vague prose
- secret-bearing materials stay outside the default bundle
- later recipients can distinguish `this setup exists`, `this setup was reviewed`, and `this setup was actually rehearsed`
