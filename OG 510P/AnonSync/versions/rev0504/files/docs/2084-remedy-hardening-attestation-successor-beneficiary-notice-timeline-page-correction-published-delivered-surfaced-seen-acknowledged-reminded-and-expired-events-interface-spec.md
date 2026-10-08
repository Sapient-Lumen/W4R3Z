# Remedy-hardening-attestation successor beneficiary-notice timeline page — correction published, delivered, surfaced, seen, acknowledged, reminded, and expired events

## Purpose

This page records the life of one beneficiary-facing correction from publication through delivery, surfacing, likely observation, explicit acknowledgement, reminder, expiry, or supersession.
It exists so the product can tell not just whether a correction exists, but how far it actually traveled into beneficiary awareness.

## Required event families

The timeline must support at least these events:

- correction published
- correction severity raised or lowered
- carrier selected
- carrier degraded
- correction delivered to beneficiary lane
- correction surfaced in beneficiary environment
- beneficiary opened related view
- beneficiary viewed correction detail
- beneficiary dismissed surface without acknowledgement
- acknowledgement requested
- acknowledgement completed
- reminder sent
- acknowledgement overdue
- notice evidence expired
- correction superseded
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- touched beneficiary / correction / slice identifier
- before state
- after state
- whether notice confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- correction published
- first beneficiary-surface event
- first likely-seen event
- acknowledgement completion or overdue event
- current strongest sentence

### Full audit view

Show:

- every carrier selection and degradation event
- every surface, open, view, dismissal, and acknowledgement event
- every reminder, expiry, supersession, and sentence-upgrade or downgrade event

## Mandatory badges

The timeline must surface badges for:

- correction published
- surfaced only
- seen likely
- acknowledgement required
- acknowledgement complete
- acknowledgement overdue
- notice degraded
- evidence expired
- uptake sentence blocked
- receipt superseded

## Hard rules

The timeline must never allow:

- `correction exists` to silently become `beneficiary informed`
- `delivered to lane` to silently become `beneficiary saw it`
- `view opened` to silently become `acknowledgement completed`
- `reminder sent` to silently become `notice succeeded`
