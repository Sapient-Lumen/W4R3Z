# Remedy-runway proof page — source presence, capacity reservation, and execution floor

## Purpose

This page is the durable proof object for why the product believed a remedy lane was or was not executable at a specific moment.
It exists so later readers can verify whether the product honestly distinguished preserved repair material from an actually runnable cure lane.

## Proof body

The proof must record:

- case identifier
- source hold-enforcement receipt identifier
- current remedy-runway posture rung
- required cohort identifier
- required response window
- proof timestamp and time-authority basis
- required source object count
- source-present count
- placeholder-only count
- source-missing count
- queue-depth snapshot
- priority class snapshot
- scheduler state snapshot
- free-space and temporary-space floor
- internal-task pressure summary
- discovery-lag floor
- strongest honest sentence
- strongest blocked stronger sentence
- exact blocker summary

## Acceptable proof inputs

The proof may draw from:

- explicit source-present attestations
- recent reachability evidence for required peers
- queue and priority state
- scheduler and pause state
- free-space and temporary-space checks
- watcher-health or rescan-risk signals
- execution receipts showing that cure work has actually started for named objects

## Forbidden compressions

The proof must not compress these into one verdict:

- preserved versus source-ready
- configured priority versus effective runway
- disk-above-threshold versus safe temporary write floor
- connected-now versus required-cohort ready
- warning absence versus low discovery-lag risk

## Stronger-sentence blockers

The proof must explicitly preserve blockers such as:

- one or more required sources offline
- placeholder-only state for required objects
- ghost-file suspicion
- queue or priority starvation
- scheduler closure or pause state
- disk headroom shortfall
- temporary-space amplification risk
- delayed discovery risk
- manual preparation debt
