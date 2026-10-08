# Remedy-hardening-attestation affected-party-closure timeline page — notice, delivery, acknowledge, contest, accept, lapse, and reopen events

## Purpose

This page is the ordered event view for the closure phase after remediation.
It exists so later operators can see whether the case moved from notice obligation to delivery, acknowledgement, acceptance, uncontested lapse, contest, or reopen in the right order.

## Event classes

The timeline must support at least these events:

- materially affected cohort defined
- notice obligation added or narrowed
- notice issued
- delivery proven
- delivery failed or bounced
- acknowledgement received
- acknowledgement refused
- contest opened
- acceptance recorded
- objection window opened
- objection window paused
- objection window lapsed
- closure sentence issued
- closure sentence downgraded
- closure reopened

## Required columns

- timestamp
- event class
- affected cohort or party
- source evidence reference
- resulting closure class
- stronger sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- issue and delivery into one event by default
- acknowledgement and acceptance into one event by default
- silence and objection-window lapse into one event without policy basis
- prior closure and later reopen into a single continuous good state
