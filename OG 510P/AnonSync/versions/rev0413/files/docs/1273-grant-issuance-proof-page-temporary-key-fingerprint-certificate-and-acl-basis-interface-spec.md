# Grant-issuance proof page: temporary key, fingerprint, certificate, and ACL basis interface spec

## Purpose

The admission sheet says what access basis is in play.
This page proves *when* access became durable and *why* that sentence is safe.

## Core decision

AnonSync must require a **Grant-issuance proof** whenever current access depends on several distinct moments that can be confused with each other: invitation receipt, request arrival, human approval, credential minting, and actual transfer eligibility.

## Proof layout

1. **Grant headline**
2. **Evidence stack**
3. **Phase verdict table**
4. **Runtime explanation sentence**
5. **Blocked stronger sentence**

### 1) Grant headline

Show:

- subject ref
- peer ref
- current grant verdict
- strongest safe sentence
- blocked stronger sentence
- proof freshness

Supported verdicts:

- `invitation-only`
- `request-pending-human-gate`
- `approved-not-yet-issued`
- `certificate-issued-acl-installed`
- `transfer-eligible`
- `grant-status-unknown`

### 2) Evidence stack

Supported evidence classes:

- `instrument-witness`
- `temporary-key-witness`
- `join-request-witness`
- `public-key-fingerprint-witness`
- `approval-action-witness`
- `certificate-issuance-witness`
- `acl-install-witness`
- `transfer-start-witness`
- `unknown-evidence`

Each item must show:

- source
- timestamp
- scope
- confidence
- which grant phase it governs

The operator must be able to answer:

> what exactly proves that access is durable, rather than merely attempted?

### 3) Phase verdict table

Each row must show:

- phase (`instrument delivered`, `request sent`, `identity reviewed`, `approval granted`, `credential issued`, `acl installed`, `transfer eligible`)
- current verdict
- governing evidence
- freshness
- uncertainty note

### 4) Runtime explanation sentence

This section must emit one exact sentence reusable across surfaces.
Examples:

- `The invite was opened, but access is still pending owner approval.`
- `Approval occurred, and durable access began only once the certificate and ACL entry were issued.`
- `This peer currently appears transfer-eligible, but the proof does not establish whether access remains non-revoked.`

### 5) Blocked stronger sentence

Examples:

- `The link itself granted access` blocked because the link only carried a temporary admission path
- `Approval alone completed the join` blocked because certificate issuance and ACL installation were not yet proven
- `This peer still has access now` blocked because the proof only covers issuance, not later revocation status

## Hard rules

- proof must always separate invitation transport from durable grant issuance
- approval UI evidence may not stand in for credential issuance evidence
- a durable grant must preserve both credential and ACL basis when available
- missing evidence must lower the sentence rather than be smoothed over
