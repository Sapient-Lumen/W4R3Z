# Dormancy timeline page — last-good witness, hide/expiry, and return-context interface spec

## Purpose

The archive already had duty-cycle timelines and posture-drift timelines.
What it still lacked was one timeline for the narrower question:

> what exactly happened between the last trustworthy sighting and the current return, and which events made the return weaker or stronger?

AnonSync should therefore expose a first-class **dormancy timeline page** whenever a seat, peer, or subject comes back after meaningful absence or stale uncertainty.

## Core decision

A stale return must be explainable as a short evidence ladder, not as remembered folklore.
The timeline must preserve five truths:

1. last good witness before dormancy
2. dormancy anchors and uncertainty band
3. hide / roster expiry / visibility change events
4. return and recovery events
5. current interpretation of the covered interval

## Fixed review order

1. **Last good witness**
2. **Dormancy interval**
3. **Visibility and roster changes**
4. **Return-context events**
5. **Current interpretation**

## 1) Last good witness

Show the last reviewed trustworthy state before dormancy:

- timestamp or range
- witness class
- what it proved
- what it did *not* prove beyond that point

## 2) Dormancy interval

Publish:

- first absent / uncertain anchor
- interval end or current return anchor
- uncertainty band width
- whether the seat was hidden, expired, stopped, asleep, foreground-only, clock-invalid, or unknown during this interval

## 3) Visibility and roster changes

Record events such as:

- hidden from roster
- reappeared in roster
- peer expired from list
- peer returned after expiry
- runtime stopped / resumed
- clock warning opened / cleared

Each event row must say whether it changed only visibility, only trust, or both.

## 4) Return-context events

Record relevant return-side anchors such as:

- app restart or reopen
- foreground resume
- next wake interval
- allowed network return
- source-peer return
- ghost-announcement detection
- manual clock repair

## 5) Current interpretation

The page must end with one explicit summary:

- `ordinary wake with short dormancy`
- `long-offline return with guarded chronology`
- `hidden roster reappearance`
- `aged-out peer returned`
- `clock-invalid interval blocks normalization`
- `announcement survives but source reality is broken`
- `mixed / unresolved`

## Public object

### Dormancy timeline page

Fields:

- `dormancy_timeline_page_id`
- `scope_ref`
- `last_good_witness_ref`
- `dormancy_interval`
- `visibility_change_rows[]`
- `return_context_rows[]`
- `current_interpretation`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. last good witness
3. dormancy interval label
4. strongest return event
5. current interpretation

Example:

```text
Laptop seat     trusted at 10:14 yesterday     dormant ~17h     reappeared after hide + restart     long-offline return with guarded chronology
```

## Non-goals

This page does **not** decide the final safe action by itself.
It preserves the dormancy story so later review stops flattening all returns into `came back online`.
