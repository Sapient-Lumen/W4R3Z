# Remedy-hardening-attestation regime-shift timeline page — upgrade, migrate, rebind, relocate, fork, and recertify events

## Purpose

This page is the ordered timeline for understanding how a durable state moved through named regime shifts.
It exists so later operators can see whether the state actually survived the transition, or whether the system passed through a fork, rebind, reconnect, or unsupported shortcut that changes the strongest honest sentence.

## Required event families

The timeline must be able to render at least these event families:

- pre-transition durable receipt issued
- upgrade prepared
- install style changed
- version-family changed
- service-account changed
- storage root relocated or auto-created
- config mode entered or exited
- control surface disabled, replaced, or overridden
- folder-class availability changed
- re-share or reconnect required
- unsupported clone or copied-instance event detected
- transition witness captured
- fork confirmed
- survival confirmed
- recertification after transition completed
- regime-robustness collapsed or narrowed

## Event cards

Every event card must preserve:

- event identifier
- event class
- timestamp
- affected governed slice
- prior class
- resulting class
- world-continuity effect
- storage or identity continuity effect
- control-surface effect
- manual step required
- resulting stronger sentence blocked or unlocked

## Fixed rendering order

Every regime-shift timeline must render the same sections in the same order:

1. **Pre-transition durable basis**
2. **Transition preparation and prerequisites**
3. **World fork or continuity events**
4. **Rebind, reconnect, or manual recovery events**
5. **Post-transition recertification and final sentence**

## Hard rules

- The timeline must never hide a world fork between two apparently calm surfaces.
- The timeline must never hide required re-share or reconnect work behind `migration`.
- The timeline must never treat unsupported clone events as normal migration steps.
- The timeline must never let post-transition calm erase the fact that the pre-transition sentence may have been interrupted or narrowed.
