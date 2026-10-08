# Admission-instrument contract sheet page: key, link, QR, approval, and certificate basis interface spec

## Purpose

The archive already has pages for reachability provenance, detachment, cohort census, capability floor, and activity posture.
What it still lacked was one ordinary page for the narrower question:

> what access path exists here, what exact thing was sent, what join gate it implies, and what durable credential later resulted from it?

Current official Resilio docs make this seam concrete.
They separately describe automatic sharing through linked identity, manual sharing through key/link/QR, approval settings that differ by instrument, temporary-key link flow, certificate issuance after owner approval, and non-propagating key changes.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Admission-instrument contract sheet** whenever access to a subject depends on how a peer was admitted, what wrapper or credential was used, whether approval was required, or what durable grant was later minted.

The sheet exists to answer seven things in one place:

1. what admission basis is in play
2. what transport wrapper was observed
3. what durable credential class is in force
4. whether approval was required, skipped, reused, or not yet satisfied
5. whether the current join is only requested or already granted
6. what expiry or use-count limit applied to entry
7. what stronger access sentence remains blocked

## Fixed page order

1. **Admission header**
2. **Instrument and wrapper card**
3. **Approval gate card**
4. **Grant issuance card**
5. **Expiry / use-limit / rotation rail**
6. **Blocked stronger sentence**

### 1) Admission header

Show at minimum:

- `admission_contract_id`
- subject ref
- peer ref
- last admission witness time
- strongest safe sentence
- blocked stronger sentence
- current admission basis
- current durable credential class

Supported headline states must include:

- `identity-linked-auto-admission`
- `manual-key-admission`
- `manual-link-pending-approval`
- `manual-link-auto-approved`
- `qr-rendered-manual-admission`
- `granted-but-afterlife-limited`
- `unknown`

Example safe sentence:

- `This peer arrived through a manually shared link, approval was required, and durable access began only after certificate issuance.`

### 2) Instrument and wrapper card

Separate these truths explicitly:

- admission basis
- transport wrapper
- underlying credential payload
- grantable permission class
- minting authority
- reshare ceiling

Supported values must include at least:

- `linked-identity-automation`
- `manual-standard-key`
- `manual-read-only-key`
- `manual-link`
- `manual-link-rendered-as-qr`
- `unknown`

Hard rule:

- `QR` must never be treated as an authority class by itself; it is only a representation wrapper around another admission payload.

Each row must show:

- current value
- witness source
- freshness
- why it matters

### 3) Approval gate card

Separate these approval truths explicitly:

- `approval-not-applicable`
- `approval-bypassed-by-key`
- `approval-disabled-for-link`
- `approval-required-new-peer-only`
- `approval-required-for-all-peers-per-folder`
- `approval-request-pending`
- `approval-satisfied`
- `approval-status-unknown`

Each row must show:

- requirement class
- who can satisfy it
- whether prior approvals may be reused
- current pending/completed state
- blocked stronger sentence

The operator must be able to answer:

> is this peer already admitted, merely holding a token, or still waiting for a human gate?

### 4) Grant issuance card

This card must keep these moments separate:

- instrument received
- join request sent
- fingerprint observed
- owner approval granted
- certificate issued
- ACL entry signed / installed
- transfer eligibility reached

Supported durable credential classes must include:

- `none-yet`
- `session-request-only`
- `certificate-plus-acl`
- `legacy-keylineage`
- `unknown`

Hard rule:

- the product may never claim `access granted` from link click, key possession, or QR scan alone.

### 5) Expiry / use-limit / rotation rail

This rail must answer:

- did the instrument expire by time?
- did the instrument expire by use count?
- does expiry only block future joins?
- did a local key rotation happen?
- did rotation propagate or split the cohort into old and new lineages?

Supported states:

- `no-expiry`
- `time-limited-entry`
- `use-count-limited-entry`
- `entry-expired-existing-grant-unchanged`
- `local-key-rotated-lineage-split`
- `rotation-status-unknown`

### 6) Blocked stronger sentence

Examples:

- `This QR code itself grants access` blocked because QR is only a rendering form
- `This link click already joined the share` blocked because approval and certificate issuance were still pending
- `This expired invite removed existing access` blocked because expiry only governed new joins
- `Everyone moved to the new key` blocked because local key change does not auto-distribute

## Hard rules

- wrapper, admission gate, and durable credential must never be collapsed into one `shared` field
- automatic linked-identity arrival and manual invitation arrival must stay distinguishable
- `approved` is weaker than `certificate-and-acl-issued`
- `certificate-and-acl-issued` is weaker than `currently non-revoked`
