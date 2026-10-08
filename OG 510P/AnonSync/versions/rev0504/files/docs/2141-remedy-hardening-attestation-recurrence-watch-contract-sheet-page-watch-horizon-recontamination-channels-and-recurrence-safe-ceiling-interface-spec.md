# Remedy-hardening-attestation recurrence-watch contract sheet page — watch horizon, recontamination channels, and recurrence-safe ceiling

## Purpose

This page is the operator-facing contract sheet for deciding whether a newly clean outsider state is likely to remain trustworthy across the named horizon.
It exists to stop `clean now` from being mistaken for `safe against known reopen channels later`.

## Core question

The page must answer:

**what is the strongest honest sentence we can make about recurrence-safe clean state across the named watch horizon, and what stronger sentence is still blocked?**

## Required fields

The contract sheet must capture at least:

- stale artifact identifier
- corrected replacement identifier
- outsider identifier or audience slice
- last confirmed clean-state boundary
- watch horizon class
- recontamination channel set
- detection posture class
- maximum expected detection lag
- automatic containment class
- manual re-review trigger set
- recurrence proof artifact set
- strongest honest recurrence-safe sentence
- blocked stronger recurrence-safe sentence

## Watch horizon classes

The sheet must preserve at least:

- no recurrence watch declared
- short handoff horizon
- session horizon
- business-day horizon
- governed review window
- indefinite watch not justified
- unknown horizon

## Recontamination channel set

The page must force explicit answers about whether the reviewed slice can still be reopened by:

- offline peer comeback precedence
- archive restore or version replay
- reconnect to a different local path
- delayed rescan or disabled notifications
- pause / scheduler windows that still allow partial effects
- read-only divergence and suspended updates
- conflict artifacts / naming collisions / filesystem incompatibilities
- residual forwarded or disconnected local copies

## Detection panel

The page must force explicit answers to:

- which channels are detected immediately and which are only detected on rescan, restart, history inspection, or manual review?
- what is the worst honest detection lag under the current watcher, rescan, and pause posture?
- does detection depend on live UI surfaces that disappear later or on portable artifacts that survive later?
- what surfaces can still show `healthy` while recurrence risk remains open?

## Hard rules

The page must never allow:

- `verified once` to silently stand in for `remains clean across the horizon`
- green status to silently stand in for recurrence-safe state
- recent history to silently stand in for durable recontamination watch
- `paused` to silently stand in for contained or quiet state
