# Reservation contention timeline page — claim collision, escalation, preemption, and release events

## Purpose

This page preserves the time-ordered life of a contested-room case so later operators can see whether a claimant won fairly, lost repeatedly, or was hidden by repeated quiet deferral.

## Event classes

- contest opened
- claimant added
- claimant withdrawn
- priority class changed
- reserve floor changed
- split proposed
- preemption proposed
- verdict published
- hold released
- hold expired
- claimant escalated
- starvation timer armed
- starvation timer breached
- contest reopened

## Timeline obligations

- show every claimant's first arrival time
- show each defer cycle instead of compressing them into one line
- show when a claimant lost because room was protected rather than because it lacked value
- show when emergency preemption overrode normal fairness rules
- show when a losing claimant later became winner after release or expiry

## Required comparison views

### By claimant

One lane per claimant showing:

- first claim
- every delay or deferral
- every partial allocation
- final outcome

### By room pool

One lane showing:

- free room changes
- reserve floor changes
- winning claimant switches
- preemption windows

## Interpretive guard

This timeline exists so that repeated deferral cannot masquerade as one harmless wait.
A claimant that keeps losing while never formally denied must still surface as accumulating starvation risk.
