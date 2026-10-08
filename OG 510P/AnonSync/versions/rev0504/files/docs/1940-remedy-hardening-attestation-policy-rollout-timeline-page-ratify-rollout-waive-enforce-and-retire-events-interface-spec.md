
# Remedy-hardening-attestation policy-rollout timeline page — ratify, rollout, waive, enforce, and retire events

## Purpose

This page is the ordered event view for rollout claims after precedent portability.
It exists so later operators can see whether the case moved from portable rule to named-slice deployment, waiver-bearing enforcement, narrowing, pause, expiry, or retirement in the right order.

## Event classes

The timeline must support at least these events:

- precedent ratified as rollout-eligible
- target estate slice defined or narrowed
- deployment wave approved
- deployment started
- verification sample captured
- named-slice enforcement achieved
- manual override detected
- waiver granted
- waiver expired
- grandfathered population sunset scheduled
- exception debt exceeded budget
- rollout paused
- rollout narrowed
- policy retired or superseded

## Required columns

- timestamp
- event class
- target estate slice
- source evidence reference
- resulting policy-rollout class
- stronger sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- portability approval and rollout completion into one event by default
- deployment start and effective enforcement into one event by default
- waiver expiry into silent metadata change
- drift detection into invisible background state
- retirement or supersession into an unlogged sentence change
