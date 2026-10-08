# Remedy-convergence contract sheet page — required-cohort convergence, returner risk, and late-joiner quarantine

## Purpose

This page is the operator's compact contract for whether an authoritative cutover has actually converged across the cohorts that matter now and later.
It exists so the product can distinguish `the cure is currently authoritative` from `the cure has safely converged across present, returning, and newly admitted participants`.

## Core fields

- case identifier
- source remedy-cutover receipt identifier
- current remedy-convergence posture rung
- intended authoritative object identifier
- intended required present cohort
- intended required returning cohort
- intended possible late-joiner cohort
- connected full-sync convergence posture
- selective-sync placeholder cohort posture
- disconnected cohort posture
- pending or auto-connect cohort posture
- linked-device auto-availability posture
- offline-writer return-risk posture
- read-only suspended-divergence posture
- newcomer approval-memory posture
- future-joiner quarantine posture
- strongest blocked stronger cure sentence
- next strengthening trigger
- next weakening trigger

## Remedy-convergence posture rungs

The page must model at least these distinct rungs:

- cutover active pending convergence review
- connected full-sync convergence only
- named required present-cohort convergence
- convergence blocked by placeholder-only cohort
- convergence blocked by disconnected or pending cohort
- convergence blocked by offline-writer return risk
- convergence blocked by read-only suspended divergence
- returner-safe convergence
- future-joiner-safe convergence
- convergence collapsed by late arrival
- convergence verification collapsed

## Required distinctions

The page must keep these truths separate:

- authoritative cutover versus cohort convergence
- connected peers versus all required peers
- visible folder versus readable bytes present
- placeholder presence versus materialized convergence
- disconnected visibility versus admitted active participant
- approval memory versus explicit fresh admission into this convergence sentence
- returner-safe convergence versus future-joiner-safe convergence

## Operator promises

The contract sheet must let the operator say things like:

- `the cure is authoritative for all currently connected full-sync peers, but one required disconnected cohort keeps the stronger convergence sentence blocked`
- `all named present cohorts converged, but an offline writer can still return with higher precedence, so returner-safe convergence remains blocked`
- `linked devices automatically expose the folder more widely than the current reader cohort, so late-joiner quarantine remains open`
- `a previously approved pending peer can still auto-connect later, so the stronger future-joiner-safe sentence stays blocked`
- `placeholder-only visibility exists for one cohort, so convergence remains weaker than readable material adoption`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- offline writer return precedence
- pending or auto-connect participant still outside review
- disconnected cohort still outside byte adoption
- placeholder-only or selective-sync-only cohort
- read-only suspended local divergence
- linked-device auto-availability widening the possible cohort
