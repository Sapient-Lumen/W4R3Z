# Remedy-hardening-attestation executable-mandate timeline page — order, route, attempt, deadline, failover, and execute events

## Purpose

This page is the ordered event view for execution questions after verdict legitimacy is established.
It exists so later operators can see whether the case moved from a legitimate sentence into a binding, routed, and executed mandate, or whether manual detours, missing actuators, missed deadlines, or fallback routes kept the stronger sentence blocked.

## Event classes

The timeline must support at least these events:

- verdict imported as mandate candidate
- mandate draft created
- mandate issued
- binding scope narrowed
- obligated actor set changed
- primary actuator selected
- primary actuator unavailable
- manual step requested
- restart required
- reconnect required
- replacement route required
- execution attempt started
- deadline warning raised
- deadline missed
- fallback route armed
- fallback route governing
- partial named-slice execution confirmed
- execution complete for named slice
- broader stronger sentence blocked
- mandate superseded or withdrawn

## Required columns

- timestamp
- event class
- source evidence or order reference
- resulting executable-mandate class
- stronger execution sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- legitimate verdict and mandate issuance into one event by default
- mandate issuance and execution start into one event by default
- execution start and execution completion into one event by default
- deadline miss and fallback activation into one event by default
- named-slice completion and broader completion into one event by default
