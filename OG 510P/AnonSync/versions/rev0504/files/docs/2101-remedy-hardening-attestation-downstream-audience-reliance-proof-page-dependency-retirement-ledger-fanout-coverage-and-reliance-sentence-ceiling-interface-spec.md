# Remedy-hardening-attestation downstream audience reliance proof page — dependency-retirement ledger, fan-out coverage, and reliance sentence ceiling

## Purpose

This page preserves the evidence needed to justify the strongest honest sentence about audience-wide stale-dependency retirement.
It is where the archive proves whether the correction retired stale dependence only for one beneficiary, for direct dependents, or for the full named audience boundary.

## Core sections

### 1. Audience claim rail

Show:

- governed audience identifier
- audience boundary rule
- dependency graph version
- intended coverage threshold
- current strongest honest reliance sentence

This rail must stay pinned while the operator scrolls.

### 2. Fan-out map

List direct, delegated, transitive, and local-only dependents separately.
Each node must preserve:

- node identifier
- dependency class
- stale-artifact class
- current retirement status (`retired`, `likely retired`, `still active`, `unknown`)
- evidence source
- sentence effect

### 3. Retirement ledger

Each retirement row must preserve:

- retirement identifier
- downstream node or artifact
- retirement carrier (`replacement published`, `cache expired`, `delegate repaired`, `export withdrawn`, `local derivative removed`, `other`)
- time retired
- proof source
- confidence class

### 4. Residual stale-dependency ledger

Each unresolved row must preserve:

- residue identifier
- downstream node or artifact
- why stale reliance remains possible
- last confirmed stale or unresolved time
- whether the node is direct or transitive
- whether it blocks the strongest audience-wide sentence

### 5. Sentence ceiling panel

This panel must always show:

- strongest honest sentence now
- next stronger sentence blocked
- exact blockers
- whether the blocker is boundary ambiguity, fan-out undercoverage, stale-artifact residue, or evidence decay

## Visualization rules

The proof page must include:

- a fan-out coverage bar split into direct, delegated, transitive, and local-only lanes
- distinct visual treatment for `positive retirement`, `inferred retirement`, `active stale`, and `unknown`
- an explicit count of unresolved stale nodes, not just percentage covered
- a marker whenever the page proves only named-audience retirement rather than broader public repair

## Interaction requirements

The page must support:

- filtering the graph by artifact class
- hovering over any uncovered node to see why coverage is still missing
- expanding a residue row into the exact evidence bundle behind it
- exporting a narrow proof package for one governed audience without flattening direct versus transitive coverage

## Hard rules

The page must never allow:

- one beneficiary receipt to satisfy an audience-wide proof need
- future-update revocation to erase already-landed stale copies
- inferred transitive coverage to be styled like direct proof
- a stronger sentence to render unless every unresolved residue has been named
