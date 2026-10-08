# Space-stop proof page: budget gate, default location, and actual occupancy interface spec

## Purpose

A storage warning is usually treated as if it proved a whole-device or whole-product space truth.
This page exists to stop that overclaim.

## Core decision

AnonSync must emit one **Space-stop proof** whenever low-space risk, sync stoppage, or capacity planning depends on a specific watched budget rather than the total footprint.

## Proof layout

1. **Budget header**
2. **Watched-basis block**
3. **Stop-behavior block**
4. **Occupancy mismatch block**
5. **Blocked stronger sentence**

### 1) Budget header

Show:

- `space_stop_proof_id`
- subject or storage-root ref
- witness time
- strongest safe sentence
- blocked stronger sentence

### 2) Watched-basis block

Must preserve:

- watched drive / storage root
- threshold or free-space floor
- whether the budget is tied to default folder location, explicit share location, storage folder, or unknown aggregate
- source of the threshold
- freshness and witness class

Supported verdicts:

- `default-location-budget-proven`
- `share-root-budget-proven`
- `service-storage-budget-proven`
- `budget-basis-partial`
- `budget-basis-unknown`

### 3) Stop-behavior block

Must preserve:

- what work pauses or stops
- what work may still continue
- whether the condition is warning-only or already active stoppage
- next recovery trigger
- whether manual cleanup or rematerialization choices can affect the watched budget

### 4) Occupancy mismatch block

Must preserve:

- visible-tree bytes at issue time
- hidden Archive / service-storage / temp residue relevance
- whether a large excluded class existed outside the watched basis
- whether remote telemetry was used instead of local proof

This block exists so later readers do not misread `out of space` as proving one total-footprint sentence.

### 5) Blocked stronger sentence

Examples:

- `The whole product is out of space.`
- `This visible folder size alone triggered the stop.`
- `Reverting files to placeholders resolves the warning completely.`
- `Archive and service storage are irrelevant to this budget.`

## Hard rules

- a space-stop proof may never serialize `out of space` without the watched budget basis
- visible-tree occupancy and watched budget basis must remain distinct
- recovery claims must say which occupancy class must shrink for the gate to clear
