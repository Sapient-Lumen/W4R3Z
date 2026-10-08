# Runtime stop proof page: visible state, service state, and platform background ceiling

This page exists so the product can prove what actually stopped instead of gesturing at a vanished window or a quiet status row.
It joins projection state, runtime state, service-manager state, and platform background ceiling into one proof page.

## Operator question

> Is this runtime actually stopped now, what independent evidence agrees or disagrees, and what background ceiling applies on this platform class?

## When this page must appear

Render whenever:

- the operator asks `is it really stopped?`
- a stop review completed but left ambiguity
- a runtime appears gone in one surface but present in another
- background-capable and foreground-only platform classes could be confused

## Fixed proof order

1. **Projection evidence now**
2. **Runtime / process evidence now**
3. **Service / boot manager evidence now**
4. **Platform background ceiling**
5. **Verdict and blocked stronger sentence**

## 1) Projection evidence now

Show:

- visible projection state: `open`, `hidden`, `closed`, `unknown`
- browser/webui state if relevant
- whether projection evidence is merely UI-local or independently corroborated

The operator must be able to answer: **what happened to the surface I can see?**

## 2) Runtime / process evidence now

Show:

- runtime presence: `observed-running`, `observed-not-running`, `ambiguous`, `unknown`
- observation source: process table, runtime heartbeat, IPC failure, explicit exit ack, service host, unknown
- freshness and confidence

The operator must be able to answer: **what happened to the actual runtime?**

## 3) Service / boot manager evidence now

Show:

- service manager state: `running`, `stopped`, `scheduled`, `not-applicable`, `unknown`
- startup registration state: `enabled`, `disabled`, `not-supported`, `unknown`
- whether a later reboot/login can recreate the runtime without another operator action

The operator must be able to answer: **what supervisor can still recreate this runtime later?**

## 4) Platform background ceiling

Show:

- platform ceiling: `background-capable`, `service-capable`, `foreground-only`, `priority-sensitive-background`, `unknown`
- whether hidden/runtime separation exists on this platform
- whether explicit `Exit` is required for a stronger stop claim
- whether background is unavailable and therefore projection disappearance has stronger meaning

The operator must be able to answer: **how strong can stop proof ever get on this platform?**

## 5) Verdict and blocked stronger sentence

Allowed verdicts:

- `projection closed only`
- `runtime appears stopped`
- `runtime stopped but future re-entry still armed`
- `service stopped now`
- `stable stop not yet proven`
- `unknown`

Also show:

- strongest blocked sentence
- exact missing proof that would unblock it

## Primary actions

- `Accept proof`
- `Open shutdown drain review`
- `Disable future startup`
- `Stop supervising service`
- `Re-open projection only`

## What this page must never imply

It must never imply that these are the same:

- projection closed and runtime stopped
- runtime stopped and no supervisor can relaunch it
- no background on iOS and no background limits on Android
- one evidence source and joined proof

## CLI projection expectation

A headless projection such as `anonsync runtime stop prove --subject <id>` must render the same proof sections and verdicts without requiring visual UI state.
