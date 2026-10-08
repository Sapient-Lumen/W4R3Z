# Storage-accounting contract sheet page: visible size, placeholder weight, and hidden growth interface spec

## Purpose

The archive already has pages for presence, redundancy floor, control substrate, and activity posture.
What it still lacked was one ordinary page for the narrower question:

> what here occupies bytes, what only occupies namespace, what is included in the visible size claim, what hidden stores can drift upward, and what stronger storage sentence remains blocked?

Current official Resilio docs make this seam concrete.
They separately describe disconnected folders with no path or local space, placeholder-only Selective Sync subjects, ignored files excluded from `Size`, hidden `.sync/Archive` growth, storage-folder debug/profiler residue, and low-space warnings tied to the default folder location.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Storage-accounting contract sheet** whenever an operator is shown a size claim, storage warning, cleanup result, or residency mode that changes which bytes really occupy local media.

The sheet exists to answer seven things in one place:

1. what occupancy classes exist right now
2. what counted-scope produced the visible size number
3. what hidden growth channels exist
4. what budget gate is armed
5. what remote storage telemetry exists
6. what cleanup or dematerialization actions changed only one occupancy class
7. what stronger storage sentence remains blocked

## Fixed page order

1. **Storage-accounting header**
2. **Visible-size card**
3. **Occupancy-class matrix**
4. **Budget-gate card**
5. **Hidden-growth and cleanup rail**
6. **Blocked stronger sentence**

### 1) Storage-accounting header

Show at minimum:

- `storage_accounting_contract_id`
- subject ref or cohort ref
- actor / seat ref
- last footprint witness time
- strongest safe sentence
- blocked stronger sentence
- current visible size verdict
- current budget gate verdict

Supported headline states must include:

- `namespace-only-visible`
- `placeholder-weight-only`
- `working-bytes-present`
- `hidden-growth-open`
- `counted-scope-narrower-than-namespace`
- `budget-gate-armed`
- `unknown`

Example safe sentence:

- `This share currently exposes full namespace visibility, but the reported size excludes ignored subjects and does not include hidden Archive or storage-folder growth.`

### 2) Visible-size card

Separate these truths explicitly:

- counted size basis
- counted subject scope
- placeholder treatment
- ignored-subject treatment
- hidden-store exclusion status
- witness freshness
- blocked stronger sentence

Supported values must include at least:

- `indexed-sync-subjects-only`
- `working-bytes-materialized-only`
- `placeholders-excluded-from-byte-weight`
- `ignored-subjects-excluded`
- `archive-excluded`
- `service-storage-excluded`
- `counted-scope-unknown`

Hard rule:

- `Size` must never be shown as a flat byte truth unless counted scope and exclusion basis are explicit.

Each row must show:

- current value
- witness source
- freshness
- why it matters

### 3) Occupancy-class matrix

Separate these occupancy classes explicitly:

- disconnected visible subject only
- placeholder namespace entry
- materialized working bytes
- hidden Archive bytes
- hidden service-storage bytes
- temporary transfer residue
- ignored local-only bytes
- remote storage telemetry only

Each row must show:

- byte presence class (`none`, `minimal`, `full`, `hidden`, `remote-only`, `unknown`)
- counted-in-visible-size yes/no/unknown
- cleanup verb if any
- future-growth class
- strongest safe claim supported by that class

### 4) Budget-gate card

Separate these budget truths explicitly:

- watched drive or storage root
- threshold basis
- stop behavior
- whether gate applies to visible tree, default folder drive, storage folder, or unknown aggregate
- whether gate was merely warned or has already suspended sync-moving work
- blocked stronger sentence

Supported values:

- `default-location-drive-threshold`
- `share-local-budget-reviewed`
- `service-storage-budget-reviewed`
- `low-space-warning-open`
- `sync-stop-risk-open`
- `budget-basis-unknown`

The operator must be able to answer:

> which budget is actually being watched, and what class of work will stop first if this threshold is crossed?

### 5) Hidden-growth and cleanup rail

This rail must answer:

- what hidden reservoirs can still grow?
- what retention or TTL policy governs them?
- what cleanup removed only placeholders versus real bytes?
- what cleanup touched Archive or service storage?
- what remote-storage reading exists and what it excludes?

Supported states:

- `archive-growth-open`
- `archive-ttl-bounded`
- `archive-growth-unbounded`
- `service-storage-growth-open`
- `placeholder-reversion-only`
- `working-bytes-reclaimed`
- `remote-telemetry-partial`
- `unknown`

### 6) Blocked stronger sentence

Examples:

- `This size number equals all bytes relevant to this share.` blocked because ignored subjects or hidden stores were excluded
- `No local space is being used.` blocked because Archive, service storage, or temp residue may still exist
- `Removing from this device reclaimed all relevant space.` blocked because only working bytes changed while placeholders or Archive survived
- `Low-space protection covers the whole footprint.` blocked because only one drive or one budget basis was proven

## Hard rules

- visible namespace, placeholder weight, working bytes, Archive bytes, and service-storage bytes must never be collapsed into one `uses space` sentence
- counted-scope and exclusion basis must remain visible whenever a size number is shown
- cleanup results must state which occupancy classes changed and which remained
- remote storage telemetry must never be displayed as full local-footprint truth without explicit limits
