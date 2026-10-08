# Storage-accounting lineage receipt page: footprint basis, growth risks, and blocked stronger sentences interface spec

## Purpose

The archive repeatedly chooses receipts whenever a later operator may need to prove not just *what the storage number was*, but *what that number actually meant and what it excluded at the time*.
This receipt is the durable output for the storage-accounting family.

## Core decision

AnonSync must emit one **Storage-accounting lineage receipt** whenever a user-visible size claim, low-space warning, storage cleanup result, or remote storage-status sentence depends on counted scope, occupancy class, or hidden-growth basis.

## Receipt layout

1. **Receipt header**
2. **Counted-scope block**
3. **Occupancy basis block**
4. **Budget and drift block**
5. **Blocked stronger sentences block**

### 1) Receipt header

Show:

- `storage_accounting_receipt_id`
- subject ref
- issued-at time
- receipt freshness horizon
- strongest safe sentence
- blocked stronger sentence

### 2) Counted-scope block

Must preserve:

- visible size verdict
- counted subject scope
- ignored-subject treatment
- placeholder treatment
- Archive inclusion / exclusion
- service-storage inclusion / exclusion

### 3) Occupancy basis block

Must preserve:

- which occupancy classes were proven present
- which were only possible but unwitnessed
- what cleanup or dematerialization verbs changed which classes
- whether telemetry was local proof or remote-only reading

This block exists so future readers do not misread historical `uses X GB` or `freed space` language as stronger than what was actually witnessed.

### 4) Budget and drift block

Must preserve:

- watched budget basis
- threshold if known
- hidden-growth risks open at issue time
- retention or rotation policies relevant to storage drift
- whether the final sentence depended on visible working bytes only, full proven footprint, or partial telemetry

### 5) Blocked stronger sentences block

Each receipt must preserve at least one blocked stronger sentence, for example:

- `This number equals the total relevant local footprint.`
- `Cleanup removed every storage class associated with this share.`
- `The low-space stop watched all relevant bytes.`
- `No hidden growth risk remained.`

## Hard rules

- receipts may never serialize `size` without counted-scope meaning
- receipts must preserve both occupancy-class truth and budget-basis truth
- receipts must state whether the strongest sentence depended on local proof, hidden-growth review, or remote telemetry only
- receipts must remain readable without cross-referencing the full sheet
