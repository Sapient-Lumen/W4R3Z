# Remedy-hardening-attestation successor beneficiary-notice contract sheet page — correction notice carrier, acknowledgement requirement, and uptake ceiling

## Purpose

This page is the operator-facing sheet for deciding whether a later canonical correction did more than merely exist or sync.
It exists to stop `correction published`, `files arrived`, `bell lit`, or `history updated` from being mistaken for `the named beneficiary noticed and acknowledged the correction`.

## Core question

The page must answer:

**for this named beneficiary and later canonical correction, what is the strongest honest sentence about delivery, notice, acknowledgement, and uptake now?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source beneficiary-authority receipt identifier
- named beneficiary identifier
- governed slice identifier
- canonical correction identifier
- correction class (`fix`, `supersession`, `withdrawal`, `warning`, `revoke`, `scope-change`)
- notice policy class
- required acknowledgement class
- allowed carrier set
- observed carrier used
- carrier health class
- surfaced-to-device state
- beneficiary-seen state
- beneficiary-acknowledged state
- reminder / escalation posture
- expiry or acknowledgement deadline
- strongest honest notice sentence now
- blocked stronger uptake sentence now

## Standing ladder

The page must support at least these distinct standings:

- correction published, beneficiary notice still unproven
- correction delivered to lane, surfaced-to-device still unproven
- surfaced in UI or queue, human-seen state unproven
- beneficiary seen, acknowledgement still unproven
- acknowledgement required and completed
- acknowledgement optional and absent
- reminder due, acknowledgement overdue
- notice or acknowledgement evidence expired below proof floor
- receipt superseded

## Required comparisons

The sheet must compare:

- correction publication versus beneficiary notice standing
- device-surface evidence versus human-seen evidence
- human-seen evidence versus acknowledgement evidence
- required acknowledgement policy versus current acknowledgement state
- intended carrier set versus actual carrier used
- nominal carrier health versus degraded discovery or surfacing posture
- desired uptake sentence versus currently blocked stronger sentence

## Required layout

### Header

Show:

- correction name
- beneficiary name
- notice posture
- acknowledgement posture
- strongest honest sentence now

### Left column — intended notice contract

Show:

- governed slice
- correction class
- notice policy
- acknowledgement requirement
- allowed carriers
- reminder ladder
- forbidden substitute states

### Center column — observed notice facts

Show:

- correction publish time
- delivery path actually used
- carrier health state
- surfaced-to-device evidence
- seen evidence
- acknowledgement evidence
- reminder / expiry events

Every row in this column must have:

- current value
- evidence source
- whether it strengthens or weakens the notice sentence

### Right column — consequence for beneficiary truth

Show:

- whether the correction merely exists, merely synced, merely surfaced, was seen, or was acknowledged
- whether acknowledgement is required, optional, missing, overdue, or completed
- whether the beneficiary-facing correction sentence is current, stale, degraded, or still blocked
- what stronger sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- correction exists, notice unproven
- correction synced, seen unproven
- surfaced-to-device, human-seen unproven
- seen, acknowledgement pending
- acknowledged under policy
- stronger uptake sentence still blocked

## Interaction requirements

The interface must support:

- clicking any notice chip to open a drawer showing `published / delivered / surfaced / seen / acknowledged / overdue / expired`
- clicking any carrier badge to reveal whether the path was event-driven, rescan-backed, manual-open dependent, or otherwise degraded
- clicking the blocked-sentence rail to reveal the minimum missing proof needed to upgrade from `surfaced` to `seen`, or from `seen` to `acknowledged`
- pinning one beneficiary while comparing several later corrections so the acknowledgement ladder stays stable across the list

## Hard rules

The page must never allow:

- `files synced` to silently become `beneficiary noticed`
- `notification could appear` to silently become `notification was seen`
- `history shows activity` to silently become `beneficiary acknowledged the correction`
- `debug log recorded the event` to silently become `human uptake proved`
