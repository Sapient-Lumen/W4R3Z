# Occupancy drift timeline page: materialization, Archive, rotation, and clear-storage events interface spec

## Purpose

Operators need a durable answer to:

> how did local footprint change over time, and which changes were working-byte materialization, hidden retention growth, or service-storage churn rather than ordinary content growth?

## Core decision

AnonSync must expose one **Occupancy drift timeline** whenever the storage story depends on mode changes, placeholder dematerialization, Archive retention, service-storage rotation, or explicit clear-storage actions.

## Timeline layout

1. **Timeline header**
2. **Occupancy event stream**
3. **Growth-cause legend**
4. **Current drift verdict**

### 1) Timeline header

Show:

- subject or storage-root ref
- review window
- strongest safe sentence
- blocked stronger sentence

### 2) Occupancy event stream

Supported events must include:

- `disconnected-visible-without-path`
- `connected-placeholder-spawn`
- `materialized-working-bytes`
- `placeholder-reversion`
- `archive-growth`
- `archive-prune`
- `service-storage-log-rotation`
- `profiler-growth`
- `temp-residue-cleared`
- `manual-clear-storage`
- `unknown-footprint-jump`

Each event row must preserve:

- timestamp
- occupancy class changed
- delta direction
- actor / automation cause
- whether visible size changed
- whether hidden bytes changed

### 3) Growth-cause legend

The page must classify growth cause as:

- `working-tree-growth`
- `materialization-without-new-content`
- `hidden-retention-growth`
- `service-storage-growth`
- `counted-scope-change`
- `telemetry-only-reading`
- `unknown`

### 4) Current drift verdict

Examples:

- `Visible working bytes are flat, but hidden Archive occupancy increased due to remote deletions and updates.`
- `Apparent cleanup reclaimed working bytes only; placeholder namespace and service storage remain.`
- `Reported size stayed flat because counted scope excluded the class that grew.`

## Hard rules

- materialization events must remain separate from content-authorship events
- hidden-retention growth must remain separate from visible working-tree growth
- counted-scope changes must remain separate from byte-occupancy changes
