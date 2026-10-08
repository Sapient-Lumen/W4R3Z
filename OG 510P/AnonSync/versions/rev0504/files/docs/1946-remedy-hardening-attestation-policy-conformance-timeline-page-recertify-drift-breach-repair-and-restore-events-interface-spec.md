# Remedy-hardening-attestation policy-conformance timeline page — recertify, drift, breach, repair, and restore events

## Purpose

This page is the ordered event view for current conformance claims after rollout.
It exists so later operators can see whether the case moved from deployment into fresh proof, overdue recertification, drift suspicion, breach, containment, repair, or restored conformance in the right order.

## Event classes

The timeline must support at least these events:

- rollout receipt adopted as current baseline
- fresh conformance witness captured
- recertification deadline scheduled
- recertification missed
- new population or object entered scope
- inheritance gap detected
- manual override detected
- service-world or principal-world split detected
- reconnect or path fork detected
- suspected drift opened
- breach confirmed
- containment activated
- repair started
- repair applied
- recertification after repair passed
- conformance restored
- policy narrowed, paused, or retired

## Required columns

- timestamp
- event class
- target estate slice
- source evidence reference
- resulting policy-conformance class
- stronger sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- rollout and present conformance into one event by default
- missed recertification into silent metadata change
- inheritance gaps into invisible background state
- suspected drift and confirmed breach into one event by default
- repair applied and conformance restored into one event by default
