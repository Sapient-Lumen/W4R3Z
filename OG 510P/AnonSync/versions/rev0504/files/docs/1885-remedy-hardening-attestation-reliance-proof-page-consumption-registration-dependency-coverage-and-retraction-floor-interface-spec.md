# Remedy-hardening-attestation-reliance proof page — consumption registration, dependency coverage, and retraction floor

## Purpose

This page is the durable proof that downstream reliance was evaluated under explicit registration, consumption, coverage, and revocation rules.
It must let a later verifier see not only that a ruling was speakable, but who relied on it, which artifacts were derived from it, and what obligations were triggered when the source receipt changed.

## Sections

### 1) Dependency header

Publish:

- case identifier
- source finality receipt identifier
- current governing sentence
- allowed reliance audience class
- current dependency-governance class
- current revocation posture
- registry version identifier

### 2) Consumer registry summary

List at least:

- registered consumer count by class
- observed consumer count by class
- unregistered-but-eligible class count
- consumers frozen from further reliance
- consumers with unknown callback path

### 3) Observed consumption table

For each consumer or consumer class print:

- consumer identifier or cohort label
- evidence of consumption
- first observed consumption time
- last observed consumption time
- source receipt consumed
- downstream artifacts derived
- current stale flag
- current remediation status

### 4) Dependency coverage map

The proof must print explicit coverage results:

- named cohort fully covered or not
- required cohort fully covered or not
- external cohort unknown or bounded
- reasons coverage cannot yet be broadened
- oldest evidence that still supports current coverage claim

### 5) Revocation and revalidation table

For each active obligation print:

- obligation identifier
- trigger receipt change
- affected consumer or artifact
- action required
- owner
- deadline or horizon
- completion evidence
- current status

Example proof outputs:

- `allowed for named automation class; no observed consumption yet`
- `consumed by three registered automations; one exported packet still unverified`
- `superseded by successor receipt; revocation wave active for two stale dashboards and one downstream receipt`
- `historical-only source; all registered dependents revalidated or retracted`

### 6) Safe-speak sentence ladder

The proof must print the sentence ladder explicitly:

- current governing sentence
- strongest speakable dependency sentence
- strongest blocked broad-reliance sentence
- strongest blocked all-dependents-current sentence

### 7) Claim ceilings

The page must explicitly forbid false upgrades such as:

- `everyone who could rely did rely`
- `all dependents are current` when registry coverage is incomplete
- `superseded harmlessly` when stale derivative artifacts remain live
- `historical only` when retraction or revalidation work is still open
- `no one depended on this` when logs or callback paths are too incomplete to justify that claim

