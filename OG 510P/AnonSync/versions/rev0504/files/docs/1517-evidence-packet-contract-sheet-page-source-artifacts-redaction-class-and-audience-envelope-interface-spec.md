# Evidence packet contract sheet page: source artifacts, redaction class, and audience envelope interface spec

## Purpose

After evidence has been captured, the operator still needs one page that answers:

> what exactly are we packaging, what form will it take, what has been removed or transformed, and who is this packet actually for?

## Core decision

AnonSync must expose one first-class **Evidence packet contract sheet** whenever captured facts or artifacts are prepared for handoff, review, support, appeal, or archival reliance.

## Fixed page order

1. **Packet header**
2. **Source-artifact card**
3. **Packet-form card**
4. **Redaction-and-transformation card**
5. **Audience-envelope card**
6. **Current packet decision card**
7. **Decision sentence**

### 1) Packet header

Show:

- packet sheet id
- source case id
- source capture proof ids
- packet owner
- current packet posture
- current strongest safe evidence sentence
- strongest blocked evidence sentence

Supported `packet_posture` values:

- `raw-packet-preferred`
- `derived-packet-acceptable`
- `redacted-packet-required`
- `summary-only-safe`
- `packet-not-yet-safe-to-share`
- `packet-ready-for-export`

Hard rule:

The page may not discuss export before naming packet posture first.

### 2) Source-artifact card

Required rows:

- source artifact ids
- source artifact classes
- source world or runtime lane
- capture times
- collector identity
- custody start point
- artifact freshness horizon

Supported `source_artifact_class` values:

- `ui-observation-set`
- `log-bundle`
- `single-log-excerpt`
- `history-export`
- `queue-or-peer-snapshot`
- `crash-report`
- `mini-dump`
- `core-dump`
- `narrative-note`
- `mixed-packet`

Hard rule:

Source world must stay visible.
A service-world log and a user-world log are not interchangeable provenance.

### 3) Packet-form card

Required rows:

- proposed packet form
- included artifacts
- omitted artifacts
- derived digests or summaries included
- audience-readable index included or not
- packet size or transport constraints

Supported `packet_form` values:

- `raw-archive`
- `raw-plus-index`
- `redacted-archive`
- `excerpt-bundle`
- `derived-digest`
- `narrative-summary`
- `hybrid-packet`

Hard rule:

The packet form must distinguish raw artifact carriage from explanatory layers.
A narrative summary may accompany a raw archive, but cannot silently replace it.

### 4) Redaction-and-transformation card

Required rows:

- redaction class
- transformation steps applied
- reason each step was applied
- diagnostic power weakened
- challenge or appeal power weakened
- reconstructability from retained raw source

Supported `redaction_class` values:

- `none`
- `identifier-redacted`
- `path-redacted`
- `time-redacted`
- `content-excerpted`
- `metadata-only`
- `summary-only`
- `mixed-redaction`

Hard rule:

Every redaction or transformation must publish what stronger evidence claim it prevents.
`privacy-safe` is not enough.

### 5) Audience-envelope card

Required rows:

- target audience class
- minimum sufficient share
- forbidden packet forms for this audience
- confidentiality boundary
- expected validation skill at destination
- recall path if packet is superseded

Supported `target_audience_class` values:

- `internal-operator`
- `peer-reviewer`
- `support-channel`
- `appeal-body`
- `external-stakeholder`
- `archival-record-only`

Hard rule:

Audience envelope and packet form must stay separate.
A raw packet may be valid for one audience and inappropriate for another.

### 6) Current packet decision card

Supported `current_packet_decision` values:

- `share-raw`
- `share-redacted`
- `share-hybrid`
- `share-summary-first`
- `withhold-until-reshaped`
- `retain-local-only`

Required rows:

- current packet decision
- chosen packet form
- chosen audience envelope
- why it beat alternatives
- strongest preserved claim
- strongest weakened claim
- rereview trigger

Hard rule:

The chosen packet must publish both what survives and what was sacrificed.

### 7) Decision sentence

Render one sentence only:

- `The current packet decision is [decision] as [packet form] for [audience], preserving [preserved claim] while weakening [weakened claim] because of [redaction/transformation basis].`

## Required interactions

- **Attach source artifact**
- **Change packet form**
- **Add or remove redaction step**
- **Switch audience envelope**
- **Withhold packet**

## Failure state

If no acceptable packet form exists, show:

- `No safe packet form currently satisfies this audience and confidentiality boundary. Retain locally or reshape the packet before export.`
