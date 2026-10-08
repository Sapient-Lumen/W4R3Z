# Remedy-hardening-attestation executable-mandate contract sheet page — bound parties, actuators, deadlines, and fallbacks

## Purpose

This page is the compact contract for deciding whether a verdict that is already legitimate has become a real mandate that binds named actors and can actually be executed through a known route.
It exists so the product can distinguish `legitimate verdict only`, `mandate issued`, `binding for named cohort only`, `actuator unavailable`, `execution pending`, `fallback governing`, `named-slice execution complete`, and `broader stronger sentence blocked`.

## Core fields

- executable-mandate identifier
- source verdict-legitimacy receipt identifier
- governing verdict sentence
- mandate issuer or authority identifier
- binding scope by actor class, estate slice, world, and topology
- obligated actor set identifier
- required action set identifier
- action deadline or execution window
- primary actuator class
- primary actuator identifier
- manual-step requirement flag
- restart or reconnect requirement flag
- fallback actuator class
- fallback trigger rule
- current executable-mandate class
- highest currently safe execution sentence
- strongest blocked stronger sentence
- next fact that upgrades executable standing now
- next fact that collapses executable standing now

## Executable-mandate classes

The page must model at least these distinct classes:

- legitimate verdict, advisory only
- mandate draft pending issuance
- mandate issued, binding scope ambiguous
- mandate issued for named cohort only
- mandate issued, primary actuator unavailable
- mandate issued, execution pending within deadline
- deadline missed, fallback required
- fallback route governing
- partially executed for named slice only
- execution complete for named slice
- broader stronger sentence blocked

## Actuator classes

The page must support at least these actuator classes:

- in-product automatic mutation
- per-subject manual operator action
- remove-and-recreate route
- disconnect-and-reconnect route
- restart-gated route
- configuration-at-startup route
- out-of-product human procedure

## Fixed rendering order

Every executable-mandate contract sheet must render the same sections in the same order:

1. **Highest currently execution-safe sentence**
2. **Binding scope, obligated actors, and deadline**
3. **Primary actuator, manual steps, and restart requirements**
4. **Fallback route, failure triggers, and current execution class**
5. **Next fact that upgrades or collapses executable standing**

## Hard rules

The contract sheet must never let an operator hide:

- a legitimate verdict behind an unstated `who is actually bound`
- an automatic-looking permission behind an unstated manual detour
- a chosen action behind an unstated restart, reconnect, or re-share requirement
- a partial slice completion behind `execution complete` wording
- a missing actuator behind `policy already landed` wording
