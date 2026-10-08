# Third-party knowledge proof page — local-only fragment, relay blindness, and service-visible facts interface spec

## Purpose

This page exists to prove what a third party or infrastructure component can and cannot know for one concrete action instance.

It answers:

> for this exact link, carrier, route, and runtime moment, which facts stayed local, which were visible to infrastructure, which were only carried as ciphertext, and which stronger privacy sentence is still unproven?

## Core decision

Every serious privacy / disclosure claim should be backed by a first-class **Third-party knowledge proof** page.

That page owns witness-grade evidence, not just policy prose.

## Page layout

The page renders the same order:

1. target observer
2. action instance
3. visible facts
4. non-visible facts
5. proof basis
6. rejected overclaim
7. exportable receipt

### 1) Target observer

Show one observer class at a time:

- browser landing page service
- relay infrastructure
- tracker / discovery infrastructure
- telemetry recipient
- chosen peer
- local-only parse path

### 2) Action instance

Show:

- action ID
- artifact ID or route ID if relevant
- time window
- carrier actually used
- whether this is current live evidence or imported historical receipt

### 3) Visible facts

Show only facts supported by proof.
Examples:

- `tracker learned public and local IP addresses plus share-list participation`
- `telemetry recipient learned OS, version, active-state metrics`
- `browser handler saw browser-open request`
- `relay carried encrypted payload flow`

### 4) Non-visible facts

Show facts the system can positively exclude for that observer.
Examples:

- `relay could not read payload bytes`
- `server did not receive fragment parameters because they remained after #`
- `payload content was not included in telemetry`

### 5) Proof basis

Each fact row must cite one basis class:

- `artifact-shape proof`
- `protocol / route proof`
- `product-state proof`
- `operator-config proof`
- `imported documentation proof`
- `weak inference`

The operator must see whether a claim is witnessed, configured, or merely inferred.

### 6) Rejected overclaim

Every proof page must include one forbidden stronger sentence.
Examples:

- `reject saying “the service page learned nothing”`
- `reject saying “the relay learned nothing”`
- `reject saying “the browser never handled the artifact”`
- `reject saying “telemetry off means no infrastructure interaction anywhere”`

### 7) Exportable receipt

The export should preserve:

- target observer
- action instance
- visible fact set
- excluded fact set
- proof basis classes
- strongest safe sentence
- rejected stronger sentence
- expiration / stale-after condition

## Rules

### Rule 1 — proof pages speak observer-by-observer

Mixing all observers into one summary sentence hides the important edge cases.

### Rule 2 — `cannot learn` and `not proved to learn` stay separate

The page must distinguish exclusion from absence of evidence.

### Rule 3 — local fragment parsing deserves its own proof mode

When artifact facts stay local because they remain in the URL fragment or another local-only carrier, that is a different proof class than server-side non-retention promises.

## Result

AnonSync should turn privacy claims into auditable knowledge proofs.
If the operator still has to defend `who learned what` from memory of several FAQ pages, the page has failed.
